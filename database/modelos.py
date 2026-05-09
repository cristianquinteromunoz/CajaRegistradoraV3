# ============================================================
#  database/modelos.py  —  Definición de tablas con SQLAlchemy
# ============================================================
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import enum


# ------------------------------------------------------------
# BASE — todas las tablas heredan de aquí
# ------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# ============================================================
#  ENUMS
# ============================================================
class FrecuenciaGasto(enum.Enum):
    diario   = "diario"
    semanal  = "semanal"
    mensual  = "mensual"
    anual    = "anual"

class EstadoVenta(enum.Enum):
    completada = "completada"
    anulada    = "anulada"
    pendiente  = "pendiente"

class MetodoPago(enum.Enum):
    efectivo      = "efectivo"
    tarjeta       = "tarjeta"
    transferencia = "transferencia"


# ============================================================
#  MÓDULO PRODUCTOS
# ============================================================
class CategoriaProducto(Base):
    __tablename__ = "categorias_producto"

    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre       = Column(String(100), nullable=False, unique=True)
    descripcion  = Column(Text)

    productos = relationship("Producto", back_populates="categoria")


class Proveedor(Base):
    __tablename__ = "proveedores"

    id_proveedor = Column(Integer, primary_key=True, autoincrement=True)
    nombre       = Column(String(150), nullable=False)
    telefono     = Column(String(20))
    email        = Column(String(100))
    direccion    = Column(Text)
    activo       = Column(Boolean, default=True)

    productos = relationship("Producto", back_populates="proveedor")


class Producto(Base):
    __tablename__ = "productos"

    id_producto     = Column(Integer, primary_key=True, autoincrement=True)
    nombre          = Column(String(150), nullable=False)
    descripcion     = Column(Text)
    id_categoria    = Column(Integer, ForeignKey("categorias_producto.id_categoria"))
    id_proveedor    = Column(Integer, ForeignKey("proveedores.id_proveedor"))
    precio_compra   = Column(Float, nullable=False, default=0)
    stock_actual    = Column(Float, nullable=False, default=0)  # Float para fracciones
    stock_minimo    = Column(Float, default=0)
    unidad_medida   = Column(String(50))
    codigo_barras   = Column(String(100), unique=True, nullable=True)
    requiere_receta = Column(Boolean, default=False)
    activo          = Column(Boolean, default=True)
    fecha_creacion  = Column(DateTime, default=datetime.now)

    categoria      = relationship("CategoriaProducto", back_populates="productos")
    proveedor      = relationship("Proveedor",          back_populates="productos")
    presentaciones = relationship("ProductoPresentacion", back_populates="producto")
    detalles_venta = relationship("DetalleVenta",         back_populates="producto")


# ============================================================
#  MÓDULO SERVICIOS
# ============================================================
class CategoriaServicio(Base):
    __tablename__ = "categorias_servicio"

    id_categoria_servicio = Column(Integer, primary_key=True, autoincrement=True)
    nombre                = Column(String(100), nullable=False, unique=True)
    descripcion           = Column(Text)

    servicios = relationship("Servicio", back_populates="categoria")


class Servicio(Base):
    __tablename__ = "servicios"

    id_servicio           = Column(Integer, primary_key=True, autoincrement=True)
    nombre                = Column(String(150), nullable=False)
    descripcion           = Column(Text)
    id_categoria_servicio = Column(Integer, ForeignKey("categorias_servicio.id_categoria_servicio"))
    precio                = Column(Float, nullable=False)
    duracion_minutos      = Column(Integer)
    activo                = Column(Boolean, default=True)

    categoria = relationship("CategoriaServicio", back_populates="servicios")


# ============================================================
#  MÓDULO USUARIOS
# ============================================================
class Rol(Base):
    __tablename__ = "roles"

    id_rol      = Column(Integer, primary_key=True, autoincrement=True)
    nombre      = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text)

    usuarios        = relationship("Usuario",      back_populates="rol")
    roles_permisos  = relationship("RolPermiso",   back_populates="rol")


class Permiso(Base):
    __tablename__ = "permisos"

    id_permiso  = Column(Integer, primary_key=True, autoincrement=True)
    nombre      = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)

    roles_permisos = relationship("RolPermiso", back_populates="permiso")


class RolPermiso(Base):
    __tablename__ = "roles_permisos"

    id_rol     = Column(Integer, ForeignKey("roles.id_rol"),         primary_key=True)
    id_permiso = Column(Integer, ForeignKey("permisos.id_permiso"),  primary_key=True)

    rol     = relationship("Rol",     back_populates="roles_permisos")
    permiso = relationship("Permiso", back_populates="roles_permisos")


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario     = Column(Integer, primary_key=True, autoincrement=True)
    nombre         = Column(String(100), nullable=False)
    apellido       = Column(String(100), nullable=False)
    email          = Column(String(150), unique=True)
    username       = Column(String(50),  nullable=False, unique=True)
    password_hash  = Column(String(255), nullable=False)
    id_rol         = Column(Integer, ForeignKey("roles.id_rol"))
    activo         = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    ultimo_acceso  = Column(DateTime)

    rol    = relationship("Rol",   back_populates="usuarios")
    ventas = relationship("Venta", back_populates="usuario")
    registro_gastos = relationship("RegistroGasto", back_populates="usuario")


# ============================================================
#  MÓDULO GASTOS
# ============================================================
class CategoriaGasto(Base):
    __tablename__ = "categorias_gasto"

    id_categoria_gasto = Column(Integer, primary_key=True, autoincrement=True)
    nombre             = Column(String(100), nullable=False, unique=True)
    descripcion        = Column(Text)

    gastos = relationship("GastoFijo", back_populates="categoria")


class GastoFijo(Base):
    __tablename__ = "gastos_fijos"

    id_gasto           = Column(Integer, primary_key=True, autoincrement=True)
    nombre             = Column(String(150), nullable=False)
    descripcion        = Column(Text)
    id_categoria_gasto = Column(Integer, ForeignKey("categorias_gasto.id_categoria_gasto"))
    monto              = Column(Float, nullable=False)
    frecuencia         = Column(Enum(FrecuenciaGasto), default=FrecuenciaGasto.mensual)
    dia_cobro          = Column(Integer)  # día del mes, ej: 5
    activo             = Column(Boolean, default=True)

    categoria       = relationship("CategoriaGasto", back_populates="gastos")
    registro_gastos = relationship("RegistroGasto",  back_populates="gasto")


class RegistroGasto(Base):
    __tablename__ = "registro_gastos"

    id_registro   = Column(Integer, primary_key=True, autoincrement=True)
    id_gasto      = Column(Integer, ForeignKey("gastos_fijos.id_gasto"))
    id_usuario    = Column(Integer, ForeignKey("usuarios.id_usuario"))
    monto_pagado  = Column(Float, nullable=False)
    fecha_pago    = Column(DateTime, default=datetime.now)
    observaciones = Column(Text)

    gasto   = relationship("GastoFijo", back_populates="registro_gastos")
    usuario = relationship("Usuario",   back_populates="registro_gastos")


# ============================================================
#  MÓDULO VENTAS
# ============================================================
class TipoVenta(Base):
    __tablename__ = "tipos_venta"

    id_tipo_venta = Column(Integer, primary_key=True, autoincrement=True)
    nombre        = Column(String(50), nullable=False, unique=True)  # Unidad, Fracción, Blister
    descripcion   = Column(Text)

    presentaciones = relationship("ProductoPresentacion", back_populates="tipo_venta")
    detalles_venta = relationship("DetalleVenta",         back_populates="tipo_venta")


class ProductoPresentacion(Base):
    __tablename__ = "producto_presentaciones"

    id_presentacion          = Column(Integer, primary_key=True, autoincrement=True)
    id_producto              = Column(Integer, ForeignKey("productos.id_producto"))
    id_tipo_venta            = Column(Integer, ForeignKey("tipos_venta.id_tipo_venta"))
    cantidad_por_presentacion = Column(Float, nullable=False, default=1)  # 1 blister = 10 unidades
    precio_venta             = Column(Float, nullable=False)
    precio_con_descuento     = Column(Float)
    porcentaje_descuento     = Column(Float, default=0)
    activo                   = Column(Boolean, default=True)

    producto   = relationship("Producto",  back_populates="presentaciones")
    tipo_venta = relationship("TipoVenta", back_populates="presentaciones")


class Venta(Base):
    __tablename__ = "ventas"

    id_venta        = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario      = Column(Integer, ForeignKey("usuarios.id_usuario"))
    fecha_venta     = Column(DateTime, default=datetime.now)
    subtotal        = Column(Float, nullable=False, default=0)
    total_descuento = Column(Float, default=0)
    total           = Column(Float, nullable=False, default=0)
    metodo_pago     = Column(Enum(MetodoPago), default=MetodoPago.efectivo)
    estado          = Column(Enum(EstadoVenta), default=EstadoVenta.completada)
    observaciones   = Column(Text)

    usuario  = relationship("Usuario",      back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta")


class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id_detalle           = Column(Integer, primary_key=True, autoincrement=True)
    id_venta             = Column(Integer, ForeignKey("ventas.id_venta"))
    id_producto          = Column(Integer, ForeignKey("productos.id_producto"))
    id_tipo_venta        = Column(Integer, ForeignKey("tipos_venta.id_tipo_venta"))
    cantidad             = Column(Float, nullable=False)
    precio_unitario      = Column(Float, nullable=False)  # precio al momento de la venta
    descuento_aplicado   = Column(Boolean, default=False)
    porcentaje_descuento = Column(Float, default=0)
    precio_con_descuento = Column(Float)
    subtotal_linea       = Column(Float, nullable=False)

    venta      = relationship("Venta",     back_populates="detalles")
    producto   = relationship("Producto",  back_populates="detalles_venta")
    tipo_venta = relationship("TipoVenta", back_populates="detalles_venta")