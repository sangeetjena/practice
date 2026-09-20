package example.platform;

import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.streaming.api.operators.co.KeyedCoProcessOperator;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.runtime.streamrecord.StreamRecord;
import org.apache.flink.streaming.util.KeyedTwoInputStreamOperatorTestHarness;
import org.junit.jupiter.api.Test;

class DelayedJoinTest {
    private KeyedTwoInputStreamOperatorTestHarness<String, Event, Event, Joined> harness() throws Exception {
        return new KeyedTwoInputStreamOperatorTestHarness<>(
                new KeyedCoProcessOperator<>(new DelayedJoin(10000, 2000, 30000)),
                event -> event.orderId, event -> event.orderId, Types.STRING);
    }
    private void watermark(KeyedTwoInputStreamOperatorTestHarness<String, Event, Event, Joined> h, long value)
            throws Exception {
        h.processWatermark1(new Watermark(value)); h.processWatermark2(new Watermark(value));
    }
    private List<? extends Joined> results(KeyedTwoInputStreamOperatorTestHarness<String, Event, Event, Joined> h) {
        return h.extractOutputStreamRecords().stream().map(StreamRecord::getValue).toList();
    }
    @Test void holdsOrderUntilDelayedPaymentAndSuppressesDuplicate() throws Exception {
        try (var h = harness()) {
            h.open();
            Event order = new Event("order-1", "key-1", 1000, 1500);
            Event payment = new Event("pay-1", "key-1", 3000, 1500);
            h.processElement1(new StreamRecord<>(order, order.eventTime));
            assertEquals(0, results(h).size());
            watermark(h, 10000);
            h.processElement2(new StreamRecord<>(payment, payment.eventTime));
            h.processElement2(new StreamRecord<>(payment, payment.eventTime));
            assertEquals(1, results(h).size());
            assertEquals("SETTLED", results(h).get(0).status);
        }
    }
    @Test void paymentMayArriveFirst() throws Exception {
        try (var h = harness()) {
            h.open();
            h.processElement2(new StreamRecord<>(new Event("p", "key", 2000, 99), 2000));
            h.processElement1(new StreamRecord<>(new Event("o", "key", 1000, 100), 1000));
            assertEquals("AMOUNT_MISMATCH", results(h).get(0).status);
            assertEquals(2000, results(h).get(0).eventTime);
        }
    }
    @Test void emitsUnmatchedAtWatermarkDeadlineAndRoutesTooLateRecord() throws Exception {
        try (var h = harness()) {
            h.open();
            h.processElement1(new StreamRecord<>(new Event("o", "key", 1000, 100), 1000));
            watermark(h, 12999);
            assertNull(h.getSideOutput(DelayedJoin.REJECTED));
            watermark(h, 13000);
            assertTrue(h.getSideOutput(DelayedJoin.REJECTED).peek().getValue().contains("UNMATCHED_WATERMARK"));
            h.processElement2(new StreamRecord<>(new Event("p", "key", 1000, 100), 1000));
            assertEquals(2, h.getSideOutput(DelayedJoin.REJECTED).size());
            assertEquals(0, results(h).size());
        }
    }
    @Test void idleProcessingTimerBoundsStateEvenWhenWatermarksStop() throws Exception {
        try (var h = harness()) {
            h.open();
            h.processElement1(new StreamRecord<>(new Event("o", "key", 1000, 100), 1000));
            h.setProcessingTime(30001);
            assertTrue(h.getSideOutput(DelayedJoin.REJECTED).peek().getValue().contains("UNMATCHED_IDLE_RETENTION"));
            assertEquals(0, h.numKeyedStateEntries());
        }
    }
    @Test void restoresPendingKeyAndTimersFromCheckpoint() throws Exception {
        var first = harness(); first.open();
        first.processElement1(new StreamRecord<>(new Event("o", "key", 1000, 100), 1000));
        var snapshot = first.snapshot(1, 100);
        first.close();
        try (var restored = harness()) {
            restored.setup(); restored.initializeState(snapshot); restored.open();
            restored.processElement2(new StreamRecord<>(new Event("p", "key", 2000, 100), 2000));
            assertEquals(1, results(restored).size());
            watermark(restored, 14000);
            assertEquals(0, restored.numKeyedStateEntries());
        }
    }
    @Test void rejectsCounterpartOutsideConfiguredInterval() throws Exception {
        try (var h = harness()) {
            h.open();
            h.processElement1(new StreamRecord<>(new Event("o", "key", 1000, 100), 1000));
            h.processElement2(new StreamRecord<>(new Event("p", "key", 12000, 100), 12000));
            assertEquals(0, results(h).size());
            assertTrue(h.getSideOutput(DelayedJoin.REJECTED).peek().getValue().contains("OUTSIDE_JOIN_INTERVAL"));
        }
    }
}
