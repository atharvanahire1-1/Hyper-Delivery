import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

load_dotenv(ENV_PATH)


KAFKA_CONFIG = {
    "bootstrap.servers": os.getenv("BOOTSTRAP_SERVERS"),
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": os.getenv("KAFKA_API_KEY"),
    "sasl.password": os.getenv("KAFKA_API_SECRET"),
    "acks": "all"
}


TOPICS = {
    "order": os.getenv("ORDER_TOPIC"),
    "delivery": os.getenv("DELIVERY_TOPIC"),
    "product": os.getenv("PRODUCT_TOPIC"),
    "rider": os.getenv("RIDER_TOPIC")
}