from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from .api.auth import router as auth_router
from .api.loads import router as loads_router
from .api.organizations import router as orgs_router
from .api.vehicles import router as vehicles_router
from .config import settings

app = FastAPI(
    title="F4ST API",
    version="0.1.0",
    description=(
        "F4ST Nakliye Platformu için REST API.\n\n"
        "Başlıca özellikler:\n"
        "- Kullanıcı kayıt ve kimlik doğrulama (JWT)\n"
        "- Kuruluş ve kullanıcı ilişkileri (ileri sürümlerde)\n"
    ),
    terms_of_service="https://f4st.com/terms",
    contact={
        "name": "F4ST",
        "url": "https://f4st.com",
        "email": "info@f4st.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "auth",
            "description": "Kullanıcı kayıt, giriş, token yenileme ve profil bilgileri",
        },
        {
            "name": "health",
            "description": "Servis sağlık kontrolü",
        },
        {
            "name": "organizations",
            "description": "Organizasyon CRUD uç noktaları",
        },
        {
            "name": "vehicles",
            "description": "Araç CRUD uç noktaları",
        },
        {
            "name": "loads",
            "description": "Yük CRUD uç noktaları",
        },
    ],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Inject servers list dynamically from settings and ENV
    servers = []
    # always include local
    if settings.LOCAL_API_URL:
        servers.append({"url": settings.LOCAL_API_URL, "description": "Local"})
    # include staging
    if settings.STAGING_API_URL:
        servers.append({"url": settings.STAGING_API_URL, "description": "Staging"})
    # include prod
    if settings.PROD_API_URL:
        servers.append({"url": settings.PROD_API_URL, "description": "Production"})

    # Re-order to put current ENV first
    env_priority = {
        "local": settings.LOCAL_API_URL,
        "staging": settings.STAGING_API_URL,
        "prod": settings.PROD_API_URL,
        "production": settings.PROD_API_URL,
    }
    preferred = env_priority.get(str(settings.ENV).lower())
    if preferred:
        servers = sorted(servers, key=lambda s: 0 if s["url"] == preferred else 1)

    openapi_schema["servers"] = servers
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[assignment]


@app.get(
    "/health",
    tags=["health"],
    summary="Sağlık kontrolü",
    description="Servisin çalıştığını doğrulamak için basit bir sağlık uç noktası.",
)
def health_check():
    return {
        "status": "ok",
        "app": app.title,
        "version": app.version,
        "env": settings.ENV,
    }


# Routers
app.include_router(auth_router)
app.include_router(orgs_router)
app.include_router(vehicles_router)
app.include_router(loads_router)


# Static assets (for Swagger UI branding)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} — Dokümanlar",
        swagger_favicon_url="/static/logo.svg",
        swagger_css_url="/static/swagger.css",
    )
