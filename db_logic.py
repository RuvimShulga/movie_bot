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
