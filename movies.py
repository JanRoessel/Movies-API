import os
import random
import requests
import movie_storage_sql as movie_storage

API_KEY = "613e10be"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_movie(title):
    try:
        url = f"https://www.omdbapi.com/?apikey={API_KEY}&t={title}"
        return requests.get(url).json()
    except Exception as e:
        print(f"Could not reach OMDB API: {e}")
        return None


def select_user():
    """Show user selection menu at startup, return (user_id, username)"""
    while True:
        users = movie_storage.get_all_users()

        print("\nWelcome to the Movie App!")
        print("\nSelect a user:")
        for i, user in enumerate(users, 1):
            print(f"{i}. {user['name']}")
        print(f"{len(users) + 1}. Create new user")

        choice = input("\nEnter choice: ")

        try:
            choice = int(choice)
            if 1 <= choice <= len(users):
                user = users[choice - 1]
                print(f"\nWelcome back, {user['name']}!")
                return user["id"], user["name"]
            elif choice == len(users) + 1:
                name = input("Enter new username: ").strip()
                if name:
                    user_id = movie_storage.create_user(name)
                    print(f"\nWelcome, {name}!")
                    return user_id, name
                else:
                    print("Username cannot be empty.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")


def list_movies(movies, username):
    if not movies:
        print(f"\n{username}, your movie collection is empty. Add some movies!")
        return
    for m in movies:
        print(f"{m['title']} ({m['year']}) - {m['rating']}")


def add_movie(user_id):
    title = input("Title: ")
    year = int(input("Year: "))
    rating = float(input("Rating: ").replace(",", "."))
    movie_storage.add_movie(title, year, rating, user_id)


def delete_movie(user_id):
    title = input("Delete: ")
    movie_storage.delete_movie(title, user_id)


def update_movie(user_id):
    title = input("Movie: ")
    rating = float(input("New rating: "))
    movie_storage.update_movie(title, rating, user_id)


def add_movie_from_api(user_id):
    title = input("Movie title: ")
    data = fetch_movie(title)

    if data.get("Response") == "False":
        print("Not found.")
        return

    try:
        rating = float(data.get("imdbRating"))
    except:
        rating = 0

    try:
        year = int(data.get("Year", "0")[:4])
    except:
        year = 0

    movie_storage.add_movie(
        data.get("Title"),
        year,
        rating,
        user_id,
        data.get("Poster")
    )
    print("Added from OMDb!")


def stats(movies):
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
    if not movies:
        print("No movies available.")
        return
    movie = random.choice(movies)
    print(f"Random: {movie['title']} ({movie['year']}) - {movie['rating']}")


def search_movie(movies):
    query = input("Search: ").lower()
    results = [m for m in movies if query in m["title"].lower()]
    if not results:
        print("No matches found.")
        return
    for movie in results:
        print(f"{movie['title']} ({movie['year']}) - {movie['rating']}")


def movies_sorted_by_year(movies):
    for movie in sorted(movies, key=lambda x: x["year"], reverse=True):
        print(f"{movie['title']} ({movie['year']}) - {movie['rating']}")


def sorted_by_rating(movies):
    for movie in sorted(movies, key=lambda x: x["rating"], reverse=True):
        print(f"{movie['title']} - {movie['rating']}")


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


def generate_website(user_id, username):
    movies = movie_storage.get_movies(user_id)

    template_path = os.path.join(BASE_DIR, "_static", "index_template.html")
    output_path = os.path.join(BASE_DIR, "_static", f"{username}.html")

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    movie_grid = generate_movie_grid(movies)
    html = template.replace("__TEMPLATE_TITLE__", f"{username}'s Movie App")
    html = html.replace("__TEMPLATE_MOVIE_GRID__", movie_grid)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Website saved as {username}.html!")


def main():
    movie_storage.init_db()

    user_id, username = select_user()

    actions = {
        "1": lambda: list_movies(movie_storage.get_movies(user_id), username),
        "2": lambda: add_movie(user_id),
        "3": lambda: delete_movie(user_id),
        "4": lambda: update_movie(user_id),
        "5": lambda: stats(movie_storage.get_movies(user_id)),
        "6": lambda: random_movie(movie_storage.get_movies(user_id)),
        "7": lambda: search_movie(movie_storage.get_movies(user_id)),
        "8": lambda: sorted_by_rating(movie_storage.get_movies(user_id)),
        "9": lambda: movies_sorted_by_year(movie_storage.get_movies(user_id)),
        "10": lambda: add_movie_from_api(user_id),
        "11": lambda: generate_website(user_id, username),
        "12": lambda: switch_user(),
    }

    while True:
        print(f"\n[{username}]")
        print("0 Exit")
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
        print("12 Switch user")

        choice = input("Choice: ")

        if choice == "0":
            break

        if choice == "12":
            user_id, username = select_user()
            actions = {
                "1": lambda: list_movies(movie_storage.get_movies(user_id), username),
                "2": lambda: add_movie(user_id),
                "3": lambda: delete_movie(user_id),
                "4": lambda: update_movie(user_id),
                "5": lambda: stats(movie_storage.get_movies(user_id)),
                "6": lambda: random_movie(movie_storage.get_movies(user_id)),
                "7": lambda: search_movie(movie_storage.get_movies(user_id)),
                "8": lambda: sorted_by_rating(movie_storage.get_movies(user_id)),
                "9": lambda: movies_sorted_by_year(movie_storage.get_movies(user_id)),
                "10": lambda: add_movie_from_api(user_id),
                "11": lambda: generate_website(user_id, username),
                "12": lambda: switch_user(),
            }
            continue

        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()