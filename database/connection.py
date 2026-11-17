import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Permite importar models independientemente de dónde se ejecute el script
DATABASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DATABASE_DIR.parent
sys.path.append(str(DATABASE_DIR))
from models import Base

# Ruta del archivo SQLite en la raíz del proyecto
DATABASE_PATH = PROJECT_ROOT / "kellytix.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    print("Creando tablas en la base de datos SQLite...")
    Base.metadata.create_all(bind=engine)
    print("¡Base de datos kellytix.db e infraestructura de tablas creadas con éxito!")

if __name__ == "__main__":
    init_db()





