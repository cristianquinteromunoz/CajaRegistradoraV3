# ============================================================
#  servicios/usuarios_service.py
# ============================================================
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from database.modelos import Usuario, Rol, Permiso, RolPermiso


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class UsuariosService:
    def __init__(self, session: Session):
        self.session = session

    # ----------------------------------------------------------
    # AUTENTICACIÓN
    # ----------------------------------------------------------
    def login(self, username: str, password: str) -> Usuario | None:
        usuario = (
            self.session.query(Usuario)
            .filter_by(username=username, activo=True)
            .first()
        )
        if usuario and usuario.password_hash == _hash(password):
            usuario.ultimo_acceso = datetime.now()
            self.session.commit()
            return usuario
        return None

    def tiene_permiso(self, id_usuario: int, nombre_permiso: str) -> bool:
        usuario = self.obtener_por_id(id_usuario)
        if not usuario:
            return False
        permisos = [rp.permiso.nombre for rp in usuario.rol.roles_permisos]
        return nombre_permiso in permisos

    # ----------------------------------------------------------
    # CRUD USUARIOS
    # ----------------------------------------------------------
    def obtener_todos(self, solo_activos=True) -> list[Usuario]:
        q = self.session.query(Usuario)
        if solo_activos:
            q = q.filter(Usuario.activo == True)
        return q.all()

    def obtener_por_id(self, id_usuario: int) -> Usuario | None:
        return self.session.query(Usuario).filter_by(id_usuario=id_usuario).first()

    def crear(self, datos: dict) -> Usuario | None:
        """
        datos debe incluir: nombre, apellido, username, password, id_rol
        """
        if self.session.query(Usuario).filter_by(username=datos["username"]).first():
            print("❌ El username ya existe.")
            return None
        try:
            usuario = Usuario(
                nombre        = datos["nombre"],
                apellido      = datos["apellido"],
                email         = datos.get("email"),
                username      = datos["username"],
                password_hash = _hash(datos["password"]),
                id_rol        = datos["id_rol"],
            )
            self.session.add(usuario)
            self.session.commit()
            self.session.refresh(usuario)
            return usuario
        except Exception as e:
            self.session.rollback()
            print(f"❌ Error al crear usuario: {e}")
            return None

    def actualizar(self, id_usuario: int, datos: dict) -> Usuario | None:
        usuario = self.obtener_por_id(id_usuario)
        if not usuario:
            return None
        campos_permitidos = {"nombre", "apellido", "email", "id_rol", "activo"}
        for campo, valor in datos.items():
            if campo in campos_permitidos:
                setattr(usuario, campo, valor)
        self.session.commit()
        return usuario

    def cambiar_password(self, id_usuario: int, password_nueva: str) -> bool:
        usuario = self.obtener_por_id(id_usuario)
        if not usuario:
            return False
        usuario.password_hash = _hash(password_nueva)
        self.session.commit()
        return True

    def desactivar(self, id_usuario: int) -> bool:
        usuario = self.obtener_por_id(id_usuario)
        if not usuario:
            return False
        usuario.activo = False
        self.session.commit()
        return True

    # ----------------------------------------------------------
    # ROLES Y PERMISOS
    # ----------------------------------------------------------
    def obtener_roles(self) -> list[Rol]:
        return self.session.query(Rol).all()

    def obtener_permisos(self) -> list[Permiso]:
        return self.session.query(Permiso).all()

    def crear_rol(self, nombre: str, descripcion: str = "") -> Rol:
        rol = Rol(nombre=nombre, descripcion=descripcion)
        self.session.add(rol)
        self.session.commit()
        return rol

    def asignar_permiso(self, id_rol: int, id_permiso: int) -> bool:
        existe = self.session.query(RolPermiso).filter_by(
            id_rol=id_rol, id_permiso=id_permiso
        ).first()
        if existe:
            return False
        self.session.add(RolPermiso(id_rol=id_rol, id_permiso=id_permiso))
        self.session.commit()
        return True

    def quitar_permiso(self, id_rol: int, id_permiso: int) -> bool:
        rp = self.session.query(RolPermiso).filter_by(
            id_rol=id_rol, id_permiso=id_permiso
        ).first()
        if not rp:
            return False
        self.session.delete(rp)
        self.session.commit()
        return True