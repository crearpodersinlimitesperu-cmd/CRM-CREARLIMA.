from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Importaciones locales
from db_core import get_db
import db_models
from logger_core import log

app = FastAPI(
    title="CREAR LIMA - Enterprise API",
    description="API Gateway Core para el Ecosistema CPSL",
    version="2.0.0"
)

# Configurar CORS para permitir comunicación con el futuro frontend (NextJS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Se debe restringir en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    log.info("Iniciando Enterprise API (FastAPI)...")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "CREAR LIMA API Gateway Operativo", "version": "2.0.0"}

@app.get("/api/v1/coordinadoras")
def listar_coordinadoras(db: Session = Depends(get_db)):
    """Obtiene la lista de coordinadoras activas desde la base de datos SSOT."""
    try:
        coordinadoras = db.query(db_models.Coordinadora).all()
        return {"data": [{"id": c.id, "nombre": c.nombre, "rol": c.rol} for c in coordinadoras]}
    except Exception as e:
        log.error(f"Error en /api/v1/coordinadoras: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# NOTA: En futuras iteraciones se agregarán los endpoints de IA, Participantes y KPIs.
