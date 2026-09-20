package example.platform;

import static org.junit.jupiter.api.Assertions.*;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.runtime.streamrecord.StreamRecord;
import org.apache.flink.streaming.util.OneInputStreamOperatorTestHarness;
import org.junit.jupiter.api.Test;

class BusinessTimestampTest {
    @Test void replacesTimestampWithoutSwallowingWatermark() throws Exception {
        try (var h = new OneInputStreamOperatorTestHarness<Joined, Joined>(new BusinessTimestamp())) {
            h.open();
            var match = new Joined(new Event("o", "k", 2000, 100), new Event("p", "k", 1000, 100));
            h.processElement(new StreamRecord<>(match, 1000));
            h.processWatermark(new Watermark(3000));
            var output = h.getOutput().toArray();
            assertEquals(2000, ((StreamRecord<?>) output[0]).getTimestamp());
            assertEquals(new Watermark(3000), output[1]);
        }
    }
}
