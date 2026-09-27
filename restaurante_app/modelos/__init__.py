"""
Paquete modelos.

Agrupa las clases que representan las entidades base del restaurante:
Producto, Usuario y Venta (esta última relaciona a un Usuario con un
Producto para registrar una operación de venta sencilla).
"""

from .producto import Producto
from .usuario import Usuario
from .venta import Venta

__all__ = ["Producto", "Usuario", "Venta"]
