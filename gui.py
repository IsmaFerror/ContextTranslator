import customtkinter as ctk
import threading
from services import AIService

# Configuración visual inicial (Modo oscuro y color azul)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Configuración de la ventana
        self.title("Context Translator AI")
        self.geometry("500x400")
        
        # Hacemos que la ventana siempre esté por encima de las demás (Topmost)
        # Esto es útil para una herramienta de traducción rápida.
        self.attributes("-topmost", True)

        # Inicializamos nuestro servicio de IA
        try:
            self.ai_service = AIService()
            self.status_text = "IA Conectada y lista."
        except Exception as e:
            self.ai_service = None
            self.status_text = f"Error: {e}"

        # 2. Crear los elementos visuales (Widgets)
        self.crear_interfaz()

    def crear_interfaz(self):
        # Título principal
        self.label_titulo = ctk.CTkLabel(self, text="Traductor de Contexto", font=("Arial", 20, "bold"))
        self.label_titulo.pack(pady=10)

        # Área de texto donde aparecerá la explicación (Scrollable)
        self.textbox_resultado = ctk.CTkTextbox(self, width=450, height=250)
        self.textbox_resultado.pack(pady=10)
        
        # Mensaje de bienvenida inicial
        self.textbox_resultado.insert("0.0", "Bienvenido.\n\nCopia un texto (Ctrl+C) y presiona el botón 'Analizar Portapapeles' para traducirlo y entender su contexto.")

        # Botón para accionar manualmente (luego lo haremos con teclas)
        self.boton_analizar = ctk.CTkButton(self, text="Analizar Portapapeles", command=self.accion_analizar)
        self.boton_analizar.pack(pady=10)

        # Etiqueta de estado (parte inferior)
        self.label_status = ctk.CTkLabel(self, text=self.status_text, text_color="gray")
        self.label_status.pack(side="bottom", pady=5)

    def accion_analizar(self):
        """
        Esta función se ejecuta cuando presionas el botón.
        """
        import pyperclip # Importamos aquí para leer el portapapeles
        
        # 1. Leer lo que el usuario tiene copiado
        texto_copiado = pyperclip.paste()
        
        if not texto_copiado:
            self.mostrar_resultado("El portapapeles está vacío. Copia algo de texto primero.")
            return

        self.mostrar_resultado("Pensando... (Consultando a Gemini)")

        # 2. Llamar a la IA en un hilo separado para no congelar la ventana
        # (Esto es muy importante en apps de escritorio: si la IA tarda 3 segundos,
        # la ventana no se debe quedar pegada).
        thread = threading.Thread(target=self.procesar_ia, args=(texto_copiado,))
        thread.start()

    def procesar_ia(self, texto):
        if self.ai_service:
            respuesta = self.ai_service.traducir_y_explicar(texto)
            self.mostrar_resultado(respuesta)
        else:
            self.mostrar_resultado("Error: El servicio de IA no está conectado.")

    def mostrar_resultado(self, texto):
        # Borrar el contenido anterior
        self.textbox_resultado.delete("0.0", "end")
        # Insertar el nuevo texto
        self.textbox_resultado.insert("0.0", texto)

# --- PUNTO DE ENTRADA PARA PROBAR LA GUI ---
if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()