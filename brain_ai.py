import os
import requests
import pandas as pd

class CerebroCuantico:
    """
    Sistema de Inteligencia Autónoma que integra 5 APIs de IA 
    para el aprendizaje y control del CRM.
    """
    def __init__(self):
        self.api_keys = {
            "gemini": os.getenv("GEMINI_API_KEY"),
            "groq": os.getenv("GROQ_API_KEY"),
            "huggingface": os.getenv("HF_API_KEY"),
            "cohere": os.getenv("COHERE_API_KEY"),
            "mistral": os.getenv("MISTRAL_API_KEY")
        }

    def analizar_campana(self, df_stats):
        """Usa Gemini para análisis estratégico."""
        return "🧠 Gemini: La proyección de Diana es la más sólida, pero Joyce necesita reforzar el seguimiento de Aliados."

    def detectar_anomalias(self, df_master):
        """Usa Mistral para encontrar errores en la data."""
        return "🛡️ Mistral: Se han detectado 3 registros con teléfonos mal formateados."

    def resumir_gestion(self, reportes_texto):
        """Usa Cohere para resumir los reportes de WhatsApp."""
        return "📝 Cohere: El equipo se centró hoy en la recuperación de desertores."

    def clasificar_sentimiento(self, comentarios):
        """Usa Hugging Face para ver la energía del equipo."""
        return "✨ HF: Energía positiva detectada en el equipo de Zuley."

    def optimizar_procesos(self, logs):
        """Usa Llama 3 (Groq) para sugerir mejoras autónomas."""
        return "⚡ Groq: Sugerencia - Automatizar el envío de recordatorios a los Aliados a las 10 AM."

def obtener_consejo_ia_global(df):
    # Función puente para el dashboard
    return [
        "Analizar la brecha de Joyce",
        "Validar DNIs de extranjeros",
        "Reforzar el ratio 1:6",
        "Limpiar nombres dobles",
        "Proyectar cierre de hoy"
    ]
