import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
service_key_path = BASE_DIR / "serviceAccountKey.json"

db = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    if service_key_path.exists():
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_key_path)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
except Exception as e:
    print(f"Warning: Firebase Admin initialization skipped: {e}")