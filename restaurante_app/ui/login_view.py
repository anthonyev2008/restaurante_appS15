"""
Módulo: ui/login_view.py

Contiene la clase LoginView, un tk.Frame que presenta la pantalla de
acceso simulada del restaurante: el logotipo del sistema, campos de
usuario y contraseña, un mensaje de retroalimentación y un botón para
ingresar.

LoginView NO valida credenciales por su cuenta ni lee archivos JSON:
solo recoge lo que la persona escribe y se lo entrega a
RestauranteServicio.validar_acceso(). Tampoco crea su propia ventana
Tkinter; se instancia dentro de la única ventana principal que crea
main.py, y avisa a quien la creó (mediante al_ingresar_exitosamente)
cuando el acceso fue válido, para que sea main.py quien decida cambiar
de vista.
"""

import os
import tkinter as tk

CARPETA_ASSETS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"
)


class LoginView(tk.Frame):
    """Pantalla de acceso simulada al sistema del restaurante."""

    def __init__(self, contenedor, restaurante_servicio, al_ingresar_exitosamente):
        super().__init__(contenedor)
        self.restaurante_servicio = restaurante_servicio
        self.al_ingresar_exitosamente = al_ingresar_exitosamente
        self._logo = self._cargar_logo()
        self._construir_widgets()

    def _cargar_logo(self):
        """
        Carga el logotipo del sistema desde assets/logo.png. Se
        conserva la referencia en self._logo para que Tkinter no la
        descarte; si el recurso no existe, la pantalla de acceso se
        muestra igualmente, solo que sin la imagen.
        """
        ruta_logo = os.path.join(CARPETA_ASSETS, "logo.png")
        try:
            imagen = tk.PhotoImage(file=ruta_logo)
            return imagen.subsample(3, 3)  # 256x256 -> ~85x85, a tamaño de encabezado
        except tk.TclError:
            print(f"Aviso: no se pudo cargar el logotipo ('{ruta_logo}').")
            return None

    def _construir_widgets(self) -> None:
        marco_titulo = tk.Frame(self)
        marco_titulo.pack(pady=(30, 10))

        if self._logo is not None:
            tk.Label(marco_titulo, image=self._logo).pack()

        tk.Label(
            marco_titulo, text="Mi Restaurante", font=("Arial", 20, "bold")
        ).pack(pady=(8, 0))
        tk.Label(
            marco_titulo,
            text="Acceso al sistema (simulado con fines académicos)",
            font=("Arial", 10),
            fg="gray30",
        ).pack(pady=(4, 0))

        marco_formulario = tk.Frame(self)
        marco_formulario.pack(pady=20)

        tk.Label(marco_formulario, text="Usuario:", font=("Arial", 11)).grid(
            row=0, column=0, sticky="e", padx=8, pady=8
        )
        self.entrada_usuario = tk.Entry(marco_formulario, width=28, font=("Arial", 11))
        self.entrada_usuario.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(marco_formulario, text="Contraseña:", font=("Arial", 11)).grid(
            row=1, column=0, sticky="e", padx=8, pady=8
        )
        self.entrada_contrasena = tk.Entry(
            marco_formulario, width=28, font=("Arial", 11), show="*"
        )
        self.entrada_contrasena.grid(row=1, column=1, padx=8, pady=8)

        self.etiqueta_mensaje = tk.Label(self, text="", fg="firebrick", font=("Arial", 10))
        self.etiqueta_mensaje.pack(pady=(0, 10))

        tk.Button(
            self,
            text="Ingresar",
            width=16,
            font=("Arial", 11),
            command=self._intentar_ingresar,
        ).pack(pady=5)

        # Permite ingresar presionando Enter desde el campo de contraseña.
        self.entrada_contrasena.bind("<Return>", lambda evento: self._intentar_ingresar())
        self.entrada_usuario.focus_set()

    def _intentar_ingresar(self) -> None:
        """
        Recoge lo escrito en ambos campos, valida que no estén vacíos y
        delega la verificación de credenciales en RestauranteServicio.
        Muestra un mensaje visual si algo falla, o avisa al contenedor
        de la aplicación si el acceso fue exitoso.
        """
        identificacion = self.entrada_usuario.get().strip()
        contrasena = self.entrada_contrasena.get().strip()

        if not identificacion or not contrasena:
            self.etiqueta_mensaje.config(text="Ingrese usuario y contraseña.")
            return

        usuario = self.restaurante_servicio.validar_acceso(identificacion, contrasena)
        if usuario is None:
            self.etiqueta_mensaje.config(text="Usuario o contraseña incorrectos.")
            self.entrada_contrasena.delete(0, tk.END)
            return

        self.etiqueta_mensaje.config(text="")
        self.al_ingresar_exitosamente(usuario)
