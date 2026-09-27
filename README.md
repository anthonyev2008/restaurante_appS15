# Sistema de Restaurante — restaurante_app (Conceptos fundamentales de manejo de eventos)
**Nombre:** Anthony Jorlayn Espin Vintimilla
**Asignatura:** Programación Orientada a Objetos
**Tema:** Semana 15 — Conceptos fundamentales de manejo de eventos

## 1. Propósito de esta entrega

Esta entrega continúa la evolución de `restaurante_app` a partir de la versión
gráfica ya construida en etapas anteriores. Se conserva íntegra la
arquitectura modular (`datos`, `modelos`, `servicios`, `ui`, `main.py`), el
flujo de acceso, la gestión completa de productos y la consulta de usuarios
que ya funcionaban, y se incorpora la sección de **Ventas**, que hasta ahora
figuraba como pendiente.

El propósito central de la semana **no** es la venta en sí, sino comprender
los **fundamentos básicos del manejo de eventos**: cómo una acción del
usuario (pulsar un botón) se asocia mediante `command=` a un **callback**,
cómo ese callback obtiene la información necesaria de la interfaz sin
concentrar en ella la lógica del negocio, cómo delega la operación al
servicio correspondiente, y cómo el resultado (éxito o error) se refleja de
inmediato en la pantalla. La venta se usa únicamente como contexto práctico
para evidenciar ese flujo:

```
USUARIO realiza una acción
        ↓
BOTÓN / COMPONENTE ("Registrar venta")
        ↓
command=
        ↓
CALLBACK (_registrar_venta, en MainView)
        ↓
RestauranteServicio (valida y registra)
        ↓
PERSISTENCIA (ventas.json, vía ArchivoServicio)
        ↓
RESPUESTA EN LA INTERFAZ (tabla y mensaje actualizados)
```

No se implementó manejo avanzado de eventos (`bind()`, doble clic, eventos de
teclado/mouse, `<<TreeviewSelect>>`), ni facturación, carrito de compras o
inventario avanzado: toda acción se dispara mediante botones con `command=`,
tal como en las secciones ya existentes de Productos y Usuarios.

## 2. Estructura del proyecto

```
restaurante_app/
├── datos/
│   ├── productos.json          # Información de productos (código, nombre, categoría, precio, stock)
│   ├── usuarios.json           # Información de usuarios (identificación, nombre, correo, contraseña)
│   └── ventas.json             # Ventas registradas (usuario, producto, cantidad, precio, total, fecha)
├── modelos/
│   ├── __init__.py             # Expone Producto, Usuario y Venta
│   ├── producto.py             # Clase Producto + to_dict()/from_dict()
│   ├── usuario.py              # Clase Usuario + to_dict()/from_dict()
│   └── venta.py                # Clase Venta (relaciona usuario + producto) + to_dict()/from_dict()
├── servicios/
│   ├── __init__.py             # Expone ArchivoServicio y RestauranteServicio
│   ├── archivo_servicio.py     # Lectura y escritura de productos.json, usuarios.json y ventas.json
│   └── restaurante_servicio.py # Conversión a objetos, acceso, CRUD de productos y registro de ventas
├── ui/
│   ├── __init__.py             # Paquete de vistas gráficas
│   ├── login_view.py           # Pantalla de acceso simulada, ahora con el logotipo del sistema
│   └── main_view.py            # Panel principal: Notebook con Productos, Usuarios y Ventas
├── assets/                     # Ícono de la aplicación, logotipo e íconos de cada pestaña
│   ├── logo.png
│   ├── icono_app.png
│   ├── icono_productos.png
│   ├── icono_usuarios.png
│   └── icono_ventas.png
├── main.py                     # Punto de entrada: crea la ventana y controla las vistas
└── README.md
```

No se reconstruyó el proyecto desde cero: se mantiene la misma separación de
responsabilidades entre datos, modelos, servicios, ui y `main.py`; solo se
amplió lo necesario en `modelos/`, `servicios/archivo_servicio.py`,
`servicios/restaurante_servicio.py`, `ui/main_view.py` y `ui/login_view.py`,
y se agregó la carpeta `assets/` con los recursos visuales del sistema.

## 3. La sección de Ventas

`MainView` incorpora una tercera pestaña, **Ventas**, con el mismo estilo de
componentes ya usado en Productos:

- **`ttk.LabelFrame` "Registrar venta"**: agrupa dos `ttk.Combobox` en modo
  solo lectura —uno con los usuarios registrados, otro con los productos
  registrados, mostrando "identificación/código - nombre"— y un `ttk.Entry`
  para la cantidad.
- **`ttk.Frame`** (barra de acciones): botones **Registrar venta** y
  **Limpiar campos**, ambos activados mediante `command=`.
- **`tk.Label`** de retroalimentación: igual que en Productos, muestra en
  verde el resultado exitoso o en rojo el motivo del error.
- **`ttk.LabelFrame` "Ventas registradas"** con un **`ttk.Treeview` +
  `ttk.Scrollbar`**: N° de venta, usuario, producto, cantidad, precio
  unitario, total y fecha, además del total de ventas registradas.

Los combobox de usuario y producto se llenan a partir de
`RestauranteServicio.listar_usuarios()` y `listar_productos()`, y se
refrescan automáticamente cada vez que la lista de productos cambia desde la
pestaña Productos, para que la pestaña Ventas nunca ofrezca un producto que
ya no existe.

## 4. Responsabilidades de cada capa

- **Producto** y **Usuario** (`modelos/`): sin cambios de comportamiento;
  siguen validando sus propios datos mediante `@property`/`@setter` y
  convirtiéndose a/desde diccionario.
- **Venta** (`modelos/venta.py`, nueva): representa la relación entre un
  usuario y un producto —identificador, identificación del usuario, código
  del producto, cantidad, precio unitario tomado al momento de la venta y
  fecha—. El `total` es una propiedad calculada (`cantidad * precio_unitario`),
  nunca un valor guardado por separado que pueda desincronizarse. Al igual
  que Producto y Usuario, Venta no decide si el usuario o el producto
  existen: solo valida que sus propios datos sean coherentes.
- **ArchivoServicio** (`servicios/archivo_servicio.py`): ahora también lee y
  escribe `datos/ventas.json` (`leer_ventas()` / `guardar_ventas()`), con el
  mismo manejo de excepciones ya usado para productos y usuarios: nunca
  detiene la aplicación por un problema de acceso a disco.
- **RestauranteServicio** (`servicios/restaurante_servicio.py`): concentra
  las reglas de negocio de la venta en `registrar_venta(usuario_identificacion,
  producto_codigo, cantidad)`:
  1. Verifica que se haya indicado un usuario y un producto.
  2. Busca al usuario (`buscar_usuario`, nuevo) y al producto
     (`buscar_producto`, ya existente) y confirma que ambos existan.
  3. Convierte y valida la cantidad (entero mayor que cero).
  4. Toma el precio vigente del producto como precio unitario de la venta.
  5. Genera un identificador consecutivo (`V0001`, `V0002`, ...) y la fecha
     actual.
  6. Agrega la venta a la colección en memoria y la guarda de inmediato en
     `ventas.json`.

  Cualquier dato inválido o inexistente produce un `ValueError` con un
  mensaje claro, y no se registra nada. La interfaz nunca valida estas
  reglas por su cuenta ni escribe directamente en `ventas.json`.
- **LoginView** (`ui/login_view.py`): sin cambios funcionales; se le agregó
  el logotipo del sistema (`assets/logo.png`) sobre el título existente.
- **MainView** (`ui/main_view.py`): agrega la pestaña Ventas descrita en la
  sección 3, coordina su callback (`_registrar_venta`) siguiendo el mismo
  patrón que los botones de Productos, y ahora carga desde `assets/` el
  logotipo del encabezado y un ícono para cada pestaña del `ttk.Notebook`.
- **main.py**: sin cambios de responsabilidad; adicionalmente asigna el
  ícono de la ventana (`assets/icono_app.png`) y reporta por consola cuántas
  ventas se recuperaron de `datos/`, junto con productos y usuarios.

## 5. Persistencia utilizada

- `productos.json` y `usuarios.json`: se mantienen exactamente como en la
  etapa anterior.
- `ventas.json` (nuevo): cada venta registrada desde la interfaz se agrega a
  la colección en memoria de `RestauranteServicio` y se guarda de inmediato
  mediante `ArchivoServicio.guardar_ventas()`. Al reiniciar la aplicación,
  las ventas se vuelven a cargar y los identificadores nuevos continúan la
  numeración a partir del mayor existente.

## 6. Recursos visuales (`assets/`)

La carpeta `assets/` contiene el logotipo del sistema (`logo.png`, usado en
la pantalla de acceso y en el encabezado del panel principal), el ícono de
la ventana (`icono_app.png`) y un ícono por pestaña del `ttk.Notebook`
(`icono_productos.png`, `icono_usuarios.png`, `icono_ventas.png`). Todas las
imágenes se cargan con `tkinter.PhotoImage` y se reducen con `.subsample()`
al tamaño necesario; si algún archivo faltara, la interfaz sigue funcionando
igual, solo que sin esa imagen puntual (no se interrumpe la aplicación).

## 7. Flujo de la aplicación

```
Inicio de la aplicación
        ↓
main.py prepara Tkinter y los servicios
        ↓
LoginView
        ↓
RestauranteServicio valida el acceso
        ↓
MainView (ttk.Notebook)
        ↓
   ┌────────────┬────────────┬──────────────────────────────┐
   Productos      Usuarios     Ventas
   │ Registrar     │ Consulta   │ Seleccionar usuario + producto
   │ Consultar/Cargar           │ Registrar venta (command= → callback)
   │ Actualizar                 │ Consulta de ventas registradas
   │ Eliminar
   ↓
RestauranteServicio procesa la operación
   ↓
Persistencia en productos.json / ventas.json
   ↓
Actualización de la tabla y del mensaje en la interfaz
        ↓
Cerrar sesión
        ↓
LoginView
```

> **Nota sobre el acceso:** el inicio de sesión sigue siendo una
> **simulación con fines académicos**; no implementa un mecanismo real de
> autenticación segura.

## 8. Cómo ejecutar el programa

```bash
cd restaurante_app
python main.py
```

Al iniciar, la consola muestra cuántos productos, usuarios y ventas se
recuperaron desde la carpeta `datos/`, y luego se abre la ventana con la
pantalla de acceso.

### Usuarios de prueba incluidos

| Identificación | Contraseña | Nombre |
|---|---|---|
| U001 | 1234 | Maria Fernanda Lopez |
| U002 | 5678 | Carlos Andres Vega |
| U003 | clave3 | Ana Sofia Torres |

### Comprobación rápida de la sección Ventas

1. Inicie sesión con cualquiera de los usuarios de prueba.
2. Abra la pestaña **Ventas**.
3. Elija un usuario y un producto de las listas desplegables, indique una
   cantidad (por defecto 1) y presione **Registrar venta**.
4. La venta aparece de inmediato en la tabla, con su total calculado y la
   fecha del registro; el archivo `datos/ventas.json` queda actualizado.
5. Cierre y vuelva a abrir la aplicación: la venta registrada sigue
   apareciendo, con el mismo identificador.

## 9. Qué se implementó y qué queda pendiente

**Implementado en esta etapa:**
- Modelo `Venta` y persistencia completa en `ventas.json`.
- Sección "Ventas" funcional en la interfaz: selección de usuario y
  producto existentes, registro mediante `command=` + callback, delegación
  total de las reglas a `RestauranteServicio`, y tabla de ventas siempre
  actualizada.
- Flujo de manejo de eventos evidenciado de extremo a extremo: botón →
  `command=` → callback → servicio → persistencia → respuesta visual.
- Incorporación de `assets/` con el logotipo del sistema y un ícono por
  pestaña.
- Conservación íntegra de todo lo desarrollado previamente: arquitectura
  modular, flujo de acceso, gestión completa de productos y consulta de
  usuarios.

**Pendiente para próximas etapas:**
- Registro, edición o baja de usuarios desde la interfaz.
- Cualquier mecanismo real de autenticación.
- Manejo de eventos más avanzado (selección de filas, atajos de teclado,
  etc.), fuera del alcance de esta semana.
