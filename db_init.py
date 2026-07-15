from db_core import init_db
import db_models # Importa para que Base conozca las tablas

if __name__ == "__main__":
    init_db()
    print("Base de datos SSOT inicializada con éxito.")
