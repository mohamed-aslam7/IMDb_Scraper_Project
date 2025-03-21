import sqlite3
import pandas as pd

db_file = "imdb_movies.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:", tables)

cursor.execute("SELECT COUNT(*) FROM movies;")
total_rows = cursor.fetchone()[0]
print(f"Total movies stored: {total_rows}")

df = pd.read_sql("SELECT * FROM movies LIMIT 5;", conn)
print("Sample Data:")
print(df)

conn.close()
