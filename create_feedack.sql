CREATE TABLE feedback (
	id SERIAL NOT NULL,
	isbn VARCHAR NOT NULL,
	email VARCHAR NOT NULL,
	review VARCHAR NOT NULL,
	rating INT NOT NULL
);