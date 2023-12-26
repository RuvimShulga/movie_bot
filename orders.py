from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    from_user = Column(Integer)
    to_user = Column(Integer)
    status = Column(String)


# Установка соединения с базой данных
engine = create_engine('sqlite:///movies.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

