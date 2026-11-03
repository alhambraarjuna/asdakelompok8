"""
scripts/4_unggah_mongodb.py — Pengunggah Dokumen Paspor ke MongoDB Atlas
"""
import os
import json
from pymongo import MongoClient

def main():
    mongo_uri = os.environ.get("MONGO_URI")
    if not mongo_uri:
        print("MONGO_URI belum diatur. Lewati unggah MongoDB (menggunakan mode lokal).")
        return
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    db = client["agrotrace_db"]
    col = db["paspor_batch"]
    with open("data/paspor.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for doc in data:
        col.replace_one({"id_batch": doc["id_batch"]}, doc, upsert=True)
    print(f"Berhasil mengunggah {len(data)} dokumen paspor ke MongoDB Atlas.")

if __name__ == "__main__":
    main()
