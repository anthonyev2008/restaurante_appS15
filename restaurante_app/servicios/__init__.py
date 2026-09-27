"""
Paquete servicios.

Agrupa las clases de servicio de esta etapa: ArchivoServicio (lectura
de los archivos JSON locales) y RestauranteServicio (conversión de los
datos leídos en objetos del dominio y operaciones sobre productos y
usuarios).
"""

from .archivo_servicio import ArchivoServicio
from .restaurante_servicio import RestauranteServicio

__all__ = ["ArchivoServicio", "RestauranteServicio"]
