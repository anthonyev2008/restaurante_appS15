"""
Módulo: modelos/usuario.py

Contiene la clase Usuario, que representa a una persona registrada en
el sistema del restaurante (identificación, nombre, correo y una
contraseña).

Se agrega el atributo contraseña, necesario para poder simular el
ingreso a la aplicación desde LoginView. Usuario no valida
credenciales por sí mismo ni sabe nada sobre la interfaz gráfica:
solo garantiza que sus propios datos sean válidos mediante sus
@setter. Decidir si un intento de acceso es correcto es
responsabilidad exclusiva de RestauranteServicio.
"""


class Usuario:
    """Representa a una persona registrada en el sistema del restaurante."""

    def __init__(self, identificacion: str, nombre: str, correo: str, contrasena: str) -> None:
        self.identificacion = identificacion
        self.nombre = nombre
        self.correo = correo
        self.contrasena = contrasena

    # ------------------------------------------------------------------
    # Propiedad: identificacion
    # ------------------------------------------------------------------
    @property
    def identificacion(self) -> str:
        return self._identificacion

    @identificacion.setter
    def identificacion(self, nueva_identificacion: str) -> None:
        if not nueva_identificacion or not nueva_identificacion.strip():
            raise ValueError("La identificación del usuario no puede estar vacía.")
        self._identificacion = nueva_identificacion.strip()

    # ------------------------------------------------------------------
    # Propiedad: nombre
    # ------------------------------------------------------------------
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, nuevo_nombre: str) -> None:
        if not nuevo_nombre or not nuevo_nombre.strip():
            raise ValueError("El nombre del usuario no puede estar vacío.")
        self._nombre = nuevo_nombre.strip()

    # ------------------------------------------------------------------
    # Propiedad: correo
    # ------------------------------------------------------------------
    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, nuevo_correo: str) -> None:
        if not nuevo_correo or "@" not in nuevo_correo:
            raise ValueError("El correo del usuario no es válido.")
        self._correo = nuevo_correo.strip()

    # ------------------------------------------------------------------
    # Propiedad: contrasena
    # ------------------------------------------------------------------
    @property
    def contrasena(self) -> str:
        return self._contrasena

    @contrasena.setter
    def contrasena(self, nueva_contrasena: str) -> None:
        if not nueva_contrasena or not nueva_contrasena.strip():
            raise ValueError("La contraseña del usuario no puede estar vacía.")
        self._contrasena = nueva_contrasena.strip()

    def mostrar_informacion(self) -> str:
        """Devuelve una representación legible del usuario, sin exponer la contraseña."""
        return f"[{self.identificacion}] {self.nombre} | Correo: {self.correo}"

    # ------------------------------------------------------------------
    # Persistencia: conversión a/desde diccionario
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Convierte el usuario a un diccionario listo para json.dump()."""
        return {
            "identificacion": self.identificacion,
            "nombre": self.nombre,
            "correo": self.correo,
            "contrasena": self.contrasena,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Usuario":
        """
        Reconstruye un Usuario a partir de un diccionario (uno de los
        registros crudos que ArchivoServicio lee desde usuarios.json).
        Una clave faltante produce KeyError y un valor inválido produce
        ValueError; ambas las controla quien llama a este método
        (RestauranteServicio).
        """
        return cls(
            identificacion=datos["identificacion"],
            nombre=datos["nombre"],
            correo=datos["correo"],
            contrasena=datos["contrasena"],
        )
