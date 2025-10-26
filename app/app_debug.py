"""Entry point para desarrollo con hot-reload"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.app_main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )