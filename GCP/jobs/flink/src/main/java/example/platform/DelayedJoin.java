package example.platform;

import java.util.Map;
import org.apache.flink.api.common.functions.OpenContext;
import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.metrics.Counter;
import org.apache.flink.streaming.api.TimeDomain;
import org.apache.flink.streaming.api.functions.co.KeyedCoProcessFunction;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;

/** Symmetric event-time interval join with explicit, observable retention bounds. */
public class DelayedJoin extends KeyedCoProcessFunction<String, Event, Event, Joined> {
    public static final OutputTag<String> REJECTED = new OutputTag<String>("join-rejected") {};
    private final long horizonMs;
    private final long latenessMs;
    private final long retentionMs;
    private transient ValueState<Event> order;
    private transient ValueState<Event> payment;
    private transient ValueState<Boolean> matched;
    private transient ValueState<Long> eventDeadline;
    private transient ValueState<Long> processingDeadline;
    private transient Counter matches, duplicates, lateAccepted, lateRejected, unmatched, conflicts;
    private transient long lastWatermark, lastLag;

    public DelayedJoin(long horizonMs, long latenessMs, long retentionMs) {
        if (horizonMs <= 0 || latenessMs < 0 || retentionMs < horizonMs + latenessMs) {
            throw new IllegalArgumentException("Invalid join retention policy");
        }
        this.horizonMs = horizonMs; this.latenessMs = latenessMs; this.retentionMs = retentionMs;
    }
    @Override public void open(OpenContext context) throws Exception {
        order = getRuntimeContext().getState(new ValueStateDescriptor<>("order-v1", Event.class));
        payment = getRuntimeContext().getState(new ValueStateDescriptor<>("payment-v1", Event.class));
        matched = getRuntimeContext().getState(new ValueStateDescriptor<>("matched-v1", Boolean.class));
        eventDeadline = getRuntimeContext().getState(new ValueStateDescriptor<>("event-deadline-v1", Long.class));
        processingDeadline = getRuntimeContext().getState(new ValueStateDescriptor<>("processing-deadline-v1", Long.class));
        var metrics = getRuntimeContext().getMetricGroup().addGroup("join");
        matches = metrics.counter("matched_total"); duplicates = metrics.counter("duplicates_total");
        lateAccepted = metrics.counter("late_accepted_total"); lateRejected = metrics.counter("late_rejected_total");
        unmatched = metrics.counter("unmatched_total"); conflicts = metrics.counter("conflicts_total");
        metrics.gauge("last_watermark_ms", () -> lastWatermark);
        metrics.gauge("last_event_lag_ms", () -> lastLag);
    }
    @Override public void processElement1(Event value, Context ctx, Collector<Joined> out) throws Exception {
        accept(value, true, ctx, out);
    }
    @Override public void processElement2(Event value, Context ctx, Collector<Joined> out) throws Exception {
        accept(value, false, ctx, out);
    }
    private void accept(Event value, boolean isOrder, Context ctx, Collector<Joined> out) throws Exception {
        lastWatermark = ctx.timerService().currentWatermark();
        lastLag = Math.max(0, ctx.timerService().currentProcessingTime() - value.eventTime);
        long expiry = Math.addExact(value.eventTime, Math.addExact(horizonMs, latenessMs));
        if (lastWatermark >= expiry) {
            lateRejected.inc(); reject(ctx, "JOIN_HORIZON_EXPIRED", value); return;
        }
        if (value.eventTime < lastWatermark) { lateAccepted.inc(); }
        ValueState<Event> own = isOrder ? order : payment;
        Event existing = own.value();
        if (existing != null) {
            if (existing.eventId.equals(value.eventId) && existing.eventTime == value.eventTime
                    && existing.amountCents == value.amountCents) { duplicates.inc(); }
            else { conflicts.inc(); reject(ctx, "CONFLICTING_EVENT_FOR_KEY", value); }
            return;
        }
        Event other = (isOrder ? payment : order).value();
        if (other != null && Math.abs(value.eventTime - other.eventTime) > horizonMs) {
            conflicts.inc(); reject(ctx, "OUTSIDE_JOIN_INTERVAL", value); return;
        }
        own.update(value);
        Long previous = eventDeadline.value();
        if (previous == null || expiry > previous) {
            if (previous != null) { ctx.timerService().deleteEventTimeTimer(previous); }
            eventDeadline.update(expiry); ctx.timerService().registerEventTimeTimer(expiry);
        }
        if (processingDeadline.value() == null) {
            long safety = Math.addExact(ctx.timerService().currentProcessingTime(), retentionMs);
            processingDeadline.update(safety); ctx.timerService().registerProcessingTimeTimer(safety);
        }
        if (other != null && !Boolean.TRUE.equals(matched.value())) {
            out.collect(new Joined(order.value(), payment.value())); matched.update(true); matches.inc();
            // Retain both IDs until the deadline as a deduplication tombstone.
        }
    }
    private void reject(Context ctx, String reason, Event value) {
        ctx.output(REJECTED, Event.json(Map.of("reason", reason, "event", value)));
    }
    @Override public void onTimer(long timestamp, OnTimerContext ctx, Collector<Joined> out) throws Exception {
        Long expected = ctx.timeDomain() == TimeDomain.EVENT_TIME ? eventDeadline.value() : processingDeadline.value();
        if (expected == null || expected != timestamp) { return; }
        if (!Boolean.TRUE.equals(matched.value())) {
            Event value = order.value() != null ? order.value() : payment.value();
            if (value != null) {
                unmatched.inc();
                ctx.output(REJECTED, Event.json(Map.of("reason",
                        ctx.timeDomain() == TimeDomain.EVENT_TIME ? "UNMATCHED_WATERMARK_EXPIRED" : "UNMATCHED_IDLE_RETENTION",
                        "event", value)));
            }
        }
        if (eventDeadline.value() != null) { ctx.timerService().deleteEventTimeTimer(eventDeadline.value()); }
        if (processingDeadline.value() != null) { ctx.timerService().deleteProcessingTimeTimer(processingDeadline.value()); }
        order.clear(); payment.clear(); matched.clear(); eventDeadline.clear(); processingDeadline.clear();
    }
}
