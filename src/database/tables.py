from sqlalchemy import Column, Integer, String, Text, DateTime, MetaData, Table
from sqlalchemy.dialects import postgresql

# СПОСОБ 1
# служебный объект метаданных для описания таблиц ---------------------------------------------------------------------
meta = MetaData()

# Описание таблицы для Главного Меню
main_menu = Table('mainmenu', meta,
                  Column('id', Integer(), primary_key=True),
                  Column('title', String(64), nullable=False),
                  Column('url', String(256), nullable=False)
                  )
# Описание таблицы для Статей
posts = Table('posts', meta,
              Column('id', Integer(), primary_key=True),
              Column('title', String(256), nullable=False),
              Column('text', Text, nullable=False),
              Column('url', String(256), nullable=False),
              Column('time', DateTime, nullable=False)
              )

# описание таблицы для Пользователей
users = Table('users', meta,
              Column('id', Integer(), primary_key=True),
              Column('name', String(128), nullable=False),
              Column('email', String(128), nullable=False),
              Column('psw', String(256), nullable=False),
              Column('avatar', postgresql.BYTEA, nullable=True),
              Column('time', DateTime, nullable=False)
              )

# СПОСОБ 2
# объект для ВСЕХ таблиц базы для наследования классов таблиц -------------------------------------------------------
# from database.init import Base

# описание таблицы для Пользователей
# class Users(Base):
#     __tablename__ = 'users'
#     __table_args__ = {'extend_existing': True}  # продолжать, если таблица существует
#     id = Column(Integer(), primary_key=True)
#     name = Column(String(128), nullable=False)
#     email = Column(String(128), nullable=False)
#     psw = Column(String(256), nullable=False)
#     avatar = Column(postgresql.BYTEA, nullable=True)
#     time = Column(DateTime, nullable=False)
#
#
# # Описание таблицы для Статей
# class Posts(Base):
#     __tablename__ = 'posts'
#     __table_args__ = {'extend_existing': True}  # продолжать, если таблица существует
#     id = Column(Integer(), primary_key=True)
#     title = Column(String(256), nullable=False)
#     text = Column(Text, nullable=False)
#     url = Column(String(256), nullable=False)
#     time = Column(DateTime, nullable=False)
#
#
# # Описание таблицы для Главного Меню
# class MainMenu(Base):
#     __tablename__ = 'main_menu'
#     __table_args__ = {'extend_existing': True}  # продолжать, если таблица существует
#     id = Column(Integer(), autoincrement=True, primary_key=True, index=True)
#     title = Column(String(64), nullable=False, unique=True)
#     url = Column(String(256), nullable=False)
