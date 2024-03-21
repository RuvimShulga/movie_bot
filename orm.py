from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)

class Movies(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, unique=True)
    movie_name = Column(String)
    movie_rating = Column(Float)
    movie_year = Column(Integer)
    description = Column(String)
    url = Column(String)
    poster = Column(String)

class LikedMovies(Base):
    __tablename__ = "liked_movies"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    movie_id = Column(Integer)

class DislikedMovies(Base):
    __tablename__ = "disliked_movies"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    movie_id = Column(Integer)

class Collections(Base):
    __tablename__ = "collections"
    id = Column(Integer, primary_key=True)
    category = Column(String)
    name = Column(String)
    slug = Column(String)


# Установка соединения с базой данных
engine = create_engine('sqlite:///movies.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

