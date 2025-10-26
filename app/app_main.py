"""Entry point de la aplicación"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import check, partidos, usuarios, invitaciones
from app.api.routers.exception_handler import configurar_exception_handlers
from app.utils.config import settings

# Crear aplicación
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="API RESTful para gestionar partidos de fútbol amateur",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar manejadores de excepciones
configurar_exception_handlers(app)

# Registrar routers
app.include_router(check.router)
app.include_router(partidos.router)
app.include_router(usuarios.router)
app.include_router(invitaciones.router)


@app.get("/")
def root():
    return {
        "mensaje": "API ME FALTA UNO",
        "version": settings.API_VERSION,
        "arquitectura": "Capas con Repositorios",
        "endpoints": {
            "partidos": "/partidos",
            "usuarios": "/usuarios",
            "invitaciones": "/invitaciones",
            "health": "/health",
            "documentacion": "/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)