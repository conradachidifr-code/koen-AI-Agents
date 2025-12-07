#!/usr/bin/env python3
"""
Test script for DBuddy
Run this to test the agent functionality programmatically
"""

from agent import agent
from database import db_manager
import json


def main():
    print("=== DBuddy Test ===\n")

    # Test 1: Database Connection
    print("1. Testing database connection...")
    if db_manager.test_connection():
        print("   ✓ Database connected successfully!\n")
    else:
        print("   ✗ Database connection failed!")
        print("   Please check your .env configuration\n")
        return

    # Test 2: Get Schema
    print("2. Retrieving database schema...")
    try:
        schema = db_manager.get_schema()
        print("   ✓ Schema retrieved successfully!")
        print("\nDatabase Schema:")
        print("-" * 50)
        print(schema)
        print("-" * 50)
        print()
    except Exception as e:
        print(f"   ✗ Failed to get schema: {e}\n")
        return

    # Test 3: Process a sample query
    print("3. Testing natural language query processing...")
    test_queries = [
        "Show me all tables in the database",
        "How many records are in each table?",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {query}")
        print("   Processing...\n")

        try:
            result = agent.process_query(query)

            if result["success"]:
                print("   ✓ Query processed successfully!")
                print(f"\n   SQL Generated:\n   {result['sql_query']}")
                print(f"\n   Response:\n   {result['response']}")
                print(f"\n   Raw Results:\n   {json.dumps(result['results'], indent=2)}")
            else:
                print(f"   ✗ Query failed: {result['error']}")
                if result.get('sql_query'):
                    print(f"   SQL attempted: {result['sql_query']}")

        except Exception as e:
            print(f"   ✗ Error: {e}")

        print("\n" + "=" * 70 + "\n")

    print("\nTest completed! You can now start the web server with:")
    print("  python main.py")
    print("\nOr use the quick start script:")
    print("  ./start.sh")


if __name__ == "__main__":
    main()
