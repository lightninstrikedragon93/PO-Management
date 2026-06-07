from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importurile noastre din Core
from app.core.config import settings
from app.core.database import engine, Base
from app.core.exceptions import add_exception_handlers

# Importurile Routerelor
from app.api.routers import auth, purchase_orders

def create_app() -> FastAPI:
    """Funcție factory pentru a construi și configura instanța FastAPI."""
    
    # 1. Inițializăm aplicația
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="REST API for the Purchase Order Management System."
    )

    # 2. Configurare CORS (Crucial pentru conectarea cu Next.js)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"], # Aici punem portul frontend-ului
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. Crearea tabelelor în Baza de Date
    # Într-un mediu de producție real am folosi Alembic pentru migrații, 
    # dar pentru MVP, acest call creează tabelele automat la startup.
    Base.metadata.create_all(bind=engine)

    # 4. Adăugăm handlerele globale de erori (din core/exceptions.py)
    add_exception_handlers(app)

    # 5. Înregistrăm Routerele (Endpoints)
    app.include_router(auth.router, prefix="/api")
    app.include_router(purchase_orders.router, prefix="/api")

    return app

# Instanța care va fi rulată de uvicorn (ex: uvicorn app.main:app --reload)
app = create_app()

@app.get("/", tags=["Health"])
def health_check():
    """Endpoint simplu pentru a verifica dacă serverul este Up."""
    return {"status": "ok", "app": settings.PROJECT_NAME}