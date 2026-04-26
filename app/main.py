from fastapi import FastAPI
from app.config import get_settings
from app.middleware import RequestContextMiddleware
from app.exceptions import register_exception_handlers
from app.routers import books

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        # Disable interactive docs in production
        # docs_url="/docs" if settings.debug else None,
        # redoc_url="/redoc" if settings.debug else None,
    )

    # register middleware
    app.add_middleware(RequestContextMiddleware)

    # register exception handlers
    register_exception_handlers(app)

    # register routers
    app.include_router(books.router)

    # Health check - no router, lives on main app
    @app.get("/health")
    def health():
        return {"status": "ok", "version": settings.app_version}

    
    return app

app = create_app()