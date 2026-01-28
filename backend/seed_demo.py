from datetime import datetime, timezone

from pymongo import MongoClient

MONGO_URI = "mongodb://mongo:27017/helloin"
DB_NAME = "helloin"

client = MongoClient(MONGO_URI)

db = client[DB_NAME]

privacy = db.privacy.find_one({"version": "v1"})
if not privacy:
    db.privacy.insert_one(
        {
            "version": "v1",
            "text": "Informativa privacy demo per HelloIN. I dati saranno usati per la gestione dell'accesso.",
            "updated_at": datetime.now(timezone.utc),
        }
    )

if db.visits.count_documents({}) == 0:
    db.visits.insert_one(
        {
            "token": "demo-token",
            "status": "completed",
            "form_data": {
                "first_name": "Giulia",
                "last_name": "Bianchi",
                "company": "Acme S.p.A.",
                "email": "giulia.bianchi@example.com",
                "phone": "+39 333 1234567",
                "purpose": "Audit sicurezza",
            },
            "consents": {"privacy": True, "marketing": False},
            "signature": {"data_url": None, "signed_at": None, "hash": ""},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "completed_at": datetime.now(timezone.utc),
        }
    )

print("Seed completed")
