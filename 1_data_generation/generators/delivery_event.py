
import uuid
import random

from faker import Faker
from datetime import datetime, timezone

fake = Faker()


def generate_delivery_event(
    order_id=None,
    rider_id=None,
    store_id=None,
    city=None,
    expected_delivery_minutes=15
):
    actual = random.randint(10, 25)
    event_time = datetime.now(timezone.utc).isoformat()

    return {
        "delivery_id": f"DLV{uuid.uuid4().hex[:8]}",
        "order_id": order_id or f"ORD{uuid.uuid4().hex[:8]}",
        "rider_id": rider_id or f"RID{fake.random_int(1000, 9999)}",
        "store_id": store_id or f"STR{fake.random_int(100, 999)}",
        "city": city or fake.city(),
        "expected_delivery_minutes": expected_delivery_minutes,
        "actual_delivery_minutes": actual,
        "delivery_status": (
            "ON_TIME"
            if actual <= expected_delivery_minutes
            else "DELAYED"
        ),
        "delivery_time": event_time,
        "event_time": event_time
    }


if __name__ == "__main__":
    print(generate_delivery_event())
