"""
Módulo para operaciones CRUD en la base de datos
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from typing import List, Tuple, Optional
from database.connection import DatabaseConnection


class DocumentRepository:
    """Repositorio para operaciones con documentos"""

    def __init__(self, db_connection: DatabaseConnection = None):
        """
        Inicializa el repositorio

        Args:
            db_connection: Conexión a la base de datos (opcional)
        """
        self.db = db_connection if db_connection else DatabaseConnection()
        if not self.db.connection:
            self.db.connect()

    def insert_document(self, filename: str, content: str, embedding_bytes: bytes) -> int:
        """
        Inserta un documento con su embedding en la base de datos

        Args:
            filename: Nombre del archivo
            content: Contenido del documento
            embedding_bytes: Embedding en formato bytes

        Returns:
            ID del documento insertado
        """
        insert_query = """
        INSERT INTO Documents (filename, content, embedding)
        VALUES (?, ?, ?)
        """

        select_query = "SELECT SCOPE_IDENTITY() AS id"

        try:
            # Insertar documento
            cursor = self.db.execute_query(insert_query, (filename, content, embedding_bytes))

            # Obtener el ID del documento insertado
            cursor.execute(select_query)
            row = cursor.fetchone()
            doc_id = int(row[0]) if row else None

            if doc_id:
                print(f"Documento '{filename}' insertado con ID: {doc_id}")
                return doc_id
            else:
                raise Exception("No se pudo obtener el ID del documento insertado")

        except Exception as e:
            raise Exception(f"Error al insertar documento: {str(e)}")

    def get_all_documents(self) -> List[Tuple[int, str, str, bytes]]:
        """
        Obtiene todos los documentos de la base de datos

        Returns:
            Lista de tuplas (id, filename, content, embedding_bytes)
        """
        query = "SELECT id, filename, content, embedding FROM Documents"

        try:
            cursor = self.db.execute_query(query)
            documents = cursor.fetchall()
            print(f"Se recuperaron {len(documents)} documentos")
            return documents

        except Exception as e:
            raise Exception(f"Error al obtener documentos: {str(e)}")

    def get_document_by_id(self, doc_id: int) -> Optional[Tuple[int, str, str, bytes]]:
        """
        Obtiene un documento por su ID

        Args:
            doc_id: ID del documento

        Returns:
            Tupla (id, filename, content, embedding_bytes) o None si no existe
        """
        query = "SELECT id, filename, content, embedding FROM Documents WHERE id = ?"

        try:
            cursor = self.db.execute_query(query, (doc_id,))
            document = cursor.fetchone()
            return document

        except Exception as e:
            raise Exception(f"Error al obtener documento: {str(e)}")

    def delete_document(self, doc_id: int) -> bool:
        """
        Elimina un documento por su ID

        Args:
            doc_id: ID del documento a eliminar

        Returns:
            True si se eliminó, False si no existía
        """
        query = "DELETE FROM Documents WHERE id = ?"

        try:
            cursor = self.db.execute_query(query, (doc_id,))
            rows_affected = cursor.rowcount
            if rows_affected > 0:
                print(f"Documento {doc_id} eliminado")
                return True
            else:
                print(f"Documento {doc_id} no encontrado")
                return False

        except Exception as e:
            raise Exception(f"Error al eliminar documento: {str(e)}")

    def delete_all_documents(self) -> int:
        """
        Elimina todos los documentos de la base de datos

        Returns:
            Número de documentos eliminados
        """
        query = "DELETE FROM Documents"

        try:
            cursor = self.db.execute_query(query)
            rows_affected = cursor.rowcount
            print(f"Se eliminaron {rows_affected} documentos")
            return rows_affected

        except Exception as e:
            raise Exception(f"Error al eliminar documentos: {str(e)}")

    def count_documents(self) -> int:
        """
        Cuenta el número total de documentos

        Returns:
            Número de documentos
        """
        query = "SELECT COUNT(*) FROM Documents"

        try:
            cursor = self.db.execute_query(query)
            count = cursor.fetchone()[0]
            return count

        except Exception as e:
            raise Exception(f"Error al contar documentos: {str(e)}")

    def document_exists(self, filename: str) -> bool:
        """
        Verifica si un documento ya existe en la base de datos

        Args:
            filename: Nombre del archivo a verificar

        Returns:
            True si existe, False si no
        """
        query = "SELECT COUNT(*) FROM Documents WHERE filename = ?"

        try:
            cursor = self.db.execute_query(query, (filename,))
            count = cursor.fetchone()[0]
            return count > 0

        except Exception as e:
            raise Exception(f"Error al verificar documento: {str(e)}")
