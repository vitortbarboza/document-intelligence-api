from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.routes.health import router as health_router
from app.api.routes.documents import router as documents_router


app = FastAPI(title="Document Intelligence API", version="0.1.0")

app.include_router(health_router)
app.include_router(documents_router)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")
