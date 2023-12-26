import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect('movies.db')
        self.cursor = self.connection.cursor()

    def delete_orders(self):
        with self.connection:
            self.cursor.execute("delete from orders")

    def add_user(self, user_id, username):
        with self.connection:
            self.cursor.execute("INSERT INTO users(user_id, username) VALUES(?, ?)", (user_id, username))

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchmany(1)
        return bool(len(result))
    
    def get_user_id(self, username):
        with self.connection:
            return self.cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,)).fetchmany(1)[0][0]

    def get_username(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,)).fetchmany(1)[0][0]

    def insert_liked(self, user_id, liked_movie_id):
        with self.connection:
            self.cursor.execute('''
                INSERT INTO liked_movies (user_id, liked_movie_id)
                VALUES(?, ?)   
                ''', (user_id, liked_movie_id))


    def insert_disliked(self, user_id, disliked_movie_id):
        with self.connection:
            self.cursor.execute('''
                INSERT INTO disliked_movies (user_id, disliked_movie_id)
                VALUES(?, ?)   
                ''', (user_id, disliked_movie_id))


    def insert_movie(self, movie_id, movie_name, movie_rating, movie_year):
        with self.connection:
            self.cursor.execute('''
                INSERT INTO movies (movie_id, movie_name, movie_rating, movie_year)
                VALUES(?, ?, ?, ?)
            ''', (movie_id, movie_name, movie_rating, movie_year))


    def insert_family(self, family_name, owner_id):
        with self.connection:
            self.cursor.execute('''
                INSERT INTO family (family_name, owner_id)
                VALUES(?, ?)
            ''', (family_name, owner_id))


    def insert_user_family(self, user_id, family_id):
        with self.connection:
            self.cursor.execute('''
                INSERT INTO user_family (user_id, family_id)
                VALUES(?, ?)
            ''', (user_id, family_id))


    def insert_recommendation(self, user_id, recommended_movie_id):
        with self.connection:
            self.cursor.execute('''
                INSERT INTO user_recommendation (user_id, recommended_movie_id)
                VALUES(?, ?)
            ''', (user_id, recommended_movie_id))


    def delete_liked(self, user_id, liked_movie_id):
        with self.connection:
            self.cursor.execute(f'''
                DELETE FROM liked_movies WHERE user_id = {user_id} and movie_id = {liked_movie_id}
            ''') 


    def get_liked_movies_for_user(self, user_id):
        with self.connection:
            result = self.cursor.execute(f'''
                SELECT movies.movie_id, movies.movie_name FROM movies JOIN liked_movies ON movies.movie_id = liked_movies.liked_movie_id
                WHERE liked_movies.user_id == {user_id}
            ''').fetchall()

        return result


    def get_disliked_movies_for_user(self, user_id):
        with self.connection:
            result = self.cursor.execute(f'''
                SELECT movies.movie_id, movies.movie_name FROM movies JOIN disliked_movies ON movies.movie_id = disliked_movies.disliked_movie_id
                WHERE disliked_movies.user_id == {user_id}
            ''').fetchall()

        return result

