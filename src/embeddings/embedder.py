"""
Módulo para generar embeddings con modelos configurables desde config.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
import numpy as np
from config import EmbeddingConfig


class Embedder:
    """
    Clase para generar embeddings con modelos configurables

    El modelo y device se cargan desde config.py, que puede ser
    configurado vía variables de entorno en .env
    """

    def __init__(self, model_name: str = None, device: str = None):
        """
        Inicializa el modelo de embeddings

        Args:
            model_name: Nombre del modelo (None = usar config)
            device: Device a usar - 'cpu', 'cuda', 'mps' (None = usar config)
        """
        # Usar config si no se especifica
        self.model_name = model_name or EmbeddingConfig.MODEL_NAME
        self.device = device or EmbeddingConfig.DEVICE

        print(f"Cargando modelo de embeddings: {self.model_name}")
        print(f"Device: {self.device}")

        # Cargar modelo
        self.model = SentenceTransformer(self.model_name, device=self.device)

        print(f"Modelo cargado exitosamente")
        print(f"Dimensiones: {self.get_embedding_dimension()}")

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

    def get_embedding_dimension(self) -> int:
        """
        Obtiene la dimensión del embedding del modelo actual

        Returns:
            Dimensión del embedding (e.g., 1024 para BGE-M3)
        """
        return self.model.get_sentence_embedding_dimension()

    def get_model_info(self) -> dict:
        """
        Obtiene información sobre el modelo actual

        Returns:
            Diccionario con información del modelo
        """
        return {
            'model_name': self.model_name,
            'device': self.device,
            'embedding_dimension': self.get_embedding_dimension(),
            'max_seq_length': self.model.max_seq_length if hasattr(self.model, 'max_seq_length') else 'N/A'
        }


if __name__ == "__main__":
    # Test del módulo
    print("=== Test del Embedder ===\n")

    # Test con configuración por defecto
    embedder = Embedder()

    # Mostrar información del modelo
    info = embedder.get_model_info()
    print(f"\nInformación del modelo:")
    print(f"  Nombre: {info['model_name']}")
    print(f"  Device: {info['device']}")
    print(f"  Dimensiones: {info['embedding_dimension']}")
    print(f"  Max seq length: {info['max_seq_length']}")

    # Test de generación
    test_text = "Este es un texto de prueba para generar embeddings"
    print(f"\nGenerando embedding para: '{test_text}'")
    embedding = embedder.generate_embedding(test_text)

    print(f"Dimensión del embedding: {embedding.shape}")
    print(f"Tipo de datos: {embedding.dtype}")
    print(f"Primeros 5 valores: {embedding[:5]}")

    # Test de conversión
    embedding_bytes = embedder.embedding_to_bytes(embedding)
    print(f"\nTamaño en bytes: {len(embedding_bytes)}")

    recovered_embedding = embedder.bytes_to_embedding(embedding_bytes)
    print(f"Embedding recuperado correctamente: {np.allclose(embedding, recovered_embedding)}")

    # Test batch
    print("\nTest de batch encoding...")
    texts = ["Texto 1", "Texto 2", "Texto 3"]
    batch_embeddings = embedder.generate_embeddings_batch(texts)
    print(f"Embeddings generados: {batch_embeddings.shape}")

    print("\n✓ Test completado exitosamente")
