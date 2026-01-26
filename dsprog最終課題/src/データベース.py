import sqlite3
import os

class DBHandler:
    def __init__(self, db_name="travel_analysis.db"):
        # main.pyと同じ階層にある「data」フォルダを確実に指定する
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(base_dir, "data")
        
        # もしdataフォルダがなければ、ここで自動作成する
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.db_path = os.path.join(self.data_dir, db_name)
        self.create_table()

    def create_table(self):
        # 確実に「絶対パス」を使ってデータベースを開く
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tourist_spots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    area_name TEXT UNIQUE,
                    wiki_length INTEGER,
                    avg_price INTEGER
                )
            """)

    def upsert_data(self, area, length, price):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tourist_spots (area_name, wiki_length, avg_price)
                VALUES (?, ?, ?)
            """, (area, length, price))