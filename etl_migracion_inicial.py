import os
import pandas as pd
from db_core import SessionLocal
from db_models import Coordinadora, Participante, Asignacion
from logger_core import log

def poblar_coordinadoras(db):
    coords = ["Diana Moscoso", "Joyce Marin", "Linid", "Leyla", "Zuley Urteaga", "General"]
    for c_nombre in coords:
        if not db.query(Coordinadora).filter_by(nombre=c_nombre).first():
            c = Coordinadora(nombre=c_nombre, rol="CC")
            db.add(c)
    db.commit()
    log.info("Coordinadoras maestras inicializadas.")

def migrar_maestro_participantes(db):
    ruta_csv = os.path.join(os.path.dirname(__file__), "Master_Participantes_Limpio.csv")
    if not os.path.exists(ruta_csv):
        log.warning(f"No se encontró {ruta_csv} para migrar.")
        return

    try:
        df = pd.read_csv(ruta_csv)
        df = df.fillna("")
        agregados = 0
        for _, row in df.iterrows():
            dni = str(row.get("DNI", "")).strip()
            nombre = str(row.get("Nombres", "")).strip().title()
            apellido = str(row.get("Apellidos", "")).strip().title()
            
            # Filtro básico: Si no tiene nombre ni DNI válido, saltar
            if not nombre:
                continue
                
            # Evitar duplicados por DNI si existe (DNI es Unique index en BDD)
            if dni and db.query(Participante).filter_by(dni=dni).first():
                continue
            
            # Si no hay DNI, buscar por nombre exacto (heurística básica para evitar colisiones masivas)
            if not dni and db.query(Participante).filter_by(nombres=nombre, apellidos=apellido).first():
                continue

            tel = str(row.get("Teléfono", "")).strip()
            email = str(row.get("Email", "")).strip()
            imo = str(row.get("IMO Enrolador", "")).strip().title()

            p = Participante(
                dni=dni if dni else None,
                nombres=nombre,
                apellidos=apellido if apellido else None,
                telefono=tel if tel else None,
                email=email if email else None,
                imo_enrolador=imo if imo else None
            )
            db.add(p)
            agregados += 1
            
            # Flush periódicamente para evitar llenar memoria en batches gigantes
            if agregados % 500 == 0:
                db.commit()

        db.commit()
        log.info(f"Migrados {agregados} participantes únicos desde el Maestro.")
    except Exception as e:
        db.rollback()
        log.error(f"Error migrando maestro: {e}")

def run_etl():
    db = SessionLocal()
    try:
        poblar_coordinadoras(db)
        migrar_maestro_participantes(db)
        log.info("Proceso ETL Inicial concluido.")
    finally:
        db.close()

if __name__ == "__main__":
    log.info("Iniciando ETL de migración a BDD Central...")
    run_etl()
