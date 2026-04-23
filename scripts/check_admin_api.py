"""E2E test: admin login + list tiles via HTTP."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app
from shared.config import config

client = TestClient(app)
admin_id = config.ADMIN_IDS[0]

# 1. Login
print("1. LOGIN /api/admin/auth/login")
r = client.post(
    "/api/admin/auth/login",
    json={
        "telegram_id": admin_id,
        "password": config.ADMIN_PASSWORD.get_secret_value() if config.ADMIN_PASSWORD else "",
    },
)
print(f"   status={r.status_code}")
if r.status_code != 200:
    print(f"   body={r.text}")
    sys.exit(1)
token = r.json()["token"]
print(f"   token={token[:40]}... (len={len(token)})")

# 2. GET /api/home/admin/layout with Admin token
print("\n2. GET /api/home/admin/layout  [Authorization: Admin <token>]")
r = client.get("/api/home/admin/layout", headers={"Authorization": f"Admin {token}"})
print(f"   status={r.status_code}")
if r.status_code == 200:
    tiles = r.json()
    print(f"   tiles count: {len(tiles)}")
    for t in tiles:
        title = (t.get("content") or {}).get("title", "<no title>")
        print(f"     id={t.get('id')} type={t.get('type')} active={t.get('is_active')} title={title!r}")
else:
    print(f"   body={r.text}")

# 3. GET without auth (what happens)
print("\n3. GET /api/home/admin/layout  [no Authorization header]")
r = client.get("/api/home/admin/layout")
print(f"   status={r.status_code}  body={r.text[:150]}")

# 4. Public endpoint
print("\n4. GET /api/home/layout (public)")
r = client.get("/api/home/layout")
print(f"   status={r.status_code}")
if r.status_code == 200:
    print(f"   tiles count: {len(r.json())}")
