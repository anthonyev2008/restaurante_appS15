"""
Módulo: modelos/venta.py

Contiene la clase Venta, que representa el registro de una venta
sencilla del restaurante: relaciona a un usuario ya registrado en el
sistema con un producto ya registrado en el menú, e indica la
cantidad vendida, el precio unitario tomado en el momento de la
operación y la fecha en que se registró. El total se deriva siempre
de cantidad x precio_unitario mediante una propiedad de solo lectura,
para que nunca quede desincronizado de esos dos valores.

Venta no decide si el usuario o el producto indicados existen
realmente, ni calcula nada a partir de listas completas de productos o
usuarios: solo garantiza, mediante sus propios @setter, que sus datos
sean coherentes (identificador presente, cantidad entera mayor que
cero, precio unitario mayor que cero, fecha presente). Verificar que el
usuario y el producto existan, tomar el precio vigente del producto y
decidir cuándo se registra una venta es responsabilidad exclusiva de
RestauranteServicio, igual que ocurre con las reglas de Producto.
"""


class Venta:
    """Representa una venta registrada: un usuario, un producto, una cantidad y una fecha."""

    def __init__(
        self,
        identificador: str,
        usuario_identificacion: str,
        producto_codigo: str,
        cantidad: int,
        precio_unitario: float,
        fecha: str,
    ) -> None:
        self.identificador = identificador
        self.usuario_identificacion = usuario_identificacion
        self.producto_codigo = producto_codigo
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.fecha = fecha

    # ------------------------------------------------------------------
    # Propiedad: identificador
    # ------------------------------------------------------------------
    @property
    def identificador(self) -> str:
        return self._identificador

    @identificador.setter
    def identificador(self, nuevo_identificador: str) -> None:
        if not nuevo_identificador or not str(nuevo_identificador).strip():
            raise ValueError("El identificador de la venta no puede estar vacío.")
        self._identificador = str(nuevo_identificador).strip()

    # ------------------------------------------------------------------
    # Propiedad: usuario_identificacion (referencia a Usuario.identificacion)
    # ------------------------------------------------------------------
    @property
    def usuario_identificacion(self) -> str:
        return self._usuario_identificacion

    @usuario_identificacion.setter
    def usuario_identificacion(self, nueva_identificacion: str) -> None:
        if not nueva_identificacion or not str(nueva_identificacion).strip():
            raise ValueError("La venta debe indicar el usuario que la realiza.")
        self._usuario_identificacion = str(nueva_identificacion).strip()

    # ------------------------------------------------------------------
    # Propiedad: producto_codigo (referencia a Producto.codigo)
    # ------------------------------------------------------------------
    @property
    def producto_codigo(self) -> str:
        return self._producto_codigo

    @producto_codigo.setter
    def producto_codigo(self, nuevo_codigo: str) -> None:
        if not nuevo_codigo or not str(nuevo_codigo).strip():
            raise ValueError("La venta debe indicar el producto vendido.")
        self._producto_codigo = str(nuevo_codigo).strip()

    # ------------------------------------------------------------------
    # Propiedad: cantidad
    # ------------------------------------------------------------------
    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, nueva_cantidad: int) -> None:
        if int(nueva_cantidad) <= 0:
            raise ValueError("La cantidad vendida debe ser mayor que cero.")
        self._cantidad = int(nueva_cantidad)

    # ------------------------------------------------------------------
    # Propiedad: precio_unitario
    # ------------------------------------------------------------------
    @property
    def precio_unitario(self) -> float:
        return self._precio_unitario

    @precio_unitario.setter
    def precio_unitario(self, nuevo_precio: float) -> None:
        if float(nuevo_precio) <= 0:
            raise ValueError("El precio unitario de la venta debe ser mayor que cero.")
        self._precio_unitario = float(nuevo_precio)

    # ------------------------------------------------------------------
    # Propiedad: fecha
    # ------------------------------------------------------------------
    @property
    def fecha(self) -> str:
        return self._fecha

    @fecha.setter
    def fecha(self, nueva_fecha: str) -> None:
        if not nueva_fecha or not str(nueva_fecha).strip():
            raise ValueError("La fecha de la venta no puede estar vacía.")
        self._fecha = str(nueva_fecha).strip()

    # ------------------------------------------------------------------
    # Propiedad derivada: total (nunca se guarda por separado del cálculo)
    # ------------------------------------------------------------------
    @property
    def total(self) -> float:
        """Total de la venta, calculado siempre como cantidad x precio_unitario."""
        return round(self.cantidad * self.precio_unitario, 2)

    def mostrar_informacion(self) -> str:
        """Devuelve una representación legible de la venta."""
        return (
            f"[{self.identificador}] Usuario: {self.usuario_identificacion} | "
            f"Producto: {self.producto_codigo} | Cantidad: {self.cantidad} | "
            f"Total: ${self.total:.2f} | Fecha: {self.fecha}"
        )

    # ------------------------------------------------------------------
    # Persistencia: conversión a/desde diccionario
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Convierte la venta a un diccionario listo para json.dump().
        Incluye 'total' únicamente como dato informativo dentro del
        archivo: al reconstruir la venta con from_dict() ese valor no
        se lee, siempre se vuelve a calcular a partir de cantidad y
        precio_unitario.
        """
        return {
            "identificador": self.identificador,
            "usuario_identificacion": self.usuario_identificacion,
            "producto_codigo": self.producto_codigo,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "total": self.total,
            "fecha": self.fecha,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Venta":
        """
        Reconstruye una Venta a partir de un diccionario (uno de los
        registros crudos que ArchivoServicio lee desde ventas.json).
        Si a 'datos' le falta alguna clave requerida, el acceso con
        datos["clave"] genera un KeyError; si algún valor no es válido,
        el propio constructor de Venta lo rechaza mediante ValueError a
        través de sus @setter. Ambas excepciones se controlan en quien
        llama a este método (RestauranteServicio), sin detener el
        programa.
        """
        return cls(
            identificador=datos["identificador"],
            usuario_identificacion=datos["usuario_identificacion"],
            producto_codigo=datos["producto_codigo"],
            cantidad=datos["cantidad"],
            precio_unitario=datos["precio_unitario"],
            fecha=datos["fecha"],
        )
