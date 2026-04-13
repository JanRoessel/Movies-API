from sqlalchemy import create_engine, text

DB_URL = "sqlite:///movies.db"
engine = create_engine(DB_URL, echo=False)


def init_db():
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """))
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                year INTEGER NOT NULL,
                rating REAL NOT NULL,
                poster TEXT,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """))


def get_all_users():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, name FROM users"))
        return [{"id": row._mapping["id"], "name": row._mapping["name"]} for row in result.fetchall()]


def create_user(name):
    with engine.begin() as connection:
        connection.execute(
            text("INSERT OR IGNORE INTO users (name) VALUES (:name)"),
            {"name": name}
        )
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT id FROM users WHERE name = :name"),
            {"name": name}
        )
        return result.fetchone()._mapping["id"]


def get_movies(user_id):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT title, year, rating, poster FROM movies WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        rows = result.fetchall()

    return [
        {
            "title": row._mapping["title"],
            "year": int(row._mapping["year"]) if row._mapping["year"] else 0,
            "rating": float(row._mapping["rating"]) if row._mapping["rating"] else 0,
            "poster": row._mapping["poster"]
        }
        for row in rows
    ]


def add_movie(title, year, rating, user_id, poster=None):
    with engine.begin() as connection:
        connection.execute(
            text("""
                INSERT INTO movies (title, year, rating, poster, user_id)
                VALUES (:title, :year, :rating, :poster, :user_id)
            """),
            {"title": title, "year": year, "rating": rating, "poster": poster, "user_id": user_id}
        )


def delete_movie(title, user_id):
    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM movies WHERE LOWER(title) = LOWER(:title) AND user_id = :user_id"),
            {"title": title, "user_id": user_id}
        )


def update_movie(title, rating, user_id):
    with engine.begin() as connection:
        connection.execute(
            text("""
                UPDATE movies SET rating = :rating
                WHERE LOWER(title) = LOWER(:title) AND user_id = :user_id
            """),
            {"title": title, "rating": rating, "user_id": user_id}
        )