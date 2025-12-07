import pymysql
from typing import List, Dict, Any
from config import settings


class DatabaseManager:
    """Manages MySQL database connections and queries"""

    def __init__(self):
        self.connection_params = {
            "host": settings.mysql_host,
            "port": settings.mysql_port,
            "user": settings.mysql_user,
            "password": settings.mysql_password,
            "database": settings.mysql_database,
            "cursorclass": pymysql.cursors.DictCursor,
        }

    def get_connection(self):
        """Create a new database connection"""
        return pymysql.connect(**self.connection_params)

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results

        Args:
            sql: SQL query to execute

        Returns:
            List of dictionaries containing query results
        """
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
                return results
        finally:
            connection.close()

    def get_schema(self) -> str:
        """
        Get database schema information for all tables

        Returns:
            Formatted string describing the database schema
        """
        connection = self.get_connection()
        schema_info = []

        try:
            with connection.cursor() as cursor:
                # Get all tables
                cursor.execute("SHOW TABLES")
                tables = [list(table.values())[0] for table in cursor.fetchall()]

                for table in tables:
                    schema_info.append(f"\nTable: {table}")

                    # Get columns for each table
                    cursor.execute(f"DESCRIBE {table}")
                    columns = cursor.fetchall()

                    for column in columns:
                        field = column['Field']
                        col_type = column['Type']
                        null = column['Null']
                        key = column['Key']
                        schema_info.append(
                            f"  - {field} ({col_type}){' PRIMARY KEY' if key == 'PRI' else ''}{' NULL' if null == 'YES' else ''}"
                        )
        finally:
            connection.close()

        return "\n".join(schema_info)

    def test_connection(self) -> bool:
        """Test if database connection is working"""
        try:
            connection = self.get_connection()
            connection.close()
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False


db_manager = DatabaseManager()
