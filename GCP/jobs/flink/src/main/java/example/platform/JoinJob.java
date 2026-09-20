package example.platform;

import java.time.Duration;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Map;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.common.serialization.SimpleStringEncoder;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.connector.file.src.FileSource;
import org.apache.flink.connector.file.src.reader.TextLineInputFormat;
import org.apache.flink.connector.file.sink.FileSink;
import org.apache.flink.core.fs.Path;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.sink.filesystem.rollingpolicies.OnCheckpointRollingPolicy;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;
import org.slf4j.LoggerFactory;

public class JoinJob {
    private static final OutputTag<Joined> WINDOW_LATE = new OutputTag<Joined>("window-too-late") {};

    public static void main(String[] args) throws Exception {
        ParameterTool p = ParameterTool.fromArgs(args);
        var env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.getConfig().setGlobalJobParameters(p); // References and non-secret arguments only.
        boolean continuous = p.getBoolean("continuous", true);
        LoggerFactory.getLogger(JoinJob.class).info("Starting reconciliation continuous={} configHash={}",
                continuous, p.get("config-hash", "local"));
        long horizon = positive(p, "join-horizon-seconds", 86400) * 1000;
        long lateness = p.getLong("allowed-lateness-seconds", 3600) * 1000;
        long retention = positive(p, "max-retention-seconds", 259200) * 1000;
        DataStream<Event> orders = source(env, p, "orders", continuous);
        DataStream<Event> payments = source(env, p, "payments", continuous);
        var joined = orders.keyBy(value -> value.orderId).connect(payments.keyBy(value -> value.orderId))
                .process(new DelayedJoin(horizon, lateness, retention)).uid("delayed-order-payment-join-v1")
                .name("orders-payments-stateful-join");
        String output = p.getRequired("output-uri");
        sink(joined.map(Event::json), output + "/joined", "joined-files-v1");
        sink(joined.getSideOutput(DelayedJoin.REJECTED), output + "/rejected", "rejected-files-v1");

        // Preserve each match's business event time even when its counterpart arrives late.
        var timed = joined.transform("business-event-time", TypeInformation.of(Joined.class),
                new BusinessTimestamp()).uid("business-time-v1");
        var summaries = timed.keyBy(value -> value.status)
                .window(TumblingEventTimeWindows.of(Time.seconds(positive(p, "window-seconds", 300))))
                .allowedLateness(Time.milliseconds(lateness)).sideOutputLateData(WINDOW_LATE)
                .aggregate(new Totals(), new StampWindow()).uid("settlement-window-v1");
        sink(summaries, output + "/window-updates", "window-files-v1");
        sink(summaries.getSideOutput(WINDOW_LATE).map(row -> Event.json(Map.of(
                "reason", "WINDOW_ALREADY_CLOSED", "match", row))), output + "/window-late", "window-late-files-v1");
        env.execute("orders-payments-reconciliation");
    }
    private static long positive(ParameterTool p, String name, long fallback) {
        long value = p.getLong(name, fallback);
        if (value <= 0) { throw new IllegalArgumentException(name + " must be positive"); }
        return value;
    }
    private static DataStream<Event> source(StreamExecutionEnvironment env, ParameterTool p, String name,
                                             boolean continuous) {
        String prefix = p.getRequired(name + "-uri");
        var paths = new ArrayList<Path>();
        if (continuous) { paths.add(new Path(prefix)); }
        else {
            LocalDate start = LocalDate.parse(p.getRequired("start-date"));
            LocalDate end = LocalDate.parse(p.getRequired("end-date"));
            if (!start.isBefore(end) || end.toEpochDay() - start.toEpochDay() > 366) {
                throw new IllegalArgumentException("Invalid bounded date window");
            }
            for (LocalDate date = start; date.isBefore(end); date = date.plusDays(1)) {
                paths.add(new Path(prefix + "/event_date=" + date));
            }
        }
        var files = FileSource.forRecordStreamFormat(new TextLineInputFormat(), paths.toArray(Path[]::new));
        if (continuous) { files.monitorContinuously(Duration.ofSeconds(positive(p, "file-discovery-seconds", 10))); }
        var events = env.fromSource(files.build(), WatermarkStrategy.noWatermarks(), name + "-files")
                .uid(name + "-source-v1").map(Event::parse).returns(Event.class).uid(name + "-parse-v1");
        if (!continuous) {
            long start = LocalDate.parse(p.getRequired("start-date")).atStartOfDay().toInstant(ZoneOffset.UTC).toEpochMilli();
            long end = LocalDate.parse(p.getRequired("end-date")).atStartOfDay().toInstant(ZoneOffset.UTC).toEpochMilli();
            events = events.filter(value -> value.eventTime >= start && value.eventTime < end);
        }
        return events.assignTimestampsAndWatermarks(WatermarkStrategy.<Event>forBoundedOutOfOrderness(
                Duration.ofSeconds(p.getLong("out-of-orderness-seconds", 30)))
                .withTimestampAssigner((value, old) -> value.eventTime)
                .withIdleness(Duration.ofSeconds(positive(p, "idle-timeout-seconds", 120))));
    }
    private static void sink(DataStream<String> rows, String uri, String uid) {
        rows.sinkTo(FileSink.forRowFormat(new Path(uri), new SimpleStringEncoder<String>("UTF-8"))
                .withRollingPolicy(OnCheckpointRollingPolicy.build()).build()).uid(uid);
    }
    public static class Totals implements AggregateFunction<Joined, long[], long[]> {
        public long[] createAccumulator() { return new long[]{0, 0}; }
        public long[] add(Joined value, long[] acc) { acc[0]++; acc[1] = Math.addExact(acc[1], value.amountCents); return acc; }
        public long[] getResult(long[] acc) { return acc; }
        public long[] merge(long[] a, long[] b) { return new long[]{Math.addExact(a[0], b[0]), Math.addExact(a[1], b[1])}; }
    }
    public static class StampWindow extends ProcessWindowFunction<long[], String, String, TimeWindow> {
        public void process(String status, Context ctx, Iterable<long[]> values, Collector<String> out) {
            long[] total = values.iterator().next();
            out.collect(Event.json(Map.of("record_type", "window_upsert", "status", status,
                    "window_start_ms", ctx.window().getStart(), "window_end_ms", ctx.window().getEnd(),
                    "count", total[0], "amount_cents", total[1])));
        }
    }
}
