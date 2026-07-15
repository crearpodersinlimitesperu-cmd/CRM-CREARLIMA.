import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from logger_core import log

# En Fase 2 usamos SQLite como stepping-stone seguro, 
# para migrar luego a PostgreSQL sin cambiar el código, solo la URL.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cpsl_master.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}, # Necesario para SQLite en multihilo (ej. FastAPI/Streamlit)
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    log.info("Inicializando esquemas de Base de Datos (SSOT)...")
    Base.metadata.create_all(bind=engine)
    log.info("Esquemas de BDD inicializados correctamente.")
