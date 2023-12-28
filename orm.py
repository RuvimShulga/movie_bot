from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()

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


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    from_user = Column(Integer)
    to_user = Column(Integer)
    family = Column(Integer)
    status = Column(String)


class Family(Base):
    __tablename__ = 'families'
    id = Column(Integer, primary_key=True)
    family_name = Column(String)
    owner = Column(Integer)


class UsersInFamily(Base):
    __tablename__ = "user_family"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    family_id = Column(Integer)
    
    
class UserRecommendation(Base):
    __tablename__ = "user_recommendation"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    recommended_movie_id = Column(Integer)


# Установка соединения с базой данных
engine = create_engine('sqlite:///movies.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

