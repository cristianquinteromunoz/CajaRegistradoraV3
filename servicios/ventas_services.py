# ============================================================
#  servicios/ventas_service.py
# ============================================================
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.modelos import Venta, DetalleVenta, EstadoVenta, ProductoPresentacion
from datetime import datetime


class VentasService:
    def __init__(self, session: Session):
        self.session = session

    # ----------------------------------------------------------
    # CREAR VENTA
    # ----------------------------------------------------------
    def crear_venta(self, id_usuario: int, items: list[dict], metodo_pago: str = "efectivo") -> Venta | None:
        """
        items es una lista de diccionarios con esta estructura:
        {
            "id_producto":          1,
            "id_tipo_venta":        2,
            "cantidad":             3,
            "precio_unitario":      7500.0,
            "descuento_aplicado":   True,
            "porcentaje_descuento": 10.0,
            "precio_con_descuento": 6750.0,
        }
        """
        try:
            subtotal        = 0.0
            total_descuento = 0.0
            detalles        = []

            for item in items:
                precio_base = item["precio_unitario"]
                cantidad    = item["cantidad"]

                if item.get("descuento_aplicado") and item.get("precio_con_descuento"):
                    precio_final    = item["precio_con_descuento"]
                    descuento_linea = (precio_base - precio_final) * cantidad
                else:
                    precio_final    = precio_base
                    descuento_linea = 0.0

                subtotal_linea   = precio_final * cantidad
                subtotal        += precio_base * cantidad
                total_descuento += descuento_linea

                detalles.append(DetalleVenta(
                    id_producto          = item["id_producto"],
                    id_tipo_venta        = item["id_tipo_venta"],
                    cantidad             = cantidad,
                    precio_unitario      = precio_base,
                    descuento_aplicado   = item.get("descuento_aplicado", False),
                    porcentaje_descuento = item.get("porcentaje_descuento", 0),
                    precio_con_descuento = item.get("precio_con_descuento"),
                    subtotal_linea       = subtotal_linea,
                ))

            venta = Venta(
                id_usuario      = id_usuario,
                subtotal        = subtotal,
                total_descuento = total_descuento,
                total           = subtotal - total_descuento,
                metodo_pago     = metodo_pago,
                estado          = EstadoVenta.completada,
            )
            self.session.add(venta)
            self.session.flush()  # obtener id_venta antes del commit

            for d in detalles:
                d.id_venta = venta.id_venta
                self.session.add(d)

            # Descontar stock
            self._descontar_stock(items)

            self.session.commit()
            self.session.refresh(venta)
            return venta

        except Exception as e:
            self.session.rollback()
            print(f"❌ Error al crear venta: {e}")
            return None

    def _descontar_stock(self, items: list[dict]):
        """Descuenta el stock según la presentación vendida."""
        for item in items:
            presentacion = (
                self.session.query(ProductoPresentacion)
                .filter_by(
                    id_producto=item["id_producto"],
                    id_tipo_venta=item["id_tipo_venta"],
                    activo=True
                ).first()
            )
            if presentacion:
                unidades = item["cantidad"] * presentacion.cantidad_por_presentacion
                producto = presentacion.producto
                producto.stock_actual = max(0, producto.stock_actual - unidades)

    # ----------------------------------------------------------
    # ANULAR VENTA
    # ----------------------------------------------------------
    def anular_venta(self, id_venta: int) -> bool:
        """Anula la venta y devuelve el stock."""
        venta = self.obtener_por_id(id_venta)
        if not venta or venta.estado == EstadoVenta.anulada:
            return False
        try:
            venta.estado = EstadoVenta.anulada
            for detalle in venta.detalles:
                presentacion = (
                    self.session.query(ProductoPresentacion)
                    .filter_by(
                        id_producto=detalle.id_producto,
                        id_tipo_venta=detalle.id_tipo_venta,
                        activo=True
                    ).first()
                )
                if presentacion:
                    unidades = detalle.cantidad * presentacion.cantidad_por_presentacion
                    detalle.producto.stock_actual += unidades

            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"❌ Error al anular venta: {e}")
            return False

    # ----------------------------------------------------------
    # CONSULTAS
    # ----------------------------------------------------------
    def obtener_por_id(self, id_venta: int) -> Venta | None:
        return self.session.query(Venta).filter_by(id_venta=id_venta).first()

    def obtener_todas(self) -> list[Venta]:
        return self.session.query(Venta).order_by(Venta.fecha_venta.desc()).all()

    def ventas_por_fecha(self, desde: datetime, hasta: datetime) -> list[Venta]:
        return (
            self.session.query(Venta)
            .filter(Venta.fecha_venta.between(desde, hasta))
            .order_by(Venta.fecha_venta.desc())
            .all()
        )

    def ventas_de_hoy(self) -> list[Venta]:
        hoy = datetime.now().date()
        return (
            self.session.query(Venta)
            .filter(func.date(Venta.fecha_venta) == hoy)
            .all()
        )

    # ----------------------------------------------------------
    # TOTALES / REPORTES
    # ----------------------------------------------------------
    def total_vendido_hoy(self) -> float:
        ventas = self.ventas_de_hoy()
        return sum(v.total for v in ventas if v.estado == EstadoVenta.completada)

    def total_vendido_periodo(self, desde: datetime, hasta: datetime) -> float:
        ventas = self.ventas_por_fecha(desde, hasta)
        return sum(v.total for v in ventas if v.estado == EstadoVenta.completada)