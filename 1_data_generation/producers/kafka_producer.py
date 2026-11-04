
import json
import time

from confluent_kafka import Producer
from config.kafka_config import KAFKA_CONFIG


# Create one Kafka producer for the application
producer = Producer(KAFKA_CONFIG)

# Track delivery results
delivered_count = 0
delivery_errors = []


def delivery_report(err, msg):
    """Called when Kafka confirms message delivery or reports failure."""
    global delivered_count

    if err is not None:
        error_message = f"{msg.topic()}: {err}"
        delivery_errors.append(error_message)
        print(f"DELIVERY FAILED: {error_message}")
    else:
        delivered_count += 1


def send_event(topic, event, key=None):
    """Serialize and send one event to a Kafka topic."""

    if not topic:
        raise ValueError("Kafka topic cannot be empty")

    # Convert the event into JSON
    message_value = json.dumps(
        event,
        ensure_ascii=False
    )

    # Preserve valid keys, including 0 or empty-string keys
    message_key = str(key) if key is not None else None

    # Retry if the local Kafka producer queue is full
    deadline = time.monotonic() + 30

    while True:
        try:
            producer.produce(
                topic=topic,
                key=message_key,
                value=message_value,
                on_delivery=delivery_report
            )

            # Process any available delivery callbacks
            producer.poll(0)
            break

        except BufferError:
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Kafka producer queue remained full for topic: {topic}"
                )

            producer.poll(0.5)


def flush(timeout=30):
    """Wait for all queued messages and verify delivery."""

    remaining = producer.flush(timeout)

    if remaining > 0:
        raise TimeoutError(
            f"{remaining} Kafka messages were not delivered "
            f"within {timeout} seconds."
        )

    if delivery_errors:
        error_summary = "; ".join(delivery_errors[:5])
        raise RuntimeError(
            f"Kafka delivery completed with errors: {error_summary}"
        )

    print(
        f"Kafka delivery completed successfully. "
        f"Messages delivered: {delivered_count}"
    )

    return delivered_count
