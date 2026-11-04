
import uuid
import random

from faker import Faker
from datetime import datetime, timezone

fake = Faker()


def generate_order_event(
    order_id=None,
    user_id=None,
    store_id=None,
    city=None
):
    event_time = datetime.now(timezone.utc).isoformat()

    return {
        "order_id": order_id or f"ORD{uuid.uuid4().hex[:8]}",
        "user_id": user_id or f"USR{uuid.uuid4().hex[:6]}",
        "store_id": store_id or f"STR{fake.random_int(100, 999)}",
        "city": city or fake.city(),
        "order_status": random.choice([
            "PLACED",
            "CONFIRMED",
            "PACKED",
            "OUT_FOR_DELIVERY",
            "DELIVERED"
        ]),
        "order_value": round(random.uniform(50, 2000), 2),
        "items_count": fake.random_int(1, 10),
        "order_time": event_time,
        "event_time": event_time
    }


if __name__ == "__main__":
    print(generate_order_event())
