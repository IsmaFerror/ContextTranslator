import customtkinter as ctk
import threading
import keyboard
import time
import winsound
import ctypes # Necesario para el icono de la barra de tareas
import os
from services import AIService
import pyperclip

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        
        # Esto separa el icono de la barra de tareas del de Python genérico
        myappid = 'context.translator.ai.v1' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Configuramos el icono de la ventana y de la barra de tareas
        # Asegúrate de tener 'logo.ico' en la misma carpeta
        if os.path.exists("frx_logo.ico"):
            self.iconbitmap("frx_logo.ico")
        else:
            print("AVISO: No se encontró 'logo.ico'. Usando icono por defecto.")

        # --- 2. CONFIGURACIÓN DE VENTANA ---
        self.title("✦AI Context")
        
        # Dimensiones fijas
        self.ancho_ventana = 400
        self.alto_ventana = 450
        
        self.resizable(False, True)
        self.attributes("-topmost", True)

        # --- 3. POSICIONAMIENTO AUTOMÁTICO (ABAJO-DERECHA) ---
        self.posicionar_abajo_derecha()

        # Inicializar IA
        try:
            self.ai_service = AIService()
            self.estado_texto = "✦Selecciona texto y pulsa Ctrl + Alt + X"
        except Exception as e:
            self.ai_service = None
            self.estado_texto = f"Error: {e}"

        self.vista_resultados_activa = False
        self.crear_pantalla_inicio()

        # Hotkey
        keyboard.add_hotkey('ctrl+alt+x', self.activar_desde_hotkey)

    def posicionar_abajo_derecha(self):
        """
        Calcula la posición exacta para que la ventana aparezca
        pegada a la derecha y justo encima de la barra de tareas.
        """
        # Obtenemos el ancho y alto de TU monitor
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Márgenes para que no quede pegado al borde absoluto
        margen_derecho = 20
        margen_inferior = 70 # Un poco más alto para librar la barra de tareas de Windows

        # Fórmula matemática de posición:
        # X = AnchoPantalla - AnchoVentana - Margen
        # Y = AltoPantalla - AltoVentana - Margen
        x_pos = screen_width - self.ancho_ventana - margen_derecho
        y_pos = screen_height - self.alto_ventana - margen_inferior

        # Aplicamos la geometría
        self.geometry(f"{self.ancho_ventana}x{self.alto_ventana}+{x_pos}+{y_pos}")

    def crear_pantalla_inicio(self):
        self.frame_inicio = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inicio.pack(fill="both", expand=True, padx=20, pady=20)

        label_titulo = ctk.CTkLabel(
            self.frame_inicio, 
            text="✦AI Context Translator✦", 
            font=("Roboto", 24, "bold"),
            text_color="#FFFFFF"
        )
        label_titulo.pack(pady=(80, 20))

        label_instr = ctk.CTkLabel(
            self.frame_inicio, 
            text="1. Selecciona texto\n2. Presiona Ctrl + Alt + X\n3. Espera el sonido de confirmación",
            font=("Arial", 14),
            text_color="gray"
        )
        label_instr.pack(pady=10)

        self.label_status = ctk.CTkLabel(self, text=self.estado_texto, text_color="gray", font=("Arial", 10))
        self.label_status.pack(side="bottom", anchor="e", padx=10, pady=5)

    def cambiar_a_vista_resultados(self):
        if not self.vista_resultados_activa:
            self.frame_inicio.destroy()
            
            self.frame_resultados = ctk.CTkFrame(self, fg_color="transparent")
            self.frame_resultados.pack(fill="both", expand=True, padx=15, pady=10)

            # Traducción
            lbl_trad = ctk.CTkLabel(self.frame_resultados, text="TRADUCCIÓN", font=("Roboto", 12, "bold"), text_color="#3B8ED0")
            lbl_trad.pack(anchor="w", pady=(0, 2))
            self.box_traduccion = ctk.CTkTextbox(self.frame_resultados, height=80, fg_color="#2b2b2b", state="disabled")
            self.box_traduccion.pack(fill="x", pady=(0, 15))

            # Contexto
            lbl_context = ctk.CTkLabel(self.frame_resultados, text="CONTEXTO Y MATICES", font=("Roboto", 12, "bold"), text_color="#3B8ED0")
            lbl_context.pack(anchor="w", pady=(0, 2))
            self.box_contexto = ctk.CTkTextbox(self.frame_resultados, height=150, fg_color="#2b2b2b", state="disabled")
            self.box_contexto.pack(fill="both", expand=True, pady=(0, 5))

            self.vista_resultados_activa = True

    def escribir_en_caja(self, caja, texto):
        caja.configure(state="normal")
        caja.delete("0.0", "end")
        caja.insert("0.0", texto)
        caja.configure(state="disabled")

    def activar_desde_hotkey(self):
        winsound.MessageBeep() 
        
        # Nos aseguramos de que siempre aparezca en su sitio (por si la moviste)
        self.posicionar_abajo_derecha()
        
        pyperclip.copy("")
        time.sleep(0.3) 

        texto_capturado = ""
        for i in range(5):
            keyboard.send('ctrl+c')
            time.sleep(0.2)
            texto_capturado = pyperclip.paste()
            if texto_capturado and texto_capturado.strip() != "":
                break
        
        if not texto_capturado or texto_capturado.strip() == "":
            print("No se pudo copiar el texto.")
            return

        self.deiconify() 
        self.focus_force() 
        
        if not self.vista_resultados_activa:
            self.cambiar_a_vista_resultados()

        self.mostrar_cargando()
        threading.Thread(target=self.procesar_ia, args=(texto_capturado,)).start()

    def mostrar_cargando(self):
        self.escribir_en_caja(self.box_traduccion, "Traduciendo...")
        self.escribir_en_caja(self.box_contexto, "Analizando matices...")
        self.label_status.configure(text="Consultando a Gemini...")

    def procesar_ia(self, texto):
        if self.ai_service:
            respuesta_raw = self.ai_service.traducir_y_explicar(texto)
            
            if "|||" in respuesta_raw:
                partes = respuesta_raw.split("|||")
                traduccion = partes[0].strip()
                contexto = partes[1].strip()
            else:
                traduccion = "Ver contexto abajo"
                contexto = respuesta_raw

            self.escribir_en_caja(self.box_traduccion, traduccion)
            self.escribir_en_caja(self.box_contexto, contexto)
            self.label_status.configure(text="Listo.")

if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()