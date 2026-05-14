# ============================================================
#  servicios/reportes_service.py
# ============================================================
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from database.modelos import (
    Venta, DetalleVenta, Producto, Usuario,
    EstadoVenta, RegistroGasto, CuentaProveedor, Proveedor
)
from datetime import datetime, timedelta


class ReportesService:
    def __init__(self, session: Session):
        self.session = session

    # ----------------------------------------------------------
    # KPIs RÁPIDOS
    # ----------------------------------------------------------
    def kpis_hoy(self) -> dict:
        hoy   = datetime.now().date()
        ventas = (self.session.query(Venta)
                  .filter(func.date(Venta.fecha_venta) == hoy,
                          Venta.estado == EstadoVenta.completada).all())
        total      = sum(v.total for v in ventas)
        descuentos = sum(v.total_descuento for v in ventas)
        return {
            "total_hoy":        total,
            "num_ventas_hoy":   len(ventas),
            "descuentos_hoy":   descuentos,
            "ticket_promedio":  total / len(ventas) if ventas else 0,
        }

    def kpis_mes(self, año: int = None, mes: int = None) -> dict:
        now = datetime.now()
        año = año or now.year
        mes = mes or now.month
        ventas = (self.session.query(Venta)
                  .filter(extract("year",  Venta.fecha_venta) == año,
                          extract("month", Venta.fecha_venta) == mes,
                          Venta.estado == EstadoVenta.completada).all())
        total = sum(v.total for v in ventas)

        gastos = (self.session.query(func.sum(RegistroGasto.monto_pagado))
                  .filter(extract("year",  RegistroGasto.fecha_pago) == año,
                          extract("month", RegistroGasto.fecha_pago) == mes)
                  .scalar() or 0)
        return {
            "total_mes":      total,
            "num_ventas_mes": len(ventas),
            "gastos_mes":     gastos,
            "utilidad_mes":   total - gastos,
        }

    # ----------------------------------------------------------
    # VENTAS POR DÍA (últimos N días)
    # ----------------------------------------------------------
    def ventas_por_dia(self, dias: int = 30) -> list[dict]:
        desde = datetime.now() - timedelta(days=dias)
        rows  = (self.session.query(
                     func.date(Venta.fecha_venta).label("dia"),
                     func.sum(Venta.total).label("total"),
                     func.count(Venta.id_venta).label("cantidad"),
                 )
                 .filter(Venta.fecha_venta >= desde,
                         Venta.estado == EstadoVenta.completada)
                 .group_by(func.date(Venta.fecha_venta))
                 .order_by(func.date(Venta.fecha_venta))
                 .all())
        return [{"dia": str(r.dia), "total": r.total or 0, "cantidad": r.cantidad} for r in rows]

    # ----------------------------------------------------------
    # VENTAS POR MES (últimos N meses)
    # ----------------------------------------------------------
    def ventas_por_mes(self, meses: int = 6) -> list[dict]:
        rows = (self.session.query(
                    extract("year",  Venta.fecha_venta).label("año"),
                    extract("month", Venta.fecha_venta).label("mes"),
                    func.sum(Venta.total).label("total"),
                    func.count(Venta.id_venta).label("cantidad"),
                )
                .filter(Venta.estado == EstadoVenta.completada)
                .group_by("año", "mes")
                .order_by("año", "mes")
                .limit(meses)
                .all())
        meses_nombres = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        return [{"periodo": f"{meses_nombres[int(r.mes)-1]} {int(r.año)}",
                 "total": r.total or 0, "cantidad": r.cantidad} for r in rows]

    # ----------------------------------------------------------
    # HORAS PICO
    # ----------------------------------------------------------
    def horas_pico(self) -> list[dict]:
        rows = (self.session.query(
                    extract("hour", Venta.fecha_venta).label("hora"),
                    func.count(Venta.id_venta).label("cantidad"),
                    func.sum(Venta.total).label("total"),
                )
                .filter(Venta.estado == EstadoVenta.completada)
                .group_by("hora")
                .order_by("hora")
                .all())
        return [{"hora": f"{int(r.hora):02d}:00", "cantidad": r.cantidad,
                 "total": r.total or 0} for r in rows]

    # ----------------------------------------------------------
    # PRODUCTOS MÁS VENDIDOS
    # ----------------------------------------------------------
    def productos_mas_vendidos(self, limite: int = 10) -> list[dict]:
        rows = (self.session.query(
                    Producto.nombre,
                    func.sum(DetalleVenta.cantidad).label("total_vendido"),
                    func.sum(DetalleVenta.subtotal_linea).label("total_ingresos"),
                )
                .join(DetalleVenta, DetalleVenta.id_producto == Producto.id_producto)
                .join(Venta, Venta.id_venta == DetalleVenta.id_venta)
                .filter(Venta.estado == EstadoVenta.completada)
                .group_by(Producto.id_producto)
                .order_by(func.sum(DetalleVenta.subtotal_linea).desc())
                .limit(limite)
                .all())
        return [{"nombre": r.nombre, "cantidad": r.total_vendido or 0,
                 "ingresos": r.total_ingresos or 0} for r in rows]

    # ----------------------------------------------------------
    # COMPARATIVO PERÍODOS
    # ----------------------------------------------------------
    def comparativo_semanas(self) -> dict:
        hoy        = datetime.now()
        ini_esta   = hoy - timedelta(days=hoy.weekday())
        ini_ant    = ini_esta - timedelta(weeks=1)
        fin_ant    = ini_esta - timedelta(days=1)

        def total_periodo(desde, hasta):
            return (self.session.query(func.sum(Venta.total))
                    .filter(Venta.fecha_venta.between(desde, hasta),
                            Venta.estado == EstadoVenta.completada)
                    .scalar() or 0)

        esta   = total_periodo(ini_esta, hoy)
        antpas = total_periodo(ini_ant, fin_ant)
        cambio = ((esta - antpas) / antpas * 100) if antpas else 0
        return {"esta_semana": esta, "semana_anterior": antpas, "cambio_pct": cambio}

    # ----------------------------------------------------------
    # STOCK BAJO
    # ----------------------------------------------------------
    def productos_stock_bajo(self) -> list[Producto]:
        return (self.session.query(Producto)
                .filter(Producto.stock_actual <= Producto.stock_minimo,
                        Producto.activo == True)
                .order_by(Producto.stock_actual)
                .all())

    # ----------------------------------------------------------
    # GASTOS VS INGRESOS (últimos 6 meses)
    # ----------------------------------------------------------
    def gastos_vs_ingresos(self, meses: int = 6) -> list[dict]:
        meses_nombres = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        resultado = []
        now = datetime.now()
        for i in range(meses - 1, -1, -1):
            fecha  = now - timedelta(days=30 * i)
            año, m = fecha.year, fecha.month
            ingresos = (self.session.query(func.sum(Venta.total))
                        .filter(extract("year",  Venta.fecha_venta) == año,
                                extract("month", Venta.fecha_venta) == m,
                                Venta.estado == EstadoVenta.completada)
                        .scalar() or 0)
            gastos = (self.session.query(func.sum(RegistroGasto.monto_pagado))
                      .filter(extract("year",  RegistroGasto.fecha_pago) == año,
                              extract("month", RegistroGasto.fecha_pago) == m)
                      .scalar() or 0)
            resultado.append({
                "periodo":  f"{meses_nombres[m-1]} {año}",
                "ingresos": ingresos,
                "gastos":   gastos,
                "utilidad": ingresos - gastos,
            })
        return resultado

    # ----------------------------------------------------------
    # RENDIMIENTO POR EMPLEADO
    # ----------------------------------------------------------
    def rendimiento_empleados(self) -> list[dict]:
        rows = (self.session.query(
                    Usuario.nombre,
                    Usuario.apellido,
                    func.count(Venta.id_venta).label("num_ventas"),
                    func.sum(Venta.total).label("total_vendido"),
                    func.sum(Venta.total_descuento).label("total_descuentos"),
                )
                .join(Venta, Venta.id_usuario == Usuario.id_usuario)
                .filter(Venta.estado == EstadoVenta.completada)
                .group_by(Usuario.id_usuario)
                .order_by(func.sum(Venta.total).desc())
                .all())
        return [{"nombre":     f"{r.nombre} {r.apellido}",
                 "num_ventas": r.num_ventas,
                 "total":      r.total_vendido or 0,
                 "descuentos": r.total_descuentos or 0,
                 "ticket_prom": (r.total_vendido / r.num_ventas) if r.num_ventas else 0,
                 } for r in rows]

    # ----------------------------------------------------------
    # ESTADO CUENTA PROVEEDORES
    # ----------------------------------------------------------
    def estado_proveedores(self) -> list[dict]:
        proveedores = self.session.query(Proveedor).filter_by(activo=True).all()
        resultado   = []
        for p in proveedores:
            saldo = (self.session.query(func.sum(CuentaProveedor.monto))
                     .filter(CuentaProveedor.id_proveedor == p.id_proveedor,
                             CuentaProveedor.tipo == "debito")
                     .scalar() or 0) - \
                    (self.session.query(func.sum(CuentaProveedor.monto))
                     .filter(CuentaProveedor.id_proveedor == p.id_proveedor,
                             CuentaProveedor.tipo == "credito")
                     .scalar() or 0)
            if saldo != 0:
                resultado.append({"proveedor": p.nombre, "saldo": saldo})
        return sorted(resultado, key=lambda x: x["saldo"], reverse=True)