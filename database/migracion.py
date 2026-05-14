from database.conexion import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE productos ADD COLUMN fecha_vencimiento DATETIME"))
    conn.commit()