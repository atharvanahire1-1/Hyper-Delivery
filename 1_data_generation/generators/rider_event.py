
import uuid
import random

from faker import Faker
from datetime import datetime, timezone

fake = Faker()


def generate_rider_event(
    rider_id=None,
    city=None,
    rider_status=None,
    current_orders=None
):
    status = rider_status or random.choice([
        "AVAILABLE",
        "BUSY",
        "OFFLINE"
    ])

    if current_orders is None:
        current_orders = (
            random.randint(1, 3) if status == "BUSY" else 0
        )

    event_time = datetime.now(timezone.utc).isoformat()

    return {
        "rider_id": rider_id or f"RID{uuid.uuid4().hex[:6]}",
        "city": city or fake.city(),
        "rider_status": status,
        "current_orders": current_orders,
        "event_time": event_time
    }


if __name__ == "__main__":
    print(generate_rider_event())
