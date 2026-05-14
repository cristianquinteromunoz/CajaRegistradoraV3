import hashlib
from database.conexion import crear_tablas, get_session
from database.modelos import (
    Rol, Permiso, RolPermiso, Usuario,
    CategoriaProducto, CategoriaServicio,
    CategoriaGasto, TipoVenta
)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def inicializar():
    # 1. Crear tablas
    crear_tablas()

    session = get_session()

    try:
        # Solo insertar si la BD está vacía
        if session.query(Rol).count() > 0:
            print("ℹ️  La base de datos ya tiene datos.")
            return

        # ── Roles ─────────────────────────────────────────────
        roles = [
            Rol(nombre="Administrador", descripcion="Acceso total al sistema"),
            Rol(nombre="Cajero",        descripcion="Gestión de ventas y caja"),
            Rol(nombre="Veterinario",   descripcion="Gestión de servicios y pacientes"),
        ]
        session.add_all(roles)
        session.flush()  # para obtener los IDs

        # ── Permisos ──────────────────────────────────────────
        permisos = [
            Permiso(nombre="ver_productos",    descripcion="Ver lista de productos"),
            Permiso(nombre="editar_productos", descripcion="Crear y editar productos"),
            Permiso(nombre="ver_ventas",       descripcion="Ver historial de ventas"),
            Permiso(nombre="realizar_ventas",  descripcion="Registrar nuevas ventas"),
            Permiso(nombre="ver_reportes",     descripcion="Acceder a reportes"),
            Permiso(nombre="gestionar_usuarios", descripcion="Crear y editar usuarios"),
            Permiso(nombre="gestionar_gastos", descripcion="Registrar gastos fijos"),
        ]
        session.add_all(permisos)
        session.flush()

        # ── Roles ↔ Permisos ──────────────────────────────────
        admin = roles[0]
        cajero = roles[1]

        # Administrador tiene todos los permisos
        for p in permisos:
            session.add(RolPermiso(id_rol=admin.id_rol, id_permiso=p.id_permiso))

        # Cajero solo puede vender y ver productos
        permisos_cajero = ["ver_productos", "ver_ventas", "realizar_ventas"]
        for p in permisos:
            if p.nombre in permisos_cajero:
                session.add(RolPermiso(id_rol=cajero.id_rol, id_permiso=p.id_permiso))

        # ── Usuario administrador por defecto ─────────────────
        admin_user = Usuario(
            nombre        = "Admin",
            apellido      = "Principal",
            email         = "admin@veterinaria.com",
            username      = "admin",
            password_hash = hash_password("admin123"),  # ← cambia esto en producción
            id_rol        = admin.id_rol,
        )
        session.add(admin_user)

        # ── Categorías de productos ───────────────────────────
        categorias_prod = [
            CategoriaProducto(nombre="Medicamentos",  descripcion="Fármacos y medicamentos veterinarios"),
            CategoriaProducto(nombre="Alimentos",     descripcion="Concentrados y suplementos"),
            CategoriaProducto(nombre="Accesorios",    descripcion="Correas, camas, juguetes"),
            CategoriaProducto(nombre="Higiene",       descripcion="Shampoo, cepillos, desparasitantes"),
            CategoriaProducto(nombre="Vacunas",       descripcion="Vacunas y biológicos"),
        ]
        session.add_all(categorias_prod)

        # ── Categorías de servicios ───────────────────────────
        categorias_serv = [
            CategoriaServicio(nombre="Consulta",    descripcion="Consultas médicas generales"),
            CategoriaServicio(nombre="Cirugía",     descripcion="Procedimientos quirúrgicos"),
            CategoriaServicio(nombre="Estética",    descripcion="Baño, corte y peluquería"),
            CategoriaServicio(nombre="Vacunación",  descripcion="Aplicación de vacunas"),
            CategoriaServicio(nombre="Laboratorio", descripcion="Exámenes y análisis clínicos"),
        ]
        session.add_all(categorias_serv)

        # ── Categorías de gastos ──────────────────────────────
        categorias_gasto = [
            CategoriaGasto(nombre="Arriendo",          descripcion="Pago de arriendo del local"),
            CategoriaGasto(nombre="Servicios públicos", descripcion="Agua, luz, internet"),
            CategoriaGasto(nombre="Nómina",            descripcion="Pago de empleados"),
            CategoriaGasto(nombre="Insumos",           descripcion="Materiales y suministros"),
        ]
        session.add_all(categorias_gasto)

        # ── Tipos de venta ────────────────────────────────────
        tipos_venta = [
            TipoVenta(nombre="Unidad",   descripcion="Venta por unidad completa"),
            TipoVenta(nombre="Fracción", descripcion="Venta por unidad fraccionada"),
            TipoVenta(nombre="Blister",  descripcion="Venta por blister"),
            TipoVenta(nombre="Caja",     descripcion="Venta por caja completa"),
        ]
        session.add_all(tipos_venta)

        session.commit()
        print("✅ Datos iniciales insertados correctamente.")
        print("👤 Usuario admin creado — user: admin / pass: admin123")

    except Exception as e:
        session.rollback()
        print(f"❌ Error al inicializar: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    inicializar()