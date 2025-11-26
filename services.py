import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar las variables de entorno (tu API Key)
load_dotenv()

class AIService:
    def __init__(self):
        # Configurar la IA con la clave
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró la API Key en el archivo .env")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash') 

    def traducir_y_explicar(self, texto):
        try:
            prompt = f"""
            Actúa como un experto traductor y lingüista.
            Analiza el siguiente texto: "{texto}"
            
            1. Tradúcelo al español (si ya está en español, tradúcelo al inglés).
            2. Explica brevemente el contexto, tono o matices culturales si los hay.
            
            Formato de respuesta:
            Traducción: [Texto traducido]
            Contexto: [Explicación breve]
            """
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error al conectar con la IA: {e}"

# --- ZONA DE PRUEBA (Esto solo se ejecuta si corres este archivo directamente) ---
if __name__ == "__main__":
    print("Probando conexión con Gemini...")
    servicio = AIService()
    respuesta = servicio.traducir_y_explicar("It's raining cats and dogs")
    print("\nRespuesta de la IA:")
    print(respuesta)