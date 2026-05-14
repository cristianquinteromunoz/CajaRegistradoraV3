# ============================================================
#  servicios/productos_service.py
# ============================================================
from sqlalchemy.orm import Session
from database.modelos import Producto, ProductoPresentacion, CategoriaProducto, Proveedor


class ProductosService:
    def __init__(self, session: Session):
        self.session = session

    # ----------------------------------------------------------
    # PRODUCTOS
    # ----------------------------------------------------------
    def obtener_todos(self, solo_activos=True) -> list[Producto]:
        q = self.session.query(Producto)
        if solo_activos:
            q = q.filter(Producto.activo == True)
        return q.all()

    def obtener_por_id(self, id_producto: int) -> Producto | None:
        return self.session.query(Producto).filter_by(id_producto=id_producto).first()

    def buscar(self, texto: str) -> list[Producto]:
        return (
            self.session.query(Producto)
            .filter(
                (Producto.nombre.ilike(f"%{texto}%") |
                 Producto.codigo_barras.ilike(f"%{texto}%")),
                Producto.activo == True
            )
            .all()
        )

    def obtener_por_codigo_barras(self, codigo: str) -> Producto | None:
        return (
            self.session.query(Producto)
            .filter_by(codigo_barras=codigo, activo=True)
            .first()
        )

    def crear(self, datos: dict) -> Producto:
        producto = Producto(**datos)
        self.session.add(producto)
        self.session.commit()
        self.session.refresh(producto)
        return producto

    def actualizar(self, id_producto: int, datos: dict) -> Producto | None:
        producto = self.obtener_por_id(id_producto)
        if not producto:
            return None
        for campo, valor in datos.items():
            setattr(producto, campo, valor)
        self.session.commit()
        self.session.refresh(producto)
        return producto

    def eliminar(self, id_producto: int) -> bool:
        """Borrado lógico — solo desactiva el producto."""
        producto = self.obtener_por_id(id_producto)
        if not producto:
            return False
        producto.activo = False
        self.session.commit()
        return True

    def productos_bajo_stock(self) -> list[Producto]:
        """Productos cuyo stock_actual <= stock_minimo."""
        return (
            self.session.query(Producto)
            .filter(Producto.stock_actual <= Producto.stock_minimo, Producto.activo == True)
            .all()
        )

    def productos_proximos_vencer(self, dias: int = 30) -> list[Producto]:
        """Productos que vencen en los próximos N días."""
        from datetime import datetime, timedelta
        limite = datetime.now() + timedelta(days=dias)
        return (
            self.session.query(Producto)
            .filter(
                Producto.fecha_vencimiento != None,
                Producto.fecha_vencimiento <= limite,
                Producto.activo == True,
            )
            .order_by(Producto.fecha_vencimiento)
            .all()
        )

    def descontar_stock(self, id_producto: int, cantidad: float) -> bool:
        producto = self.obtener_por_id(id_producto)
        if not producto or producto.stock_actual < cantidad:
            return False
        producto.stock_actual -= cantidad
        self.session.commit()
        return True

    # ----------------------------------------------------------
    # PRESENTACIONES
    # ----------------------------------------------------------
    def obtener_presentaciones(self, id_producto: int) -> list[ProductoPresentacion]:
        return (
            self.session.query(ProductoPresentacion)
            .filter_by(id_producto=id_producto, activo=True)
            .all()
        )

    def crear_presentacion(self, datos: dict) -> ProductoPresentacion:
        presentacion = ProductoPresentacion(**datos)
        self.session.add(presentacion)
        self.session.commit()
        self.session.refresh(presentacion)
        return presentacion

    def actualizar_presentacion(self, id_presentacion: int, datos: dict) -> ProductoPresentacion | None:
        p = self.session.query(ProductoPresentacion).filter_by(id_presentacion=id_presentacion).first()
        if not p:
            return None
        for campo, valor in datos.items():
            setattr(p, campo, valor)
        self.session.commit()
        return p

    # ----------------------------------------------------------
    # CATEGORÍAS
    # ----------------------------------------------------------
    def obtener_categorias(self) -> list[CategoriaProducto]:
        return self.session.query(CategoriaProducto).all()

    def crear_categoria(self, nombre: str, descripcion: str = "") -> CategoriaProducto:
        cat = CategoriaProducto(nombre=nombre, descripcion=descripcion)
        self.session.add(cat)
        self.session.commit()
        return cat

    # ----------------------------------------------------------
    # PROVEEDORES
    # ----------------------------------------------------------
    def obtener_proveedores(self, solo_activos=True) -> list[Proveedor]:
        q = self.session.query(Proveedor)
        if solo_activos:
            q = q.filter(Proveedor.activo == True)
        return q.all()

    def crear_proveedor(self, datos: dict) -> Proveedor:
        proveedor = Proveedor(**datos)
        self.session.add(proveedor)
        self.session.commit()
        return proveedor