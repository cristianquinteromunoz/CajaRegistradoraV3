# ============================================================
#  servicios/personal_service.py
# ============================================================
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.modelos import Usuario, Turno, Nomina
from datetime import datetime


class PersonalService:
    def __init__(self, session: Session):
        self.session = session

    # ----------------------------------------------------------
    # USUARIOS / EMPLEADOS
    # ----------------------------------------------------------
    def obtener_todos(self, solo_activos=True) -> list[Usuario]:
        q = self.session.query(Usuario)
        if solo_activos:
            q = q.filter(Usuario.activo == True)
        return q.all()

    def obtener_por_id(self, id_usuario: int) -> Usuario | None:
        return self.session.query(Usuario).filter_by(id_usuario=id_usuario).first()

    def buscar(self, texto: str) -> list[Usuario]:
        return (
            self.session.query(Usuario)
            .filter(
                (Usuario.nombre.ilike(f"%{texto}%") |
                 Usuario.apellido.ilike(f"%{texto}%") |
                 Usuario.username.ilike(f"%{texto}%")),
                Usuario.activo == True
            ).all()
        )

    # ----------------------------------------------------------
    # TURNOS
    # ----------------------------------------------------------
    def obtener_turnos(self, id_usuario: int) -> list[Turno]:
        return (
            self.session.query(Turno)
            .filter_by(id_usuario=id_usuario)
            .all()
        )

    def guardar_turnos(self, id_usuario: int, turnos: list[dict]):
        """Reemplaza todos los turnos del usuario."""
        self.session.query(Turno).filter_by(id_usuario=id_usuario).delete()
        for t in turnos:
            self.session.add(Turno(
                id_usuario  = id_usuario,
                dia_semana  = t["dia_semana"],
                hora_inicio = t["hora_inicio"],
                hora_fin    = t["hora_fin"],
            ))
        self.session.commit()

    # ----------------------------------------------------------
    # NÓMINA
    # ----------------------------------------------------------
    def obtener_nomina(self, id_usuario: int) -> list[Nomina]:
        return (
            self.session.query(Nomina)
            .filter_by(id_usuario=id_usuario)
            .order_by(Nomina.fecha_pago.desc())
            .all()
        )

    def registrar_pago_nomina(self, datos: dict) -> Nomina:
        total = datos["salario_base"] + datos.get("bonificacion", 0) - datos.get("deducciones", 0)
        nomina = Nomina(
            id_usuario    = datos["id_usuario"],
            salario_base  = datos["salario_base"],
            bonificacion  = datos.get("bonificacion", 0),
            deducciones   = datos.get("deducciones", 0),
            total_pago    = total,
            periodo       = datos["periodo"],
            observaciones = datos.get("observaciones", ""),
        )
        self.session.add(nomina)
        self.session.commit()
        self.session.refresh(nomina)
        return nomina

    def historial_accesos(self, id_usuario: int) -> Usuario | None:
        return self.obtener_por_id(id_usuario)