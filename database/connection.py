import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Permite importar models independientemente de dónde se ejecute el script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import Base

# Ruta del archivo SQLite en la raíz del proyecto
DATABASE_URL = "sqlite:///./kellytix.db"

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






