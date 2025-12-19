import pymysql
from pymysql.cursors import DictCursor


class Database:
    _instance = None
    _connection = None

    @classmethod
    def get(cls):
        """Get database instance (singleton pattern)"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize database connection"""
        if Database._connection is None:
            try:
                # First, connect without specifying database to create it
                temp_connection = pymysql.connect(
                    host='localhost',
                    user='root',  # Change this to your MySQL username
                    password='',  # Change this to your MySQL password
                    cursorclass=DictCursor
                )

                # Create database if it doesn't exist
                with temp_connection.cursor() as cursor:
                    cursor.execute("CREATE DATABASE IF NOT EXISTS attendance_system")
                    print("[Database] Database 'attendance_system' created or already exists")

                temp_connection.close()

                # Now connect to the database
                Database._connection = pymysql.connect(
                    host='localhost',
                    user='root',  # Change this to your MySQL username
                    password='',  # Change this to your MySQL password
                    database='attendance_system',
                    cursorclass=DictCursor,
                    autocommit=True
                )
                print("[Database] Connected successfully to 'attendance_system'")
            except Exception as e:
                print(f"[Database] Connection failed: {e}")
                raise

    def execute(self, query, params=None):
        """Execute a query that doesn't return results (INSERT, UPDATE, DELETE)"""
        try:
            with Database._connection.cursor() as cursor:
                cursor.execute(query, params or ())
                Database._connection.commit()
                return cursor
        except Exception as e:
            print(f"[Database] Execute error: {e}")
            Database._connection.rollback()
            raise

    def query_one(self, query, params=None):
        """Execute a query and return one result"""
        try:
            with Database._connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
        except Exception as e:
            print(f"[Database] Query one error: {e}")
            raise

    def query_all(self, query, params=None):
        """Execute a query and return all results"""
        try:
            with Database._connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Exception as e:
            print(f"[Database] Query all error: {e}")
            raise

    def close(self):
        """Close the database connection"""
        if Database._connection:
            Database._connection.close()
            Database._connection = None
            print("[Database] Connection closed")