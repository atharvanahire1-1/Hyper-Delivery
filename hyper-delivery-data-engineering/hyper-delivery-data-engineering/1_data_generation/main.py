
import argparse

from generators.order_event import generate_order_event
from generators.delivery_event import generate_delivery_event
from generators.product_event import generate_product_event
from generators.rider_event import generate_rider_event

from producers.kafka_producer import send_event, flush
from config.kafka_config import TOPICS


def generate_and_publish_batch(batch_size):
    print(f"Starting batch generation: {batch_size} orders")

    for i in range(batch_size):

        # 1. Generate an order
        order = generate_order_event()

        # 2. Generate a rider in the same city
        rider = generate_rider_event(
            city=order["city"],
            rider_status="BUSY",
            current_orders=1
        )

        # 3. Generate a delivery linked to that order and rider
        delivery = generate_delivery_event(
            order_id=order["order_id"],
            rider_id=rider["rider_id"],
            store_id=order["store_id"],
            city=order["city"]
        )

        # 4. Generate a product linked to that order
        product = generate_product_event(
            order_id=order["order_id"],
            store_id=order["store_id"],
            city=order["city"]
        )

        # 5. Publish all four events to Kafka
        send_event(
            TOPICS["order"],
            order,
            key=order["order_id"]
        )

        send_event(
            TOPICS["delivery"],
            delivery,
            key=delivery["delivery_id"]
        )

        send_event(
            TOPICS["product"],
            product,
            key=product["product_id"]
        )

        send_event(
            TOPICS["rider"],
            rider,
            key=rider["rider_id"]
        )

        print(f"Generated batch record {i + 1}/{batch_size}")

    # Wait for Kafka delivery confirmations
    delivered = flush()

    expected = batch_size * 4

    print("\n========== BATCH SUMMARY ==========")
    print(f"Orders generated: {batch_size}")
    print(f"Expected messages: {expected}")
    print(f"Messages confirmed delivered: {delivered}")
    print("===================================")


def main():
    parser = argparse.ArgumentParser(
        description="Hyper Delivery Kafka Event Generator"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of orders to generate (default: 10)"
    )

    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")

    generate_and_publish_batch(args.count)


if __name__ == "__main__":
    main()
