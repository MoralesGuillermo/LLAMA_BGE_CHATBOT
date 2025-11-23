"""
Módulo para generar embeddings usando BGE-M3
"""
from sentence_transformers import SentenceTransformer
import numpy as np


class Embedder:
    """Clase para generar embeddings con el modelo BGE-M3"""

    def __init__(self):
        """Inicializa el modelo BGE-M3"""
        print("Cargando modelo BGE-M3...")
        self.model = SentenceTransformer('BAAI/bge-m3')
        print("Modelo cargado exitosamente")

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Genera un embedding para un texto dado

        Args:
            text: Texto de entrada

        Returns:
            numpy array con el embedding (float32)
        """
        if not text or not text.strip():
            raise ValueError("El texto no puede estar vacío")

        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.astype('float32')

    def generate_embeddings_batch(self, texts: list) -> np.ndarray:
        """
        Genera embeddings para múltiples textos

        Args:
            texts: Lista de textos

        Returns:
            numpy array con los embeddings (float32)
        """
        if not texts:
            raise ValueError("La lista de textos no puede estar vacía")

        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.astype('float32')

    def embedding_to_bytes(self, embedding: np.ndarray) -> bytes:
        """
        Convierte un embedding a bytes para almacenar en SQL Server

        Args:
            embedding: numpy array con el embedding

        Returns:
            bytes para almacenar como VARBINARY
        """
        return embedding.astype('float32').tobytes()

    @staticmethod
    def bytes_to_embedding(embedding_bytes: bytes) -> np.ndarray:
        """
        Convierte bytes de vuelta a embedding

        Args:
            embedding_bytes: bytes del embedding

        Returns:
            numpy array con el embedding (float32)
        """
        return np.frombuffer(embedding_bytes, dtype='float32')


if __name__ == "__main__":
    # Test del módulo
    embedder = Embedder()

    test_text = "Este es un texto de prueba para generar embeddings"
    embedding = embedder.generate_embedding(test_text)

    print(f"Dimensión del embedding: {embedding.shape}")
    print(f"Primeros 5 valores: {embedding[:5]}")

    # Test de conversión
    embedding_bytes = embedder.embedding_to_bytes(embedding)
    print(f"Tamaño en bytes: {len(embedding_bytes)}")

    recovered_embedding = embedder.bytes_to_embedding(embedding_bytes)
    print(f"Embedding recuperado correctamente: {np.allclose(embedding, recovered_embedding)}")
