package example.platform;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.Serializable;
import java.time.Instant;

/** One order and one payment per globally unique orderId; not a many-to-many join. */
public class Event implements Serializable {
    private static final ObjectMapper JSON = new ObjectMapper();
    public String eventId;
    public String orderId;
    public long eventTime;
    public long amountCents;

    public Event() {}
    public Event(String eventId, String orderId, long eventTime, long amountCents) {
        this.eventId = eventId; this.orderId = orderId;
        this.eventTime = eventTime; this.amountCents = amountCents;
    }
    public static Event parse(String line) throws Exception {
        JsonNode node = JSON.readTree(line);
        for (String name : new String[]{"event_id", "order_id", "event_time"}) {
            if (!node.path(name).isTextual() || node.path(name).asText().isBlank()) {
                throw new IllegalArgumentException("Missing string field: " + name);
            }
        }
        if (!node.path("amount_cents").isIntegralNumber() || !node.path("amount_cents").canConvertToLong()
                || node.path("amount_cents").asLong() < 0) {
            throw new IllegalArgumentException("amount_cents must be a nonnegative long");
        }
        return new Event(node.get("event_id").asText(), node.get("order_id").asText(),
                Instant.parse(node.get("event_time").asText()).toEpochMilli(), node.get("amount_cents").asLong());
    }
    public static String json(Object value) {
        try { return JSON.writeValueAsString(value); }
        catch (Exception e) { throw new IllegalArgumentException("Cannot encode output", e); }
    }
}
