import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

cred_json = os.getenv("FIREBASE_CREDENTIALS")

cred_dict = json.loads(cred_json)

cred = credentials.Certificate(cred_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
