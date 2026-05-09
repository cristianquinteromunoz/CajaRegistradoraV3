# ============================================================
#  database/conexion.py  —  Conexión y creación de la BD
# ============================================================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.modelos import Base

# Ruta del archivo SQLite
DATABASE_URL = "sqlite:///database/veterinaria.db"

# Motor de la base de datos
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # necesario para SQLite con tkinter
    echo=False  # True para ver las consultas SQL en consola (útil al desarrollar)
)

# Fábrica de sesiones
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def crear_tablas():
    """Crea todas las tablas en la BD si no existen."""
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente.")


def get_session() -> Session:
    """Devuelve una sesión lista para usar."""
    return SessionLocal()