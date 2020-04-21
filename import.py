import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://nyloivhoqwkqwg:6bf9b91d56209291c3602fb221334901397ee8dcde4ef5b60948d4c10dd567ff@ec2-18-206-84-251.compute-1.amazonaws.com:5432/db53goqjqef7kq")
db = scoped_session(sessionmaker(bind=engine))

if __name__ == "__main__":
    reader = csv.reader(open("books.csv"))
    print("before")
    i = 1
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO book_details (isbn, title, author, publication_year) VALUES (:isbn, :title, :author, :year)",{"isbn": isbn, "title": title, "author": author, "year": year})
        print(i)
        i = i+1
    print("after")

    db.commit()
