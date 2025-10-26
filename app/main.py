"""Entry point de la aplicación - COMPLETO"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.api.routes import partido_routes, usuario_routes, invitacion_routes

# Crear aplicación
app = FastAPI(
    title="ME FALTA UNO API",
    version="1.0.0",
    description="API RESTful para gestionar partidos de fútbol amateur - Arquitectura Hexagonal",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(partido_routes.router)
app.include_router(usuario_routes.router)
app.include_router(invitacion_routes.router)


@app.get("/")
def root():
    return {
        "mensaje": "API ME FALTA UNO - Arquitectura Hexagonal",
        "version": "1.0.0",
        "arquitectura": "Hexagonal (Ports & Adapters)",
        "endpoints": {
            "partidos": "/partidos",
            "usuarios": "/usuarios",
            "invitaciones": "/invitaciones",
            "documentacion": "/docs",
        },
    }


@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "ok", "service": "me-falta-uno-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)