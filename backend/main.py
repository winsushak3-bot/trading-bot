import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from shared.utils.logger import setup_logger

setup_logger()  # Unified loguru + stdlib logging bridge for backend

from backend.api.routes import admin_auth, auth, charts, home, news, support, trading, users
from backend.api.routes.uploads import router as uploads_router
from backend.bot_webhook import router as telegram_webhook_router
from backend.bot_webhook import shutdown_bot_webhook, startup_bot_webhook

logger = logging.getLogger(__name__)

_BASE = os.path.dirname(__file__)


# ── Lifecycle ────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(application: FastAPI):
    await startup_bot_webhook()
    yield
    await shutdown_bot_webhook()


app = FastAPI(title="Trading Bot API", version="1.0.0", lifespan=lifespan)


# ── CORS ─────────────────────────────────────────────────────
_default_origins = ["http://localhost:5173", "http://localhost:5175", "http://localhost:3000"]
_extra = os.getenv("CORS_ORIGINS", "")  # запятая-разделённый список дополнительных origins
_origins = _default_origins + [o.strip() for o in _extra.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health (before static mounts) ────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


# ── API Routes ───────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin_auth.router, prefix="/api/admin/auth", tags=["admin-auth"])
app.include_router(trading.router, prefix="/api/trading", tags=["trading"])
app.include_router(support.router, prefix="/api/support", tags=["support"])
app.include_router(home.router, prefix="/api/home", tags=["home"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(uploads_router, prefix="/api/uploads", tags=["uploads"])
app.include_router(charts.router, prefix="/api/charts", tags=["charts"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(telegram_webhook_router, prefix="/api/telegram", tags=["telegram-webhook"])


# ── Error / 404 handlers ─────────────────────────────────────
# Любой неизвестный путь под /api/* должен вернуть JSON 404 (а не HTML index.html
# от SPA catch-all ниже). Регистрируем ДО статических маунтов.
@app.api_route("/api/{rest:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def api_not_found(rest: str):
    raise HTTPException(status_code=404, detail=f"API endpoint not found: /api/{rest}")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Логирует необработанные 500 со стеком и возвращает единый JSON формат."""
    logger.exception("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ── Static files ─────────────────────────────────────────────
uploads_dir = os.path.join(_BASE, "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

webapp_dist = os.path.join(_BASE, "..", "webapp", "dist")
webapp_assets = os.path.join(webapp_dist, "assets")
if os.path.exists(webapp_dist):
    if os.path.exists(webapp_assets):
        app.mount("/webapp/assets", StaticFiles(directory=webapp_assets), name="webapp-assets")

    @app.get("/webapp/{full_path:path}")
    async def serve_webapp(request: Request, full_path: str):
        """Serve webapp SPA with fallback to index.html for client-side routing."""
        file_path = os.path.normpath(os.path.join(webapp_dist, full_path))
        if not file_path.startswith(os.path.normpath(webapp_dist)):
            return FileResponse(os.path.join(webapp_dist, "index.html"))
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(webapp_dist, "index.html"))

admin_dist = os.path.join(_BASE, "..", "admin", "dist")
if os.path.exists(admin_dist):
    app.mount("/admin", StaticFiles(directory=admin_dist, html=True), name="admin")

