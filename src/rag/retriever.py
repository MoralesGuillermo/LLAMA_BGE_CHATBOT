"""
Módulo para recuperación de documentos relevantes usando similitud coseno
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from typing import List, Tuple
from database.repository import DocumentRepository
from embeddings.embedder import Embedder


class DocumentRetriever:
    """Clase para recuperar documentos relevantes usando búsqueda semántica"""

    def __init__(self, repository: DocumentRepository = None, embedder: Embedder = None):
        """
        Inicializa el retriever

        Args:
            repository: Repositorio de documentos (opcional)
            embedder: Generador de embeddings (opcional)
        """
        self.repository = repository if repository else DocumentRepository()
        self.embedder = embedder if embedder else Embedder()

    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcula la similitud coseno entre dos embeddings

        Args:
            embedding1: Primer embedding
            embedding2: Segundo embedding

        Returns:
            Valor de similitud coseno (0-1)
        """
        # Normalizar los vectores
        embedding1_norm = embedding1 / (np.linalg.norm(embedding1) + 1e-10)
        embedding2_norm = embedding2 / (np.linalg.norm(embedding2) + 1e-10)

        # Calcular producto punto
        similarity = np.dot(embedding1_norm, embedding2_norm)

        return float(similarity)

    def retrieve_relevant_documents(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Tuple[str, str, float]]:
        """
        Recupera los documentos más relevantes para una consulta

        Args:
            query: Pregunta del usuario
            top_k: Número de documentos a recuperar

        Returns:
            Lista de tuplas (filename, content, similarity_score)
            ordenadas por relevancia (mayor a menor)
        """
        # Generar embedding de la consulta
        print(f"Generando embedding para la consulta...")
        query_embedding = self.embedder.generate_embedding(query)

        # Obtener todos los documentos de la base de datos
        print("Recuperando documentos de la base de datos...")
        all_documents = self.repository.get_all_documents()

        if not all_documents:
            print("Advertencia: No hay documentos en la base de datos")
            return []

        # Calcular similitud con cada documento
        similarities = []

        for doc_id, filename, content, embedding_bytes in all_documents:
            # Convertir bytes a embedding
            doc_embedding = self.embedder.bytes_to_embedding(embedding_bytes)

            # Calcular similitud
            similarity = self.cosine_similarity(query_embedding, doc_embedding)

            similarities.append((filename, content, similarity))

        # Ordenar por similitud (mayor a menor)
        similarities.sort(key=lambda x: x[2], reverse=True)

        # Retornar top-k documentos
        top_documents = similarities[:top_k]

        print(f"\nTop {top_k} documentos más relevantes:")
        for i, (filename, _, score) in enumerate(top_documents, 1):
            print(f"{i}. {filename} (similitud: {score:.4f})")

        return top_documents

    def retrieve_with_threshold(
        self,
        query: str,
        threshold: float = 0.5,
        max_documents: int = 10
    ) -> List[Tuple[str, str, float]]:
        """
        Recupera documentos que superen un umbral de similitud

        Args:
            query: Pregunta del usuario
            threshold: Umbral mínimo de similitud (0-1)
            max_documents: Máximo número de documentos a retornar

        Returns:
            Lista de tuplas (filename, content, similarity_score)
        """
        # Generar embedding de la consulta
        query_embedding = self.embedder.generate_embedding(query)

        # Obtener todos los documentos
        all_documents = self.repository.get_all_documents()

        if not all_documents:
            return []

        # Calcular similitud y filtrar por umbral
        relevant_documents = []

        for doc_id, filename, content, embedding_bytes in all_documents:
            doc_embedding = self.embedder.bytes_to_embedding(embedding_bytes)
            similarity = self.cosine_similarity(query_embedding, doc_embedding)

            if similarity >= threshold:
                relevant_documents.append((filename, content, similarity))

        # Ordenar por similitud
        relevant_documents.sort(key=lambda x: x[2], reverse=True)

        # Limitar a max_documents
        return relevant_documents[:max_documents]


if __name__ == "__main__":
    # Test del retriever
    try:
        retriever = DocumentRetriever()

        test_query = "¿Cómo funciona el sistema?"

        print(f"Buscando documentos relevantes para: '{test_query}'\n")
        results = retriever.retrieve_relevant_documents(test_query, top_k=3)

        print("\n--- Resultados ---")
        for filename, content, score in results:
            print(f"\nDocumento: {filename}")
            print(f"Similitud: {score:.4f}")
            print(f"Contenido (primeros 200 chars): {content[:200]}...")

    except Exception as e:
        print(f"Error: {str(e)}")
