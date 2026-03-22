import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

load_dotenv(dotenv_path=".env")
client = QdrantClient(url=os.getenv("QDRANT_URL"))

client.create_collection(
    collection_name="hr_policies",
    vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
)
print(" Đã tạo xong collection hr_policies rỗng!")