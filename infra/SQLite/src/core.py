import sqlite3
from typing import Optional
from pathlib import Path


class MyDataBase:
    def __init__(self, db_file_path: str):
        self.db_path = Path(db_file_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection: Optional[sqlite3.Connection] = None

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Устанавливает соединение с БД при инициализации"""
        try:
            if self.connection is None:
                self.connection = sqlite3.connect(
                    database=self.db_path,
                    isolation_level=None    # отключение автокоммита для руч. управления
                )

                # поддержка внешних ключей
                self.connection.execute("PRAGMA foreign_keys = ON")

                print(f"Подключение к БД установлено: {self.db_path}")
        except sqlite3.Error as error_msg:
            print(f"Ошибка во время утановки соединения: {error_msg}")
            raise
        return self.connection

    def _close(self):
        """Закрывает соединение с БД"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print(f"Соединение с БД закрыто")


    def _init_db(self):
        """Инициализация БД, создание таблиц"""
        connection = self._get_connection()

        connection.execute("BEGIN")

        try:
            cursor = self.connection.cursor()

            # создаем таблицу пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
            )
            """)

            # создаем таблицу сообщений
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_edited INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)

            # создаем индексы для быстрого поиска

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_user_id
                ON messages(user_id)
            """)

            cursor.close()
            connection.commit()  # записывает данные в бд (Подтверждает транзакцию)
            print(f"Таблицы успешно созданы/проверены.")
        except sqlite3.Error as error_msg:
            connection.rollback()
            print(f"Ошибка во вермя создания таблиц: {error_msg}")
            raise

    def transaction_example(self):
        """Демонстрация работы транзакций"""
        connection = self._get_connection()
        print(f"Пример работы транзакции")

        connection.execute("BEGIN")
        try:
            cursor = connection.cursor()
            # Первая операция
            cursor.execute(
                "INSERT INTO users (username, email) VALUES (?, ?)",
                ("alice", "alice@example.com"))

            print(f"{cursor.lastrowid}")   # Возвращает id строки в таблице

            # Вторая операция
            cursor.execute(
                "INSERT INTO users (username, email) VALUES (?, ?)",
                ("bob", "bob@example.com"))

            print(f"{cursor.lastrowid}")

            # raise ValueError("Ошибка во вермя транзакции")

            connection.commit()  # подтверждает транзакцию
        except Exception as error_msg:
            print(f"Произошла ошибка: {error_msg}")
            print("Откат транзакции.")
            connection.rollback()  # откатываеет транзакцию
        finally:
            cursor.close()

    def demonstrate_cursor_attributes(self):
        """Демонстрация возможностей курсора"""

        connection = self._get_connection()

        cursor = connection.cursor()

        connection.execute("BEGIN")
        try:
            # очищаем таблицы
            cursor.execute("""
                DELETE FROM users
            """)
            cursor.execute("""
                DELETE FROM messages
            """)

            # создаем пользователя
            cursor.execute("""
                INSERT INTO users (
                    username,
                    email)
                 VALUES (?, ?)
            """, (
                "test_user",
                "test@example.com"))
            user_id = cursor.lastrowid  # id пользователя

            for i in range(3):
                cursor.execute("""
                    INSERT INTO messages (user_id, content) VALUES (?, ?)
                """, (user_id, f"Сообщение {i + 1}"))

            connection.commit()
        except Exception as error_msg:
            connection.rollback()
            raise

        print("Атрибуты курсора дл выполнения запроса:")
        print(f"   cursor.description: {cursor.description}")  # None - запрос еще не выполнен
        print(f"   cursor.rowcount: {cursor.rowcount}")  # -1
        print(f"   cursor.lastrowid: {cursor.lastrowid}")  # ID последней вставки
        print(f"   cursor.arraysize: {cursor.arraysize}")  # 1 (по умолчанию)

        print(f"Выполняем select запрос:")
        cursor.execute("""
            SELECT * FROM users WHERE username = ?
        """, ('test_user', ))

        print(f"Атрибуты курсора после выполнения запроса")
        print(f"   cursor.description: {cursor.description}")
        print(f"   cursor.rowcount: {cursor.rowcount}")  # -1 для SELECT в SQLite
        print(f"   cursor.lastrowid: {cursor.lastrowid}")  # Не меняется после SELECT

        print("Методы для получения данных:")
        # fetchone() - получает одну строку
        print("\n   cursor.fetchone():")
        row = cursor.fetchone()
        print(f"Первая строка: {row}")

        # fetchmany() - получает несколько строк
        print("\n   cursor.fetchmany(size=2):")
        cursor.execute("SELECT * FROM messages ORDER BY id")
        rows = cursor.fetchmany(size=2)
        print(f"   Первые 2 строки: {rows}")
        print(f"   cursor.rowcount теперь: {cursor.rowcount}")  # Все еще -1

        # fetchall() - получает все строки
        print("\n   cursor.fetchall():")
        cursor.execute("SELECT id, content FROM messages")
        all_rows = cursor.fetchall()
        print(f"   Все строки: {all_rows}")

        print("Пример выполнения массовых операций")
        user_data = [
            ("john_doe", "john@example.com"),
            ("jane_smith", "jane@example.com"),
            ("bob_wilson", "bob@example.com"),
        ]

        connection.execute('BEGIN')

        try:
            cursor.executemany("""
                INSERT INTO users (username, email) VALUES (?, ?)
                
            """, user_data)

            connection.commit()
        except Exception as e:
            connection.rollback()


def main():
    db_instance = MyDataBase('D:/denis/projects/RAGSystem/infra/SQLite/storage/best_db.db')
    # db_instance.transaction_example()
    db_instance.demonstrate_cursor_attributes()


if __name__ == "__main__":
    main()