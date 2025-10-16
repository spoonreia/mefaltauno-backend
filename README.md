# ME FALTA UNO API - Arquitectura Hexagonal

API RESTful para gestionar partidos de fútbol amateur.

## 🏗️ Arquitectura

Este proyecto implementa **Arquitectura Hexagonal (Ports & Adapters)**:
```
├── domain/          # Lógica de negocio pura
├── application/     # Casos de uso
└── infrastructure/  # Detalles técnicos (API, BD, etc.)
```

## 🚀 Instalación
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## ▶️ Ejecutar
```bash
# Desarrollo
uvicorn app.main:app --reload

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentación API

Una vez iniciado el servidor, visita:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Tests
```bash
pytest
```

## 📁 Estructura de Carpetas
```
backend/
├── app/
│   ├── domain/              # Entidades, servicios de dominio
│   ├── application/         # Casos de uso
│   ├── infrastructure/      # API, repositorios, utils
│   └── config/              # Configuración
├── tests/                   # Tests unitarios e integración
└── requirements.txt
```

## 🔑 Conceptos Clave

### Domain (Dominio)
- **Entidades**: Objetos del negocio (Partido, Usuario)
- **Servicios de Dominio**: Lógica que no pertenece a una entidad
- **Excepciones**: Errores del dominio

### Application (Aplicación)
- **Casos de Uso**: Orquestan las operaciones del dominio
- **DTOs**: Objetos de transferencia de datos

### Infrastructure (Infraestructura)
- **Repositorios**: Acceso a datos (implementan interfaces del dominio)
- **API Routes**: Endpoints REST
- **Schemas**: Validación de entrada/salida (Pydantic)

## 🔄 Flujo de una petición
```
API Request → Routes → Use Case → Domain Service → Repository → DB
                                       ↓
                                   Entities
```

## 🛠️ Tecnologías

- **FastAPI**: Framework web
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI

## 📝 Próximos pasos

- [ ] Implementar base de datos real (PostgreSQL)
- [ ] Agregar autenticación JWT
- [ ] Implementar tests unitarios
- [ ] Agregar logging
- [ ] Implementar cache (Redis)