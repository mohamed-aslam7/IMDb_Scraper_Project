import pandas as pd
from sqlalchemy import create_engine

# Load the cleaned dataset
csv_file = "imdb_data_cleaned_2024.csv"  # Ensure this file is in your project folder
df = pd.read_csv(csv_file)

# Create an SQLite database connection
db_file = "imdb_movies.db"
engine = create_engine(f"sqlite:///{db_file}", echo=True)  # echo=True for debugging

# Store the DataFrame into SQL
table_name = "movies"
df.to_sql(table_name, con=engine, if_exists="replace", index=False)

print(f"Data successfully stored in {db_file} in table {table_name}")
