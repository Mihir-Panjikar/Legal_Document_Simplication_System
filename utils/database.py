import sqlite3
import os
import json
from datetime import datetime


class HistoryDatabase:
    def __init__(self, db_path="./data/history.db"):
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create the necessary tables if they don't exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_text TEXT NOT NULL,
            simplified_text TEXT,
            translated_text TEXT,
            language TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            title TEXT
        )
        ''')
        self.conn.commit()

    def add_entry(self, input_text, simplified_text=None, translated_text=None, language=None):
        """Add a new entry to the history database."""
        # Create a title from the first 30 chars of input
        title = input_text[:30] + "..." if len(input_text) > 30 else input_text

        self.cursor.execute('''
        INSERT INTO history (input_text, simplified_text, translated_text, language, title)
        VALUES (?, ?, ?, ?, ?)
        ''', (input_text, simplified_text, translated_text, language, title))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_entry(self, entry_id, simplified_text=None, translated_text=None, language=None):
        """Update an existing history entry."""
        # Build the update query dynamically based on which fields are provided
        update_fields = []
        update_values = []

        if simplified_text is not None:
            update_fields.append("simplified_text = ?")
            update_values.append(simplified_text)

        if translated_text is not None:
            update_fields.append("translated_text = ?")
            update_values.append(translated_text)

        if language is not None:
            update_fields.append("language = ?")
            update_values.append(language)

        if not update_fields:
            return

        update_values.append(entry_id)

        query = f'''
        UPDATE history
        SET {", ".join(update_fields)}
        WHERE id = ?
        '''

        self.cursor.execute(query, update_values)
        self.conn.commit()

    def delete_entry(self, entry_id):
        """Delete a history entry by ID."""
        self.cursor.execute('''
        DELETE FROM history WHERE id = ?
        ''', (entry_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0  # Return True if a row was deleted

    def delete_all_entries(self):
        """Delete all history entries."""
        self.cursor.execute('DELETE FROM history')
        self.conn.commit()
        return self.cursor.rowcount

    def get_entry(self, entry_id):
        """Retrieve a specific history entry."""
        self.cursor.execute('''
        SELECT * FROM history WHERE id = ?
        ''', (entry_id,))
        return self.cursor.fetchone()

    def get_all_entries(self, limit=10):
        """Retrieve all history entries, sorted by most recent first."""
        self.cursor.execute('''
        SELECT id, title, timestamp FROM history
        ORDER BY timestamp DESC
        LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()

    def close(self):
        """Close the database connection."""
        self.conn.close()
