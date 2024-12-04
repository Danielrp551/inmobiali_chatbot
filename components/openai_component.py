from openai import OpenAI
from api_keys.api_keys import openai_api_key
from prompt.prompt import prompt_consulta, prompt_intenciones, prompt_informacion_inmueble, prompt_consulta_general
from helpers.helpers import formatear_conversacion
import pytz
from datetime import datetime

class OpenAIManager:
    def __init__(self):
        self.client = OpenAI(api_key=openai_api_key)

    def consulta(self, cliente,conversation_actual, conversation_history):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_consulta(cliente) + formatear_conversacion(conversation_actual)},
            ],
            max_tokens=250,
        )
        return response.choices[0].message.content.strip()
    
    def mapear_intenciones(self, conversation_actual, conversation_history):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_intenciones() + formatear_conversacion(conversation_actual)},
            ],
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    
    def consulta_informacion_inmueble(self, inmueble, conversation_actual):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_informacion_inmueble(inmueble) + formatear_conversacion(conversation_actual)},
            ],
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    
    def consulta_general(self, conversation_actual):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_consulta_general() + formatear_conversacion(conversation_actual)},
            ],
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
