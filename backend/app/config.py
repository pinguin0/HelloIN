import os


class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/helloin")
    DB_NAME = os.getenv("DB_NAME", "helloin")
    PRIVACY_VERSION = os.getenv("PRIVACY_VERSION", "v1")
    PRIVACY_TEXT = os.getenv(
        "PRIVACY_TEXT",
        "Informativa privacy demo per HelloIN. I dati saranno usati per la gestione dell'accesso.",
    )
    RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "30"))
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
