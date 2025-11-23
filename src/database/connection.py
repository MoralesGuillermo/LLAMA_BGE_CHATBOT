"""
Módulo para gestionar la conexión a SQL Server
"""
import os
import pyodbc
from dotenv import load_dotenv


class DatabaseConnection:
    """Clase para manejar la conexión a SQL Server"""

    def __init__(self):
        """Inicializa la conexión cargando variables de entorno"""
        load_dotenv()

        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
        self.database = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')

        self._validate_config()
        self.connection = None

    def _validate_config(self):
        """Valida que todas las variables de entorno necesarias estén configuradas"""
        required_vars = {
            'DB_HOST': self.host,
            'DB_PORT': self.port,
            'DB_NAME': self.database,
            'DB_USER': self.user,
            'DB_PASSWORD': self.password
        }

        missing_vars = [var for var, value in required_vars.items() if not value]

        if missing_vars:
            raise ValueError(
                f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}"
            )

    def connect(self):
        """Establece la conexión a SQL Server"""
        try:
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.host},{self.port};"
                f"DATABASE={self.database};"
                f"UID={self.user};"
                f"PWD={self.password}"
            )

            self.connection = pyodbc.connect(connection_string)
            print("Conexión a SQL Server establecida exitosamente")
            return self.connection

        except pyodbc.Error as e:
            raise ConnectionError(f"Error al conectar a SQL Server: {str(e)}")

    def disconnect(self):
        """Cierra la conexión a SQL Server"""
        if self.connection:
            self.connection.close()
            print("Conexión cerrada")

    def get_cursor(self):
        """
        Obtiene un cursor para ejecutar consultas

        Returns:
            Cursor de pyodbc
        """
        if not self.connection:
            self.connect()
        return self.connection.cursor()

    def execute_query(self, query: str, params: tuple = None):
        """
        Ejecuta una consulta SQL

        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros de la consulta (opcional)

        Returns:
            Cursor con los resultados
        """
        cursor = self.get_cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Solo hacer commit si no es un SELECT
            query_upper = query.strip().upper()
            if not query_upper.startswith('SELECT'):
                self.connection.commit()

            return cursor
        except pyodbc.Error as e:
            self.connection.rollback()
            raise Exception(f"Error al ejecutar la consulta: {str(e)}")

    def create_table_if_not_exists(self):
        """Crea la tabla Documents si no existe"""
        create_table_query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Documents' AND xtype='U')
        CREATE TABLE Documents (
            id INT PRIMARY KEY IDENTITY(1,1),
            filename NVARCHAR(255),
            content NVARCHAR(MAX),
            embedding VARBINARY(MAX)
        )
        """
        try:
            self.execute_query(create_table_query)
            print("Tabla 'Documents' verificada/creada exitosamente")
        except Exception as e:
            raise Exception(f"Error al crear la tabla: {str(e)}")


if __name__ == "__main__":
    # Test de conexión
    try:
        db = DatabaseConnection()
        db.connect()
        db.create_table_if_not_exists()
        db.disconnect()
        print("Test de conexión exitoso")
    except Exception as e:
        print(f"Error en test: {str(e)}")
