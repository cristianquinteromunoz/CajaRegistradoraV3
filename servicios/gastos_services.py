# ============================================================
#  servicios/gastos_service.py
# ============================================================
from datetime import datetime
from sqlalchemy.orm import Session
from database.modelos import GastoFijo, RegistroGasto, CategoriaGasto


class GastosService:
    def __init__(self, session: Session):
        self.session = session

    # ----------------------------------------------------------
    # GASTOS FIJOS
    # ----------------------------------------------------------
    def obtener_todos(self, solo_activos=True) -> list[GastoFijo]:
        q = self.session.query(GastoFijo)
        if solo_activos:
            q = q.filter(GastoFijo.activo == True)
        return q.all()

    def obtener_por_id(self, id_gasto: int) -> GastoFijo | None:
        return self.session.query(GastoFijo).filter_by(id_gasto=id_gasto).first()

    def crear(self, datos: dict) -> GastoFijo:
        gasto = GastoFijo(**datos)
        self.session.add(gasto)
        self.session.commit()
        self.session.refresh(gasto)
        return gasto

    def actualizar(self, id_gasto: int, datos: dict) -> GastoFijo | None:
        gasto = self.obtener_por_id(id_gasto)
        if not gasto:
            return None
        for campo, valor in datos.items():
            setattr(gasto, campo, valor)
        self.session.commit()
        return gasto

    def desactivar(self, id_gasto: int) -> bool:
        gasto = self.obtener_por_id(id_gasto)
        if not gasto:
            return False
        gasto.activo = False
        self.session.commit()
        return True

    # ----------------------------------------------------------
    # REGISTRO DE PAGOS
    # ----------------------------------------------------------
    def registrar_pago(self, id_gasto: int, id_usuario: int, monto: float, observaciones: str = "") -> RegistroGasto:
        registro = RegistroGasto(
            id_gasto      = id_gasto,
            id_usuario    = id_usuario,
            monto_pagado  = monto,
            fecha_pago    = datetime.now(),
            observaciones = observaciones,
        )
        self.session.add(registro)
        self.session.commit()
        self.session.refresh(registro)
        return registro

    def historial_pagos(self, id_gasto: int) -> list[RegistroGasto]:
        return (
            self.session.query(RegistroGasto)
            .filter_by(id_gasto=id_gasto)
            .order_by(RegistroGasto.fecha_pago.desc())
            .all()
        )

    def pagos_por_periodo(self, desde: datetime, hasta: datetime) -> list[RegistroGasto]:
        return (
            self.session.query(RegistroGasto)
            .filter(RegistroGasto.fecha_pago.between(desde, hasta))
            .order_by(RegistroGasto.fecha_pago.desc())
            .all()
        )

    def total_gastos_mes(self, año: int, mes: int) -> float:
        desde = datetime(año, mes, 1)
        hasta = datetime(año, mes + 1, 1) if mes < 12 else datetime(año + 1, 1, 1)
        registros = self.pagos_por_periodo(desde, hasta)
        return sum(r.monto_pagado for r in registros)

    # ----------------------------------------------------------
    # CATEGORÍAS
    # ----------------------------------------------------------
    def obtener_categorias(self) -> list[CategoriaGasto]:
        return self.session.query(CategoriaGasto).all()

    def crear_categoria(self, nombre: str, descripcion: str = "") -> CategoriaGasto:
        cat = CategoriaGasto(nombre=nombre, descripcion=descripcion)
        self.session.add(cat)
        self.session.commit()
        return cat