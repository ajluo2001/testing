-- Boat Reservation Schema.

DROP SCHEMA IF EXISTS reservation CASCADE;
CREATE SCHEMA reservation;
SET SEARCH_PATH to reservation;

-- the skippers.
CREATE TABLE Skippers (
   sID INT PRIMARY KEY,
   -- The id of the skipper.
   sName VARCHAR(50) NOT NULL,
   -- the name of the skipper
   age INT NOT NULL CHECK (age > 0),
   -- the age of the skipper
   rating DECIMAL NOT NULL CHECK (5>=rating>=0)
);

-- the boat model
CREATE TABLE Model (
   mID INT PRIMARY KEY, 
   -- The id of the boat model
   length DECIMAL NOT NULL CHECK (length > 0)
   -- the length of the boat
);

-- the boat reservation
CREATE TABLE Reservation (
   sID INT NOT NULL REFERENCES Skippers,
   -- The sID of the boat
   day timestamp NOT NULL,
   -- the day of the reservation
   mID INT NOT NULL REFERENCES Model,
   -- model id of the boat that is reserved 
   dID INT NOT NULL,
   -- the dock id
   PRIMARY KEY (sID, day)

);
