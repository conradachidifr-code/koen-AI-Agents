import ollama
from typing import Dict, Any
from config import settings
from database import db_manager


class SQLChatAgent:
    """Chatbot agent that converts natural language to SQL and executes queries"""

    def __init__(self):
        self.model = settings.ollama_model
        self.schema = None

    def get_database_schema(self) -> str:
        """Cache and return the database schema"""
        if self.schema is None:
            self.schema = db_manager.get_schema()
        return self.schema

    def generate_sql(self, user_query: str) -> str:
        """
        Convert natural language query to SQL

        Args:
            user_query: User's natural language question

        Returns:
            SQL query string
        """
        schema = self.get_database_schema()

        prompt = f"""You are a SQL expert. Convert the following natural language query into a valid MySQL query.

Database Schema:
{schema}

User Question: {user_query}

Rules:
1. Return ONLY the SQL query, nothing else
2. Use proper MySQL syntax
3. Make sure the query is safe (no DROP, DELETE, UPDATE, or other destructive operations)
4. Use appropriate JOINs if multiple tables are involved
5. Add LIMIT clause if appropriate to avoid returning too many results

SQL Query:"""

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
        )

        sql_query = response['response'].strip()

        # Remove markdown code blocks if present
        if sql_query.startswith("```"):
            lines = sql_query.split("\n")
            # Remove first line (```) and last line (```)
            sql_query = "\n".join(lines[1:-1]) if len(lines) > 2 else sql_query
            # Also handle inline ```sql
            if sql_query.startswith("sql"):
                sql_query = sql_query[3:].strip()

        return sql_query.strip()

    def format_results(self, user_query: str, sql_query: str, results: list) -> str:
        """
        Convert SQL results into human-readable response

        Args:
            user_query: Original user question
            sql_query: SQL query that was executed
            results: Query results

        Returns:
            Human-readable response
        """
        prompt = f"""You are a helpful assistant. The user asked: "{user_query}"

The following SQL query was executed:
{sql_query}

Query Results (as JSON):
{results}

Please provide a natural, conversational response to the user's question based on these results.
- Be concise but informative
- Format numbers and dates nicely
- If there are many results, summarize them appropriately
- If there are no results, say so politely

Response:"""

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
        )

        return response['response'].strip()

    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a natural language query end-to-end

        Args:
            user_query: User's natural language question

        Returns:
            Dictionary containing SQL query, results, and formatted response
        """
        try:
            # Generate SQL from natural language
            sql_query = self.generate_sql(user_query)

            # Validate query is safe (basic check)
            sql_upper = sql_query.upper()
            dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE"]
            if any(keyword in sql_upper for keyword in dangerous_keywords):
                return {
                    "success": False,
                    "error": "Query contains potentially dangerous operations. Only SELECT queries are allowed.",
                    "sql_query": sql_query,
                }

            # Execute query
            results = db_manager.execute_query(sql_query)

            # Format results into human-readable response
            formatted_response = self.format_results(user_query, sql_query, results)

            return {
                "success": True,
                "sql_query": sql_query,
                "results": results,
                "response": formatted_response,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sql_query": sql_query if 'sql_query' in locals() else None,
            }


agent = SQLChatAgent()
