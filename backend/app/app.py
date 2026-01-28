import base64
import hashlib
import hmac
import uuid
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, jsonify, request
from flask_cors import CORS

from .config import Config
from .db import get_db


def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "helloin-backend"})

    @app.get("/privacy/latest")
    def privacy_latest():
        db = get_db()
        privacy = db.privacy.find_one(sort=[("updated_at", -1)])
        if not privacy:
            privacy = {
                "version": Config.PRIVACY_VERSION,
                "text": Config.PRIVACY_TEXT,
                "updated_at": datetime.now(timezone.utc),
            }
            db.privacy.insert_one(privacy)
        privacy["_id"] = str(privacy["_id"])
        privacy["updated_at"] = privacy["updated_at"].isoformat()
        return jsonify(privacy)

    @app.post("/visit/start")
    def visit_start():
        db = get_db()
        token = uuid.uuid4().hex
        visit = {
            "token": token,
            "status": "started",
            "form_data": {},
            "consents": {},
            "signature": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        db.visits.insert_one(visit)
        return jsonify({"token": token})

    @app.get("/visit/<token>")
    def visit_get(token):
        db = get_db()
        visit = db.visits.find_one({"token": token})
        if not visit:
            return jsonify({"error": "not_found"}), 404
        return jsonify(_serialize_visit(visit))

    @app.post("/visit/<token>/submit")
    def visit_submit(token):
        payload = request.get_json(force=True)
        form_data = payload.get("form_data", {})
        consents = payload.get("consents", {})
        signature = payload.get("signature", {})
        if not consents.get("privacy"):
            return jsonify({"error": "privacy_required"}), 400
        db = get_db()
        visit = db.visits.find_one({"token": token})
        if not visit:
            return jsonify({"error": "not_found"}), 404
        signature_hash = ""
        if signature.get("data_url"):
            signature_hash = _hash_signature(signature["data_url"])
        update = {
            "form_data": form_data,
            "consents": consents,
            "signature": {
                "data_url": signature.get("data_url"),
                "signed_at": signature.get("signed_at"),
                "hash": signature_hash,
            },
            "status": "submitted",
            "updated_at": datetime.now(timezone.utc),
        }
        db.visits.update_one({"token": token}, {"$set": update})
        return jsonify({"status": "submitted"})

    @app.post("/visit/<token>/complete")
    def visit_complete(token):
        db = get_db()
        visit = db.visits.find_one({"token": token})
        if not visit:
            return jsonify({"error": "not_found"}), 404
        if visit.get("status") != "submitted":
            return jsonify({"error": "invalid_state"}), 400
        db.visits.update_one(
            {"token": token},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        return jsonify({"status": "completed"})

    @app.post("/auth/login")
    def auth_login():
        payload = request.get_json(force=True)
        email = payload.get("email")
        if not email:
            return jsonify({"error": "email_required"}), 400
        return jsonify({"token": "demo-token", "user": {"email": email}})

    @app.get("/admin/visits")
    def admin_visits():
        auth_response = _require_admin_auth()
        if auth_response:
            return auth_response
        db = get_db()
        visits = db.visits.find().sort("created_at", -1).limit(50)
        return jsonify([_serialize_visit(visit) for visit in visits])

    @app.get("/admin/stats")
    def admin_stats():
        auth_response = _require_admin_auth()
        if auth_response:
            return auth_response
        db = get_db()
        total = db.visits.count_documents({})
        started = db.visits.count_documents({"status": "started"})
        submitted = db.visits.count_documents({"status": "submitted"})
        completed = db.visits.count_documents({"status": "completed"})
        return jsonify(
            {
                "total": total,
                "started": started,
                "submitted": submitted,
                "completed": completed,
            }
        )

    @app.post("/admin/visits/delete")
    def admin_delete_visits():
        auth_response = _require_admin_auth()
        if auth_response:
            return auth_response
        payload = request.get_json(force=True) or {}
        ids = payload.get("ids", [])
        if not isinstance(ids, list) or not ids:
            return jsonify({"error": "ids_required"}), 400
        object_ids = []
        for raw_id in ids:
            try:
                object_ids.append(ObjectId(raw_id))
            except (InvalidId, TypeError):
                continue
        if not object_ids:
            return jsonify({"error": "invalid_ids"}), 400
        db = get_db()
        result = db.visits.delete_many({"_id": {"$in": object_ids}})
        return jsonify({"deleted": result.deleted_count})

    return app


def _hash_signature(data_url):
    try:
        header, encoded = data_url.split(",", 1)
    except ValueError:
        encoded = data_url
    raw = base64.b64decode(encoded)
    return hashlib.sha256(raw).hexdigest()


def _serialize_visit(visit):
    visit["_id"] = str(visit["_id"])
    for key in ["created_at", "updated_at", "completed_at"]:
        if visit.get(key):
            visit[key] = visit[key].isoformat()
    return visit


def _require_admin_auth():
    auth_header = request.headers.get("Authorization")
    if not _is_admin_authorized(auth_header):
        response = jsonify({"error": "unauthorized"})
        response.status_code = 401
        response.headers["WWW-Authenticate"] = 'Basic realm="HelloIN Admin"'
        return response
    return None


def _is_admin_authorized(auth_header):
    if not auth_header or not auth_header.startswith("Basic "):
        return False
    encoded = auth_header.split(" ", 1)[1]
    try:
        decoded = base64.b64decode(encoded).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return False
    username, separator, password = decoded.partition(":")
    if not separator:
        return False
    return hmac.compare_digest(username, Config.ADMIN_USERNAME) and hmac.compare_digest(
        password, Config.ADMIN_PASSWORD
    )
