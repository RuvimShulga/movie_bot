import sqlite3

conn = sqlite3.connect('movies.db')
cursor = conn.cursor()


def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS liked_movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            liked_movie_id INTEGER UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disliked_movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            disliked_movie_id INTEGER UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER UNIQUE,
            movie_name TEXT,
            movie_rating NUMERIC,
            movie_year INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS family (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            family_name TEXT,
            owner_id INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_family (
            user_id INTEGER,
            family_id INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_recommendation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            recommended_movie_id INTEGER
        )
    ''')

    conn.commit()


def insert_liked(user_id, liked_movie_id):
    cursor.execute('''
        INSERT INTO liked_movies (user_id, liked_movie_id)
        VALUES(?, ?)   
        ''', (user_id, liked_movie_id))

    conn.commit()


def insert_disliked(user_id, disliked_movie_id):
    cursor.execute('''
        INSERT INTO disliked_movies (user_id, disliked_movie_id)
        VALUES(?, ?)   
        ''', (user_id, disliked_movie_id))

    conn.commit()


def insert_movie(movie_id, movie_name, movie_rating, movie_year):
    cursor.execute('''
        INSERT INTO movies (movie_id, movie_name, movie_rating, movie_year)
        VALUES(?, ?, ?, ?)
    ''', (movie_id, movie_name, movie_rating, movie_year))

    conn.commit()


def insert_family(family_name, owner_id):
    cursor.execute('''
        INSERT INTO family (family_name, owner_id)
        VALUES(?, ?)
    ''', (family_name, owner_id))

    conn.commit()


def insert_user_family(user_id, family_id):
    cursor.execute('''
        INSERT INTO user_family (user_id, family_id)
        VALUES(?, ?)
    ''', (user_id, family_id))

    conn.commit()


def insert_recommendation(user_id, recommended_movie_id):
    cursor.execute('''
        INSERT INTO user_recommendation (user_id, recommended_movie_id)
        VALUES(?, ?)
    ''', (user_id, recommended_movie_id))

    conn.commit()


def get_liked_movies_for_user(user_id):
    cursor.execute(f'''
        SELECT movies.movie_id, movies.movie_name FROM movies JOIN liked_movies ON movies.movie_id = liked_movies.liked_movie_id
        WHERE liked_movies.user_id == {user_id}
    ''')

    return cursor.fetchall()


def get_disliked_movies_for_user(user_id):
    cursor.execute(f'''
        SELECT movies.movie_id, movies.movie_name FROM movies JOIN disliked_movies ON movies.movie_id = disliked_movies.disliked_movie_id
        WHERE disliked_movies.user_id == {user_id}
    ''')

    return cursor.fetchall()




def print_liked():
    cursor.execute("SELECT * FROM liked_movies")
    rows = cursor.fetchall()
    for row in rows:
        print(row)


def print_disliked():
    cursor.execute("SELECT * FROM disliked_movies")
    rows = cursor.fetchall()
    for row in rows:
        print(row)


def print_movies():
    cursor.execute("SELECT * FROM movies")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
