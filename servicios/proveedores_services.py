# ============================================================
#  servicios/proveedores_service.py
# ============================================================
from sqlalchemy.orm import Session
from database.modelos import Proveedor, OrdenCompra, DetalleOrden, CuentaProveedor, Producto


class ProveedoresService:
    def __init__(self, session: Session):
        self.session = session

    # ----------------------------------------------------------
    # PROVEEDORES
    # ----------------------------------------------------------
    def obtener_todos(self, solo_activos=True) -> list[Proveedor]:
        q = self.session.query(Proveedor)
        if solo_activos:
            q = q.filter(Proveedor.activo == True)
        return q.all()

    def obtener_por_id(self, id_proveedor: int) -> Proveedor | None:
        return self.session.query(Proveedor).filter_by(id_proveedor=id_proveedor).first()

    def buscar(self, texto: str) -> list[Proveedor]:
        return (
            self.session.query(Proveedor)
            .filter(Proveedor.nombre.ilike(f"%{texto}%"), Proveedor.activo == True)
            .all()
        )

    def crear(self, datos: dict) -> Proveedor:
        p = Proveedor(**datos)
        self.session.add(p)
        self.session.commit()
        self.session.refresh(p)
        return p

    def actualizar(self, id_proveedor: int, datos: dict) -> Proveedor | None:
        p = self.obtener_por_id(id_proveedor)
        if not p:
            return None
        for k, v in datos.items():
            setattr(p, k, v)
        self.session.commit()
        return p

    def desactivar(self, id_proveedor: int) -> bool:
        p = self.obtener_por_id(id_proveedor)
        if not p:
            return False
        p.activo = False
        self.session.commit()
        return True

    def productos_del_proveedor(self, id_proveedor: int) -> list[Producto]:
        return (
            self.session.query(Producto)
            .filter_by(id_proveedor=id_proveedor, activo=True)
            .all()
        )

    # ----------------------------------------------------------
    # ÓRDENES DE COMPRA
    # ----------------------------------------------------------
    def obtener_ordenes(self, id_proveedor: int) -> list[OrdenCompra]:
        return (
            self.session.query(OrdenCompra)
            .filter_by(id_proveedor=id_proveedor)
            .order_by(OrdenCompra.fecha_orden.desc())
            .all()
        )

    def crear_orden(self, id_proveedor: int, id_usuario: int,
                    items: list[dict], observaciones: str = "") -> OrdenCompra:
        total = sum(i["cantidad"] * i["precio_unit"] for i in items)
        orden = OrdenCompra(
            id_proveedor  = id_proveedor,
            id_usuario    = id_usuario,
            total         = total,
            observaciones = observaciones,
        )
        self.session.add(orden)
        self.session.flush()
        for i in items:
            self.session.add(DetalleOrden(
                id_orden    = orden.id_orden,
                id_producto = i["id_producto"],
                cantidad    = i["cantidad"],
                precio_unit = i["precio_unit"],
                subtotal    = i["cantidad"] * i["precio_unit"],
            ))
        self.session.commit()
        self.session.refresh(orden)
        return orden

    def cambiar_estado_orden(self, id_orden: int, estado: str) -> bool:
        orden = self.session.query(OrdenCompra).filter_by(id_orden=id_orden).first()
        if not orden:
            return False
        orden.estado = estado
        # Si se recibe la orden, actualizar stock
        if estado == "recibida":
            for d in orden.detalles:
                if d.producto:
                    d.producto.stock_actual += d.cantidad
        self.session.commit()
        return True

    # ----------------------------------------------------------
    # CUENTA / SALDO
    # ----------------------------------------------------------
    def saldo_proveedor(self, id_proveedor: int) -> float:
        movimientos = (
            self.session.query(CuentaProveedor)
            .filter_by(id_proveedor=id_proveedor)
            .all()
        )
        return sum(
            m.monto if m.tipo == "debito" else -m.monto
            for m in movimientos
        )

    def registrar_movimiento(self, id_proveedor: int, concepto: str,
                             monto: float, tipo: str) -> CuentaProveedor:
        saldo_actual = self.saldo_proveedor(id_proveedor)
        nuevo_saldo  = saldo_actual + monto if tipo == "debito" else saldo_actual - monto
        mov = CuentaProveedor(
            id_proveedor = id_proveedor,
            concepto     = concepto,
            monto        = monto,
            tipo         = tipo,
            saldo        = nuevo_saldo,
        )
        self.session.add(mov)
        self.session.commit()
        return mov

    def historial_cuenta(self, id_proveedor: int) -> list[CuentaProveedor]:
        return (
            self.session.query(CuentaProveedor)
            .filter_by(id_proveedor=id_proveedor)
            .order_by(CuentaProveedor.fecha.desc())
            .all()
        )