"""
Módulo: modelos/producto.py

Contiene la clase Producto, que representa cada producto del
restaurante (código, nombre, categoría, precio y stock disponible).
Aplica encapsulación mediante @property y @setter, valida sus propios
datos y sabe transformarse a/desde un diccionario compatible con JSON
mediante to_dict()/from_dict().

Producto no administra operaciones de venta ni actualiza su propio
stock por su cuenta: esas reglas se coordinan desde
RestauranteServicio, con apoyo de la clase Venta, que relaciona un
Producto con un Usuario para registrar una operación de venta.
"""


class Producto:
    """Representa un producto registrado en el restaurante."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        categoria: str,
        precio: float,
        stock: int = 0,
    ) -> None:
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.stock = stock

    # ------------------------------------------------------------------
    # Propiedad: codigo
    # ------------------------------------------------------------------
    @property
    def codigo(self) -> str:
        return self._codigo

    @codigo.setter
    def codigo(self, nuevo_codigo: str) -> None:
        if not nuevo_codigo or not nuevo_codigo.strip():
            raise ValueError("El código del producto no puede estar vacío.")
        self._codigo = nuevo_codigo.strip()

    # ------------------------------------------------------------------
    # Propiedad: nombre
    # ------------------------------------------------------------------
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, nuevo_nombre: str) -> None:
        if not nuevo_nombre or not nuevo_nombre.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        self._nombre = nuevo_nombre.strip()

    # ------------------------------------------------------------------
    # Propiedad: categoria
    # ------------------------------------------------------------------
    @property
    def categoria(self) -> str:
        return self._categoria

    @categoria.setter
    def categoria(self, nueva_categoria: str) -> None:
        if not nueva_categoria or not nueva_categoria.strip():
            raise ValueError("La categoría del producto no puede estar vacía.")
        self._categoria = nueva_categoria.strip()

    # ------------------------------------------------------------------
    # Propiedad: precio
    # ------------------------------------------------------------------
    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, nuevo_precio: float) -> None:
        if nuevo_precio <= 0:
            raise ValueError("El precio del producto debe ser mayor que cero.")
        self._precio = nuevo_precio

    # ------------------------------------------------------------------
    # Propiedad: stock
    # ------------------------------------------------------------------
    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, nuevo_stock: int) -> None:
        if nuevo_stock < 0:
            raise ValueError("El stock del producto no puede ser negativo.")
        self._stock = nuevo_stock

    def mostrar_informacion(self) -> str:
        """Devuelve una representación legible del producto, incluido su stock."""
        return (
            f"[{self.codigo}] {self.nombre} | Categoría: {self.categoria} "
            f"| Precio: ${self.precio:.2f} | Stock: {self.stock}"
        )

    # ------------------------------------------------------------------
    # Persistencia: conversión a/desde diccionario
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Convierte el producto a un diccionario listo para json.dump()."""
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio": self.precio,
            "stock": self.stock,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Producto":
        """
        Reconstruye un Producto a partir de un diccionario (uno de los
        registros crudos que ArchivoServicio lee desde productos.json).
        Si a 'datos' le falta alguna clave requerida, el acceso con
        datos["clave"] genera un KeyError; si algún valor no es válido,
        el propio constructor de Producto lo rechaza mediante ValueError
        a través de sus @setter. Ambas excepciones se controlan en quien
        llama a este método (RestauranteServicio), sin detener el
        programa.
        """
        return cls(
            codigo=datos["codigo"],
            nombre=datos["nombre"],
            categoria=datos["categoria"],
            precio=datos["precio"],
            stock=datos["stock"],
        )
