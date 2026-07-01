import os
from pymongo import MongoClient

# Mengambil URL koneksi Mongo dari environment variable Docker
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://mongodb:27017/")

# Inisialisasi client dan database
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["simple_lms_nosql"]

# Koleksi data (Collections)
activity_logs = mongo_db["activity_logs"]
learning_analytics = mongo_db["learning_analytics"]