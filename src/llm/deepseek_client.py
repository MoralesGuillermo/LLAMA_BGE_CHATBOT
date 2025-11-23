"""
Módulo para interactuar con la API de DeepSeek
"""
import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Optional


class DeepSeekClient:
    """Cliente para la API de DeepSeek"""

    def __init__(self):
        """Inicializa el cliente de DeepSeek"""
        load_dotenv()

        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY no está configurada en .env")

        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = "deepseek-chat"

    def generate_response(
        self,
        query: str,
        context_documents: List[str],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Genera una respuesta usando el contexto RAG

        Args:
            query: Pregunta del usuario
            context_documents: Lista de documentos relevantes como contexto
            temperature: Temperatura para la generación (0-1)
            max_tokens: Máximo de tokens en la respuesta

        Returns:
            Respuesta generada por DeepSeek
        """
        # Construir el prompt RAG
        context = "\n\n---\n\n".join(context_documents)

        system_prompt = """Eres un asistente útil que responde preguntas basándose ÚNICAMENTE en el contexto proporcionado.
Si la información no está en el contexto, di claramente que no tienes esa información.
No inventes información ni uses conocimiento externo al contexto."""

        user_prompt = f"""Usa SOLO esta información de contexto para responder:

{context}

Pregunta del usuario:
{query}"""

        # Preparar el payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content']
                return answer.strip()
            else:
                raise Exception("Respuesta de la API no tiene el formato esperado")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error al llamar a la API de DeepSeek: {str(e)}")

    def simple_chat(
        self,
        message: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Chat simple sin contexto RAG

        Args:
            message: Mensaje del usuario
            temperature: Temperatura para la generación
            max_tokens: Máximo de tokens

        Returns:
            Respuesta de DeepSeek
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": message}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            else:
                raise Exception("Respuesta de la API no tiene el formato esperado")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error al llamar a la API de DeepSeek: {str(e)}")


if __name__ == "__main__":
    # Test del cliente
    try:
        client = DeepSeekClient()

        # Test simple
        test_query = "¿Qué es Python?"
        test_context = [
            "Python es un lenguaje de programación de alto nivel.",
            "Python fue creado por Guido van Rossum en 1991."
        ]

        print("Enviando consulta a DeepSeek...")
        response = client.generate_response(test_query, test_context)
        print(f"\nRespuesta:\n{response}")

    except Exception as e:
        print(f"Error: {str(e)}")
