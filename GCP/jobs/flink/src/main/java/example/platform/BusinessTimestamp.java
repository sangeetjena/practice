package example.platform;

import org.apache.flink.streaming.api.operators.AbstractStreamOperator;
import org.apache.flink.streaming.api.operators.OneInputStreamOperator;
import org.apache.flink.streaming.runtime.streamrecord.StreamRecord;

/** Replace record timestamps while preserving upstream watermarks, including idle-input progress. */
public class BusinessTimestamp extends AbstractStreamOperator<Joined>
        implements OneInputStreamOperator<Joined, Joined> {
    @Override public void processElement(StreamRecord<Joined> element) {
        output.collect(new StreamRecord<>(element.getValue(), element.getValue().eventTime));
    }
}
