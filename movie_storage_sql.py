from sqlalchemy import create_engine, text

# ---------- DATABASE ----------
DB_URL = "sqlite:///movies.db"
engine = create_engine(DB_URL, echo=False)


# ---------- INIT ----------
def init_db():
  with engine.begin() as connection:
    connection.execute(text("""
      CREATE TABLE IF NOT EXISTS movies (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT UNIQUE NOT NULL,
          year INTEGER NOT NULL,
          rating REAL NOT NULL,
          poster TEXT
      )
  """))



def get_movies():
    with engine.connect() as connection:
        result = connection.execute(text(
            "SELECT title, year, rating, poster FROM movies"
        ))
        rows = result.fetchall()

    movies = []

    for row in rows:
        movies.append({
            "title": row._mapping["title"],
            "year": int(row._mapping["year"]) if row._mapping["year"] else 0,
            "rating": float(row._mapping["rating"]) if row._mapping["rating"] else 0,
            "poster": row._mapping["poster"]
        })

    return movies


# ---------- CREATE ----------
def add_movie(title, year, rating, poster=None):
    with engine.begin() as connection:
        connection.execute(
            text("""
                INSERT OR IGNORE INTO movies (title, year, rating, poster)
                VALUES (:title, :year, :rating, :poster)
            """),
            {
                "title": title,
                "year": year,
                "rating": rating,
                "poster": poster
            }
        )


# ---------- DELETE ----------
def delete_movie(title):
    with engine.begin() as connection:
        connection.execute(
            text("""
                DELETE FROM movies
                WHERE LOWER(title) = LOWER(:title)
            """),
            {"title": title}
        )


# ---------- UPDATE ----------
def update_movie(title, rating):
    with engine.begin() as connection:
        connection.execute(
            text("""
                UPDATE movies
                SET rating = :rating
                WHERE LOWER(title) = LOWER(:title)
            """),
            {
                "title": title,
                "rating": rating
            }
        )