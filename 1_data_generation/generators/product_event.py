
import random

from faker import Faker
from datetime import datetime, timezone

fake = Faker()

PRODUCTS = [
    "Milk 1L",
    "Bread",
    "Eggs",
    "Fruits",
    "Vegetables"
]


def generate_product_event(
    order_id=None,
    store_id=None,
    city=None
):
    product = fake.random_element(PRODUCTS)
    event_time = datetime.now(timezone.utc).isoformat()

    return {
        "product_id": f"PRD{fake.random_int(1000, 9999)}",
        "product_name": product,
        "category": "Grocery",
        "order_id": order_id or f"ORD{fake.random_int(100000, 999999)}",
        "store_id": store_id or f"STR{fake.random_int(100, 999)}",
        "city": city or fake.city(),
        "quantity": fake.random_int(1, 5),
        "price": round(fake.random_number(digits=2), 2),
        "event_time": event_time
    }


if __name__ == "__main__":
    print(generate_product_event())
