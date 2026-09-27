"""
Módulo: servicios/restaurante_servicio.py

Contiene la clase RestauranteServicio, capa de SERVICIO encargada de:
    - Recibir los registros crudos que entrega ArchivoServicio (listas
      de diccionarios) y convertirlos en objetos Producto, Usuario y
      Venta.
    - Concentrar las operaciones necesarias sobre esas colecciones:
      validar el acceso de un usuario, listar productos, listar
      usuarios, listar ventas y consultar cuántos hay registrados de
      cada uno.
    - Concentrar las reglas de negocio sobre productos que la interfaz
      gráfica solicita: registrar, buscar, actualizar y eliminar,
      conservando siempre el archivo productos.json sincronizado con
      lo que hay en memoria mediante ArchivoServicio.
    - Concentrar las reglas de negocio de la venta: comprobar que el
      usuario y el producto indicados existan, tomar el precio vigente
      del producto, registrar la operación y conservarla en
      ventas.json a través de ArchivoServicio.

Ninguna vista (LoginView ni MainView) debe leer o escribir archivos
JSON de forma directa, ni recorrer o modificar listas de diccionarios
crudos, ni validar datos por su cuenta: siempre deben pedir la
información ya convertida en objetos, y solicitar cualquier operación
sobre productos o ventas a través de este servicio. Los botones de la
interfaz solo recogen lo escrito o seleccionado en el formulario, y
llaman a estos métodos mediante un callback asociado con command=.

Nota sobre el acceso: validar_acceso() es una SIMULACIÓN pedagógica de
inicio de sesión (compara identificación y contraseña contra los
usuarios cargados desde usuarios.json). No implementa ningún mecanismo
real de seguridad -sin cifrado, sin tokens, sin control de intentos- y
no debe tratarse como tal.
"""

from datetime import datetime

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta


class RestauranteServicio:
    """Servicio que administra los productos, usuarios y ventas del restaurante."""

    def __init__(self, archivo_servicio) -> None:
        self.archivo_servicio = archivo_servicio
        self._productos: list[Producto] = []
        self._usuarios: list[Usuario] = []
        self._ventas: list[Venta] = []

    def cargar_datos(self) -> None:
        """
        Pide a ArchivoServicio los registros crudos de productos.json,
        usuarios.json y ventas.json, y los convierte en objetos
        Producto, Usuario y Venta respectivamente, dejándolos listos
        para ser consultados desde la interfaz gráfica.
        """
        self._productos = self._construir_productos(self.archivo_servicio.leer_productos())
        self._usuarios = self._construir_usuarios(self.archivo_servicio.leer_usuarios())
        self._ventas = self._construir_ventas(self.archivo_servicio.leer_ventas())

    # ------------------------------------------------------------------
    # Conversión de diccionarios crudos a objetos del dominio
    # ------------------------------------------------------------------
    def _construir_productos(self, registros: list) -> list:
        """Convierte los registros crudos en objetos Producto, omitiendo los inválidos."""
        productos: list[Producto] = []
        for registro in registros:
            try:
                if not isinstance(registro, dict):
                    raise ValueError("cada registro debe ser un objeto JSON (diccionario).")
                productos.append(Producto.from_dict(registro))
            except KeyError as error:
                print(f"Aviso: producto incompleto (falta la clave {error}); se omite: {registro}")
            except ValueError as error:
                print(f"Aviso: producto inválido ({error}); se omite: {registro}")
        return productos

    def _construir_usuarios(self, registros: list) -> list:
        """Convierte los registros crudos en objetos Usuario, omitiendo los inválidos."""
        usuarios: list[Usuario] = []
        for registro in registros:
            try:
                if not isinstance(registro, dict):
                    raise ValueError("cada registro debe ser un objeto JSON (diccionario).")
                usuarios.append(Usuario.from_dict(registro))
            except KeyError as error:
                print(f"Aviso: usuario incompleto (falta la clave {error}); se omite: {registro}")
            except ValueError as error:
                print(f"Aviso: usuario inválido ({error}); se omite: {registro}")
        return usuarios

    def _construir_ventas(self, registros: list) -> list:
        """Convierte los registros crudos en objetos Venta, omitiendo los inválidos."""
        ventas: list[Venta] = []
        for registro in registros:
            try:
                if not isinstance(registro, dict):
                    raise ValueError("cada registro debe ser un objeto JSON (diccionario).")
                ventas.append(Venta.from_dict(registro))
            except KeyError as error:
                print(f"Aviso: venta incompleta (falta la clave {error}); se omite: {registro}")
            except ValueError as error:
                print(f"Aviso: venta inválida ({error}); se omite: {registro}")
        return ventas

    # ------------------------------------------------------------------
    # Consultas para la interfaz gráfica
    # ------------------------------------------------------------------
    def listar_productos(self) -> list:
        """Devuelve la lista completa de productos cargados."""
        return list(self._productos)

    def listar_usuarios(self) -> list:
        """Devuelve la lista completa de usuarios cargados."""
        return list(self._usuarios)

    def buscar_usuario(self, identificacion: str):
        """
        Devuelve el objeto Usuario cuya identificación coincide
        exactamente con 'identificacion', o None si no existe ninguno.
        Se usa para comprobar que el usuario seleccionado en la venta
        existe y para mostrar su nombre junto a cada venta registrada.
        """
        return self._buscar_usuario_por_identificacion(self._normalizar_texto(identificacion))

    def listar_ventas(self) -> list:
        """Devuelve la lista completa de ventas registradas."""
        return list(self._ventas)

    def contar_productos(self) -> int:
        """Devuelve la cantidad de productos cargados."""
        return len(self._productos)

    def contar_usuarios(self) -> int:
        """Devuelve la cantidad de usuarios cargados."""
        return len(self._usuarios)

    def contar_ventas(self) -> int:
        """Devuelve la cantidad de ventas registradas."""
        return len(self._ventas)

    def listar_categorias(self) -> list:
        """
        Devuelve, ordenadas alfabéticamente, las categorías distintas
        que existen entre los productos actualmente cargados. Se usa
        para sugerir valores en el formulario de productos de la
        interfaz, sin que la vista necesite conocer los productos.
        """
        categorias = {producto.categoria for producto in self._productos}
        return sorted(categorias)

    # ------------------------------------------------------------------
    # Gestión de productos (registro, consulta, actualización, baja)
    # ------------------------------------------------------------------
    def buscar_producto(self, codigo: str):
        """
        Devuelve el objeto Producto cuyo código coincide exactamente
        con 'codigo', o None si no existe ninguno. MainView usa este
        método para cargar un producto existente en el formulario
        antes de actualizarlo o eliminarlo.
        """
        return self._buscar_producto_por_codigo(self._normalizar_texto(codigo))

    def registrar_producto(self, codigo, nombre, categoria, precio, stock) -> "Producto":
        """
        Crea un nuevo producto a partir de los datos capturados en el
        formulario de la interfaz, verifica que el código no esté
        repetido, lo agrega a la colección en memoria y guarda de
        inmediato el cambio en productos.json.

        Lanza ValueError si el código ya existe, si el precio o el
        stock no tienen un formato numérico válido, o si algún dato no
        cumple las reglas propias de Producto (validadas por sus
        @setter). En cualquiera de esos casos no se modifica nada.
        """
        codigo_normalizado = self._normalizar_texto(codigo)
        if not codigo_normalizado:
            raise ValueError("El código del producto no puede estar vacío.")
        if self._buscar_producto_por_codigo(codigo_normalizado) is not None:
            raise ValueError(f"Ya existe un producto registrado con el código '{codigo_normalizado}'.")

        precio_numerico = self._convertir_precio(precio)
        stock_numerico = self._convertir_stock(stock)

        nuevo_producto = Producto(codigo_normalizado, nombre, categoria, precio_numerico, stock_numerico)
        self._productos.append(nuevo_producto)
        self._persistir_productos()
        return nuevo_producto

    def actualizar_producto(self, codigo, nombre, categoria, precio, stock) -> "Producto":
        """
        Busca el producto con el código recibido y actualiza su
        nombre, categoría, precio y stock (el código no cambia:
        identifica al producto). Guarda el cambio en productos.json.

        Lanza ValueError si no existe un producto con ese código, si
        el precio o el stock no son numéricos, o si algún dato no
        cumple las reglas de Producto.
        """
        producto = self._buscar_producto_por_codigo(self._normalizar_texto(codigo))
        if producto is None:
            raise ValueError(f"No existe un producto registrado con el código '{codigo}'.")

        precio_numerico = self._convertir_precio(precio)
        stock_numerico = self._convertir_stock(stock)

        # Las propias @setter de Producto validan nombre, categoría,
        # precio y stock antes de aceptarlos.
        producto.nombre = nombre
        producto.categoria = categoria
        producto.precio = precio_numerico
        producto.stock = stock_numerico

        self._persistir_productos()
        return producto

    def eliminar_producto(self, codigo: str) -> None:
        """
        Elimina, de la colección en memoria y de productos.json, el
        producto cuyo código coincide con 'codigo'. Lanza ValueError
        si no existe ningún producto con ese código.
        """
        producto = self._buscar_producto_por_codigo(self._normalizar_texto(codigo))
        if producto is None:
            raise ValueError(f"No existe un producto registrado con el código '{codigo}'.")

        self._productos.remove(producto)
        self._persistir_productos()

    # ------------------------------------------------------------------
    # Auxiliares internos de la gestión de productos
    # ------------------------------------------------------------------
    def _buscar_producto_por_codigo(self, codigo):
        """Recorre la colección en memoria y devuelve el Producto con ese código, o None."""
        for producto in self._productos:
            if producto.codigo == codigo:
                return producto
        return None

    def _buscar_usuario_por_identificacion(self, identificacion):
        """Recorre la colección en memoria y devuelve el Usuario con esa identificación, o None."""
        for usuario in self._usuarios:
            if usuario.identificacion == identificacion:
                return usuario
        return None

    def _persistir_productos(self) -> None:
        """
        Convierte todos los productos en memoria a diccionarios y le
        pide a ArchivoServicio que los escriba en productos.json. Si
        la escritura falla (por ejemplo, por permisos), se informa un
        aviso por consola sin interrumpir la operación ya realizada en
        memoria.
        """
        registros = [producto.to_dict() for producto in self._productos]
        guardado_exitoso = self.archivo_servicio.guardar_productos(registros)
        if not guardado_exitoso:
            print("Aviso: el cambio se aplicó en memoria, pero no pudo guardarse en productos.json.")

    @staticmethod
    def _normalizar_texto(valor) -> str:
        """Recorta espacios de un texto recibido desde la interfaz; tolera None."""
        return valor.strip() if isinstance(valor, str) else valor

    @staticmethod
    def _convertir_precio(valor) -> float:
        """Convierte el texto del formulario a float; lanza ValueError con un mensaje claro si no es numérico."""
        try:
            return float(valor)
        except (TypeError, ValueError):
            raise ValueError("El precio debe ser un número (use punto decimal, por ejemplo 8.50).")

    @staticmethod
    def _convertir_stock(valor) -> int:
        """Convierte el texto del formulario a int; lanza ValueError con un mensaje claro si no es numérico."""
        try:
            return int(valor)
        except (TypeError, ValueError):
            raise ValueError("El stock debe ser un número entero (por ejemplo 10).")

    # ------------------------------------------------------------------
    # Gestión de ventas (registro sencillo de usuario + producto)
    # ------------------------------------------------------------------
    def registrar_venta(self, usuario_identificacion, producto_codigo, cantidad) -> "Venta":
        """
        Registra una venta sencilla que relaciona un usuario existente
        con un producto existente. Comprueba que ambos hayan sido
        seleccionados y que realmente existan, toma el precio vigente
        del producto como precio unitario de la venta, genera un
        identificador y una fecha, agrega la venta a la colección en
        memoria y guarda de inmediato el cambio en ventas.json.

        Lanza ValueError si no se seleccionó un usuario o un producto,
        si alguno de los dos no existe, o si la cantidad no es un
        número entero mayor que cero. En cualquiera de esos casos no
        se registra nada.
        """
        usuario_normalizado = self._normalizar_texto(usuario_identificacion)
        producto_normalizado = self._normalizar_texto(producto_codigo)

        if not usuario_normalizado:
            raise ValueError("Seleccione un usuario para registrar la venta.")
        if not producto_normalizado:
            raise ValueError("Seleccione un producto para registrar la venta.")

        usuario = self._buscar_usuario_por_identificacion(usuario_normalizado)
        if usuario is None:
            raise ValueError(f"No existe un usuario registrado con la identificación '{usuario_normalizado}'.")

        producto = self._buscar_producto_por_codigo(producto_normalizado)
        if producto is None:
            raise ValueError(f"No existe un producto registrado con el código '{producto_normalizado}'.")

        cantidad_numerica = self._convertir_cantidad(cantidad)

        nueva_venta = Venta(
            identificador=self._generar_identificador_venta(),
            usuario_identificacion=usuario.identificacion,
            producto_codigo=producto.codigo,
            cantidad=cantidad_numerica,
            precio_unitario=producto.precio,
            fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self._ventas.append(nueva_venta)
        self._persistir_ventas()
        return nueva_venta

    # ------------------------------------------------------------------
    # Auxiliares internos de la gestión de ventas
    # ------------------------------------------------------------------
    def _generar_identificador_venta(self) -> str:
        """
        Calcula el siguiente identificador disponible con el formato
        'V0001', 'V0002', etc., a partir del mayor número ya usado
        entre las ventas cargadas (sin depender de cuántas queden
        actualmente en la lista, por si alguna llegara a eliminarse).
        """
        mayor_numero = 0
        for venta in self._ventas:
            sufijo = venta.identificador[1:] if venta.identificador.startswith("V") else venta.identificador
            if sufijo.isdigit():
                mayor_numero = max(mayor_numero, int(sufijo))
        return f"V{mayor_numero + 1:04d}"

    def _persistir_ventas(self) -> None:
        """
        Convierte todas las ventas en memoria a diccionarios y le pide
        a ArchivoServicio que los escriba en ventas.json. Si la
        escritura falla, se informa un aviso por consola sin
        interrumpir la operación ya realizada en memoria.
        """
        registros = [venta.to_dict() for venta in self._ventas]
        guardado_exitoso = self.archivo_servicio.guardar_ventas(registros)
        if not guardado_exitoso:
            print("Aviso: el cambio se aplicó en memoria, pero no pudo guardarse en ventas.json.")

    @staticmethod
    def _convertir_cantidad(valor) -> int:
        """Convierte el texto del formulario a int; lanza ValueError con un mensaje claro si no es válido."""
        try:
            cantidad = int(valor)
        except (TypeError, ValueError):
            raise ValueError("La cantidad debe ser un número entero (por ejemplo 1).")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        return cantidad

    # ------------------------------------------------------------------
    # Acceso simulado
    # ------------------------------------------------------------------
    def validar_acceso(self, identificacion: str, contrasena: str):
        """
        Busca, entre los usuarios cargados, uno cuya identificación
        coincida con la recibida y compara su contraseña. Devuelve el
        objeto Usuario si el acceso es válido, o None si no hay
        coincidencia. LoginView solo debe llamar a este método: nunca
        debe comparar credenciales por su cuenta.
        """
        usuario = self._buscar_usuario_por_identificacion(self._normalizar_texto(identificacion))
        if usuario is not None and usuario.contrasena == contrasena:
            return usuario
        return None
