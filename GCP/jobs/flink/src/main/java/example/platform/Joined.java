package example.platform;

import java.io.Serializable;

public class Joined implements Serializable {
    public String orderId;
    public String orderEventId;
    public String paymentEventId;
    public long eventTime;
    public long amountCents;
    public String status;
    public Joined() {}
    public Joined(Event order, Event payment) {
        orderId = order.orderId; orderEventId = order.eventId; paymentEventId = payment.eventId;
        eventTime = Math.max(order.eventTime, payment.eventTime);
        amountCents = payment.amountCents;
        status = order.amountCents == payment.amountCents ? "SETTLED" : "AMOUNT_MISMATCH";
    }
}
