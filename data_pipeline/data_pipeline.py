import sqlite3
import pandas as pd


def clean_books_data(df):
    """
    Clean and transform the scraped books dataset.
    """

    df = df.copy()

    # Convert price to numeric
    df["price_gbp"] = pd.to_numeric(df["price_gbp"], errors="coerce")

    # Convert availability to binary in-stock flag
    df["in_stock"] = (
        df["availability"]
        .astype(str)
        .str.lower()
        .str.contains("in stock")
        .astype(int)
    )

    # Convert rating to numeric
    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    if df["rating"].dtype == "object":
        df["rating"] = df["rating"].replace(rating_map)

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # GBP to INR conversion
    df["price_inr"] = (df["price_gbp"] * 105.5).round(2)

    # Keep final fields
    final_columns = [
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category"
    ]

    return df[final_columns]


def validate_data(df):
    """
    Perform basic data-quality validation.
    """

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nRating values:")
    print(sorted(df["rating"].dropna().unique()))

    print("\nIn-stock distribution:")
    print(df["in_stock"].value_counts())

    print("\nCategory count:")
    print(df["category"].nunique())

    print("\nPrice GBP range:")
    print(df["price_gbp"].min(), "-", df["price_gbp"].max())

    print("\nPrice INR range:")
    print(df["price_inr"].min(), "-", df["price_inr"].max())


def create_database(df, db_path="books.db"):
    """
    Create SQLite database with books and categories tables.
    """

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS books")
    cursor.execute("DROP TABLE IF EXISTS categories")

    cursor.execute("""
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price_gbp REAL,
            price_inr REAL,
            rating REAL,
            in_stock INTEGER,
            category_id INTEGER,
            FOREIGN KEY (category_id)
                REFERENCES categories(category_id)
        )
    """)

    categories = sorted(df["category"].dropna().unique())

    cursor.executemany(
        "INSERT INTO categories (category_name) VALUES (?)",
        [(category,) for category in categories]
    )

    category_map = {
        row[1]: row[0]
        for row in cursor.execute(
            "SELECT category_id, category_name FROM categories"
        )
    }

    records = [
        (
            row["title"],
            row["price_gbp"],
            row["price_inr"],
            row["rating"],
            row["in_stock"],
            category_map[row["category"]]
        )
        for _, row in df.iterrows()
    ]

    cursor.executemany("""
        INSERT INTO books
        (title, price_gbp, price_inr, rating, in_stock, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, records)

    conn.commit()

    return conn


def sql_join(conn):
    """
    Perform the validated SQL JOIN between books and categories.
    """

    query = """
        SELECT
            b.book_id,
            b.title,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock,
            c.category_name
        FROM books b
        JOIN categories c
            ON b.category_id = c.category_id
        ORDER BY b.book_id
    """

    return pd.read_sql_query(query, conn)


if __name__ == "__main__":
    print("Data pipeline module loaded successfully.")
