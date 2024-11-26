import sqlite3
import threading
from typing import List, Dict
from queue import Queue
import time  # Add this import

class Database:
    _instance = None
    _conn_pool = Queue()
    _local = threading.local()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path='quiz_app.db'):
        if not hasattr(self, 'initialized'):
            self.db_path = db_path
            self.initialized = True
            self.create_tables()

    def get_connection(self):
        if not hasattr(self._local, 'conn'):
            if self._conn_pool.empty():
                self._local.conn = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30  # Added timeout to wait for the database to be unlocked
                )
                self._local.conn.row_factory = sqlite3.Row
                self._local.conn.execute("PRAGMA journal_mode=WAL;")  # Enable WAL mode
            else:
                self._local.conn = self._conn_pool.get()
        return self._local.conn

    def release_connection(self):
        if hasattr(self._local, 'conn'):
            self._conn_pool.put(self._local.conn)
            del self._local.conn

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL
            )
        """)
        # Create history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question TEXT,
                category TEXT,
                type TEXT,
                difficulty TEXT,
                correct_answer TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
        
        # Ensure status column exists
        cursor.execute("PRAGMA table_info(history)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'status' not in columns:
            cursor.execute("ALTER TABLE history ADD COLUMN status TEXT DEFAULT 'pending'")
            conn.commit()

    def execute_with_retry(self, cursor, query, params=(), retries=5, delay=1):
        for attempt in range(retries):
            try:
                cursor.execute(query, params)
                return
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    time.sleep(delay)
                else:
                    raise
        raise sqlite3.OperationalError("Max retries exceeded for query: " + query)

    def add_user(self, username: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            self.execute_with_retry(cursor, "INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_id(self, username: str) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        return result[0] if result else None

    def add_question_history(self, user_id: int, question: Dict) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO history (user_id, question, category, type, difficulty, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            question.get('question'),
            question.get('category'),
            question.get('type'),
            question.get('difficulty'),
            question.get('correct_answer')
        ))
        conn.commit()
        return cursor.lastrowid  # Return the inserted record's ID

    def get_user_history(self, user_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT question, category, type, difficulty, correct_answer
            FROM history
            WHERE user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()
        history = []
        for row in rows:
            history.append({
                'question': row[0],
                'category': row[1],
                'type': row[2],
                'difficulty': row[3],
                'correct_answer': row[4]
            })
        return history

    def update_question_status(self, history_id: int, status: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        self.execute_with_retry(cursor, """
            UPDATE history 
            SET status = ?
            WHERE id = ?
        """, (status, history_id))
        conn.commit()
        # Debug statement
        cursor.execute("SELECT * FROM history WHERE id = ?", (history_id,))
        updated_row = cursor.fetchone()
        print(f"Debug: Updated Row - {updated_row}")

    def get_user_history_by_status(self, user_id: int, status: str) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, question, category, type, difficulty, correct_answer
            FROM history
            WHERE user_id = ? AND status = ?
        """, (user_id, status))
        rows = cursor.fetchall()
        return [{
            'id': row[0],
            'question': row[1],
            'category': row[2],
            'type': row[3],
            'difficulty': row[4],
            'correct_answer': row[5]
        } for row in rows]

    def reset_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS history")
        cursor.execute("DROP TABLE IF EXISTS users")
        conn.commit()
        self.create_tables()
        self._local.conn.close()

    def close(self):
        while not self._conn_pool.empty():
            conn = self._conn_pool.get()
            conn.close()
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            del self._local.conn
            del self._local.conn