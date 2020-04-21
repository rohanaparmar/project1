# Project 1

Web Programming with Python and JavaScript

This project is based on book's review by different user
So in this website
	User can registered
	User can login and logout
	User can Search for book by it's title or by isbn no or by author name
	Then user can review that book which user want to review
	
For this features for website database is added and which type of structure of tables are shown in sql files.
In database.py
from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

engine = create_engine("postgres://username:password@server/database")
db = scoped_session(sessionmaker(bind=engine))

I used database.py because there is problem with environment variable DATABASE_URL

So to run this project developer has to put his/her own username, password, server name and database that is related to his/her database