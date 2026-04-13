import random
import requests
import movie_storage_sql as movie_storage
import os


API_KEY = "613e10be"


def fetch_movie(title):
    url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"
    return requests.get(url).json()


def list_movies(movies):
    if not movies:
        print("No movies found.")
        return

    for m in movies:
        print(f"{m['title']} ({m['year']}) - {m['rating']}")


def add_movie():
    """ Add a movie from a user """
    title = input("Title: ")
    year = int(input("Year: "))
    rating_input = input("Rating: ").replace(",", ".")
    rating = float(rating_input)
    movie_storage.add_movie(title, year, rating)


def delete_movie():
    """ deletes a movie named by the user """
    title = input("Delete: ")
    movie_storage.delete_movie(title)


def update_movie():
    """ updates a rating of an existing movie """
    title = input("Movie: ")
    rating = float(input("New rating: "))
    movie_storage.update_movie(title, rating)


def add_movie_from_api():
    """ adds a movie through thr API """
    title = input("Movie title: ")
    data = fetch_movie(title)

    if data.get("Response") == "False":
        print("Not found.")
        return

    rating = data.get("imdbRating")
    try:
        rating = float(rating)
    except:
        rating = 0

    year = data.get("Year", "0")
    try:
        year = int(year[:4])
    except:
        year = 0

    movie_storage.add_movie(
        data.get("Title"),
        year,
        rating,
        data.get("Poster")
    )

    print("Added from OMDb!")


def movies_sorted_by_year(movies):
    """ sorts movies by year """
    sorted_movies = sorted(movies, key=lambda x: x["year"], reverse=True)
    for movie in sorted_movies:
        print(f"{movie['title']} ({movie['year']}) - {movie['rating']}")


def sorted_by_rating(movies):
    """ sorts movies by rating """
    sorted_movies = sorted(movies, key=lambda x: x["rating"], reverse=True)
    for movie in sorted_movies:
        print(f"{movie['title']} - {movie['rating']}")


def stats(movies):
    """ Shows stats """
    if not movies:
        print("No movies in the database.")
        return

    ratings = [m["rating"] for m in movies if m["rating"] is not None]

    if not ratings:
        print("No ratings available.")
        return

    avg = sum(ratings) / len(ratings)
    print(f"Average rating: {avg:.2f}")
    print(f"Best rating: {max(ratings)}")
    print(f"Worst rating: {min(ratings)}")


def random_movie(movies):
    """ selects a random movie """
    if not movies:
        print("No movies available.")
        return

    movie = random.choice(movies)
    print(f"Random: {movie['title']} ({movie['year']}) - {movie['rating']}")


def search_movie(movies):
    """ searches for a movie by name """
    query = input("Search: ").lower()

    results = [m for m in movies if query in m["title"].lower()]

    if not results:
        print("No matches found.")
        return

    for movie in results:
        print(f"{movie['title']} ({movie['year']}) - {movie['rating']}")


def generate_movie_grid(movies):
    html = ""

    for movie in movies:
        poster = movie["poster"] if movie["poster"] not in (None, "N/A") else ""

        html += f"""
        <li>
            <div class="movie">
                <img class="movie-poster" src="{poster}" alt="{movie['title']}">
                <div class="movie-title">{movie['title']}</div>
                <div class="movie-year">{movie['year']}</div>
                <div class="movie-year">⭐ {movie['rating']}</div>
            </div>
        </li>
        """

    return html


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_website():
    movies = movie_storage.get_movies()

    template_path = os.path.join(BASE_DIR, "_static", "index_template.html")
    output_path = os.path.join(BASE_DIR, "_static", "index.html")

    with open(template_path, "r", encoding="UTF-8") as f:
        template = f.read()

    movie_grid = generate_movie_grid(movies)

    html = template.replace("__TEMPLATE_TITLE__", "My Movie App")
    html = html.replace("__TEMPLATE_MOVIE_GRID__", movie_grid)

    with open(output_path, "w", encoding="UTF-8") as f:
        f.write(html)

    print("Website was generated successfully.")

def main():
    """ Main function """
    movie_storage.init_db()

    actions = {
        "1": lambda: list_movies(movie_storage.get_movies()),
        "2": add_movie,
        "3": delete_movie,
        "4": update_movie,
        "5": lambda: stats(movie_storage.get_movies()),
        "6": lambda: random_movie(movie_storage.get_movies()),
        "7": lambda: search_movie(movie_storage.get_movies()),
        "8": lambda: sorted_by_rating(movie_storage.get_movies()),
        "9": lambda: movies_sorted_by_year(movie_storage.get_movies()),
        "10": add_movie_from_api,
        "11": generate_website,
    }

    while True:
        print("\n0 Exit")
        print("1 List")
        print("2 Add manual")
        print("3 Delete")
        print("4 Update")
        print("5 Stats")
        print("6 Random")
        print("7 Search")
        print("8 Sort rating")
        print("9 Sort year")
        print("10 Add from API")
        print("11 Generate website")

        choice = input("Choice: ")

        if choice == "0":
            break

        action = actions.get(choice)

        if action:
            action()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
