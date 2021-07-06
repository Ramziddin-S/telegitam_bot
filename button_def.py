import sqlite3

class Button:
    def __init__(self, database):
        self.conn = sqlite3.connect(database, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user(
                id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER NOT NULL,
                first_name TEXT NULL, last_name TEXT NULL,
                contact TEXT NULL, created_at DATETIME
            )
            """
        )
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS category(
                id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, 
                created_at DATETIME
            )
            """
        )
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS product(
                id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
                description TEXT NOT NULL, price TEXT NULL, image TEXT NULL, 
                category_id INTEGER NULL, created_at DATETIME,
                FOREIGN KEY (category_id) REFERENCES category (id) ON DELETE SET NULL
            )
            """
        )
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_card(
                id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NULL,
                product_id INTEGER NULL, amount INTEGER NOT NULL, 
                status INTEGER NOT NULL, created_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE SET NULL,
                FOREIGN KEY (product_id) REFERENCES product (id) ON DELETE SET NULL
            )
            """
        )
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_order(
                id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NULL,
                products TEXT NOT NULL, created_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE SET NULL
            )
            """
        )
        self.conn.commit()