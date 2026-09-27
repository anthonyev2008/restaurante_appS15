"""
Módulo: servicios/archivo_servicio.py

Contiene la clase ArchivoServicio, capa de SERVICIO encargada de la
lectura y la escritura de los datos locales del restaurante,
almacenados como listas de diccionarios en datos/productos.json,
datos/usuarios.json y datos/ventas.json.

ArchivoServicio no administra ninguna colección de objetos ni conoce
las clases Producto, Usuario o Venta: se limita a leer y escribir
listas de diccionarios en disco mediante json.load()/json.dump().
Convertir esos diccionarios en objetos del dominio (y viceversa) es
responsabilidad de RestauranteServicio, que es quien conoce las
entidades del negocio.

Cada excepción que pueda producirse al acceder a los archivos (que no
exista el archivo, que no sea un JSON válido, que falten permisos) se
controla en este mismo servicio, para que la aplicación nunca se
detenga por un problema de lectura o escritura: en esos casos se
informa un aviso por consola y se devuelve un valor seguro (lista
vacía al leer, False al guardar).
"""

import json
import os

CARPETA_DATOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos"
)
RUTA_PRODUCTOS_POR_DEFECTO = os.path.join(CARPETA_DATOS, "productos.json")
RUTA_USUARIOS_POR_DEFECTO = os.path.join(CARPETA_DATOS, "usuarios.json")
RUTA_VENTAS_POR_DEFECTO = os.path.join(CARPETA_DATOS, "ventas.json")


class ArchivoServicio:
    """Servicio encargado de leer y escribir los archivos JSON locales del restaurante."""

    def __init__(
        self,
        ruta_productos: str = RUTA_PRODUCTOS_POR_DEFECTO,
        ruta_usuarios: str = RUTA_USUARIOS_POR_DEFECTO,
        ruta_ventas: str = RUTA_VENTAS_POR_DEFECTO,
    ) -> None:
        self.ruta_productos = ruta_productos
        self.ruta_usuarios = ruta_usuarios
        self.ruta_ventas = ruta_ventas

    def leer_productos(self) -> list:
        """Lee datos/productos.json y devuelve su contenido como lista de diccionarios."""
        return self._leer_archivo(self.ruta_productos)

    def leer_usuarios(self) -> list:
        """Lee datos/usuarios.json y devuelve su contenido como lista de diccionarios."""
        return self._leer_archivo(self.ruta_usuarios)

    def leer_ventas(self) -> list:
        """Lee datos/ventas.json y devuelve su contenido como lista de diccionarios."""
        return self._leer_archivo(self.ruta_ventas)

    def guardar_productos(self, registros: list) -> bool:
        """
        Escribe la lista de diccionarios de productos en
        datos/productos.json, reemplazando su contenido anterior.
        Devuelve True si pudo guardar y False si ocurrió un problema
        de acceso (sin detener la aplicación).
        """
        return self._escribir_archivo(self.ruta_productos, registros)

    def guardar_ventas(self, registros: list) -> bool:
        """
        Escribe la lista de diccionarios de ventas en
        datos/ventas.json, reemplazando su contenido anterior.
        Devuelve True si pudo guardar y False si ocurrió un problema
        de acceso (sin detener la aplicación).
        """
        return self._escribir_archivo(self.ruta_ventas, registros)

    # ------------------------------------------------------------------
    # Lectura genérica (compartida por productos y usuarios)
    # ------------------------------------------------------------------
    def _leer_archivo(self, ruta_archivo: str) -> list:
        """
        Abre y decodifica un archivo JSON, controlando cada excepción
        de acceso de forma específica. Devuelve siempre una lista:
        vacía si el archivo no existe, está corrupto, no se puede leer,
        o no contiene la estructura esperada (una lista de registros).
        """
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except FileNotFoundError:
            print(f"Aviso: no se encontró '{ruta_archivo}'; se iniciará con una lista vacía.")
            return []
        except json.JSONDecodeError:
            print(f"Aviso: '{ruta_archivo}' no contiene un JSON válido; se iniciará con una lista vacía.")
            return []
        except PermissionError:
            print(f"Aviso: sin permisos para leer '{ruta_archivo}'; se iniciará con una lista vacía.")
            return []

        if not isinstance(datos, list):
            print(
                f"Aviso: '{ruta_archivo}' no tiene la estructura esperada "
                "(se esperaba una lista de registros); se iniciará con una lista vacía."
            )
            return []

        return datos

    # ------------------------------------------------------------------
    # Escritura genérica (usada por guardar_productos)
    # ------------------------------------------------------------------
    def _escribir_archivo(self, ruta_archivo: str, registros: list) -> bool:
        """
        Escribe 'registros' (una lista de diccionarios) en 'ruta_archivo'
        con formato JSON legible. Controla cada excepción de escritura
        de forma específica y nunca detiene la aplicación: en caso de
        error, informa un aviso por consola y devuelve False.
        """
        try:
            with open(ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(registros, archivo, ensure_ascii=False, indent=4)
        except PermissionError:
            print(f"Aviso: sin permisos para escribir en '{ruta_archivo}'; no se guardaron los cambios.")
            return False
        except OSError as error:
            print(f"Aviso: no se pudo escribir en '{ruta_archivo}' ({error}); no se guardaron los cambios.")
            return False

        return True
