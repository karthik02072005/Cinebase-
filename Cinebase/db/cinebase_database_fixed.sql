
DROP DATABASE IF EXISTS cinebase;
CREATE DATABASE cinebase;
USE cinebase;

CREATE TABLE IF NOT EXISTS Industry (
    Industry_ID INT AUTO_INCREMENT PRIMARY KEY,
    Industry_Name VARCHAR(100) NOT NULL UNIQUE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Genre (
    Genre_ID INT AUTO_INCREMENT PRIMARY KEY,
    Genre_Name VARCHAR(50) NOT NULL UNIQUE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Person (
    Person_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Date_of_Birth DATE,
    Role_Type ENUM('Actor', 'Director', 'Writer', 'Music Director') NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Movies (
    Movie_ID INT AUTO_INCREMENT PRIMARY KEY,
    Title_English VARCHAR(255) NOT NULL,
    Release_Year YEAR NOT NULL,
    Duration_Min INT,
    Plot_Summary TEXT,
    IMDB_Rating DECIMAL(2, 1),
    Industry_ID INT,
    FOREIGN KEY (Industry_ID) REFERENCES Industry(Industry_ID)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Box_Office (
    Box_Office_ID INT AUTO_INCREMENT PRIMARY KEY,
    Movie_ID INT UNIQUE,
    Budget_INR_Cr DECIMAL(10, 2),
    Revenue_INR_Cr DECIMAL(10, 2),
    FOREIGN KEY (Movie_ID) REFERENCES Movies(Movie_ID) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Movie_Genre (
    Movie_ID INT,
    Genre_ID INT,
    PRIMARY KEY (Movie_ID, Genre_ID),
    FOREIGN KEY (Movie_ID) REFERENCES Movies(Movie_ID) ON DELETE CASCADE,
    FOREIGN KEY (Genre_ID) REFERENCES Genre(Genre_ID) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Movie_Person_Role (
    Movie_ID INT,
    Person_ID INT,
    Role_Description VARCHAR(100),
    PRIMARY KEY (Movie_ID, Person_ID),
    FOREIGN KEY (Movie_ID) REFERENCES Movies(Movie_ID) ON DELETE CASCADE,
    FOREIGN KEY (Person_ID) REFERENCES Person(Person_ID) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Award (
    Award_ID INT AUTO_INCREMENT PRIMARY KEY,
    Award_Name VARCHAR(255) NOT NULL,
    Award_Year YEAR NOT NULL,
    Movie_ID INT,
    Person_ID INT,
    FOREIGN KEY (Movie_ID) REFERENCES Movies(Movie_ID),
    FOREIGN KEY (Person_ID) REFERENCES Person(Person_ID)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO Industry (Industry_ID, Industry_Name) VALUES
(1, 'Bollywood'),
(2, 'Kollywood'),
(3, 'Tollywood'),
(4, 'Sandalwood'),
(5, 'Hollywood');

INSERT IGNORE INTO Genre (Genre_Name) VALUES
('Action'), ('Drama'), ('Romance'), ('Comedy'), ('Thriller'), ('Epic'), ('Fantasy'), ('Historical'), ('Biopic');

INSERT IGNORE INTO Person (Name, Date_of_Birth, Role_Type) VALUES
('Shah Rukh Khan', '1965-11-02', 'Actor'), 
('S.S. Rajamouli', '1973-10-10', 'Director'), 
('Prabhas', '1979-10-23', 'Actor'),
('Deepika Padukone', '1986-01-05', 'Actor'), 
('Atlee', '1986-09-21', 'Director'),
('Anushka Shetty', '1981-11-07', 'Actor'),
('Yash', '1986-01-08', 'Actor'),
('Nagarjuna', '1959-08-29', 'Actor'),
('Vetrimaaran', '1975-09-04', 'Director'),
('Ranveer Singh', '1985-07-06', 'Actor'),
('Sanjay Leela Bhansali', '1963-02-24', 'Director');

DROP TRIGGER IF EXISTS trg_after_movie_insert_create_box_office;
DELIMITER //
CREATE TRIGGER trg_after_movie_insert_create_box_office
AFTER INSERT ON Movies
FOR EACH ROW
BEGIN
    INSERT INTO Box_Office (Movie_ID, Budget_INR_Cr, Revenue_INR_Cr)
    VALUES (NEW.Movie_ID, NULL, NULL)
    ON DUPLICATE KEY UPDATE Movie_ID = NEW.Movie_ID;
END;
//
DELIMITER ;

INSERT INTO Movies (Title_English, Release_Year, Duration_Min, IMDB_Rating, Industry_ID, Plot_Summary) VALUES
('Jawan', 2023, 169, 7.0, 1, 'A soldier is out to correct the wrongs in society.'),
('Baahubali: The Beginning', 2015, 159, 8.0, 3, 'A son fights to reclaim his rightful throne from a cruel uncle.'),
('Pathaan', 2023, 146, 5.9, 1, 'An exiled RAW agent battles a notorious terror outfit.'),
('Bigil', 2019, 179, 7.5, 2, 'A former football player coaches a women''s team to overcome adversity.'),
('K.G.F: Chapter 1', 2018, 155, 8.2, 4, 'A gangster rises to power in the Kolar Gold Fields.'),
('Avatar', 2009, 162, 7.9, 5, 'A paraplegic marine is dispatched to the moon Pandora on a unique mission.'),
('Padmaavat', 2018, 164, 7.0, 1, 'Queen Padmavati defends her honor against a tyrannical ruler.'),
('Master', 2021, 179, 7.8, 2, 'An alcoholic professor confronts a ruthless gangster.'),
('RRR', 2022, 187, 8.0, 3, 'Two legendary revolutionaries fight for their country against British rule.'),
('War', 2019, 154, 6.5, 1, 'An Indian soldier goes rogue, and his mentor must hunt him down.');


UPDATE Box_Office SET Budget_INR_Cr = 300.00, Revenue_INR_Cr = 1150.00 WHERE Movie_ID = 1;
UPDATE Box_Office SET Budget_INR_Cr = 180.00, Revenue_INR_Cr = 650.00 WHERE Movie_ID = 2;
UPDATE Box_Office SET Budget_INR_Cr = 225.00, Revenue_INR_Cr = 1050.00 WHERE Movie_ID = 3;
UPDATE Box_Office SET Budget_INR_Cr = 180.00, Revenue_INR_Cr = 300.00 WHERE Movie_ID = 4;
UPDATE Box_Office SET Budget_INR_Cr = 80.00, Revenue_INR_Cr = 250.00 WHERE Movie_ID = 5;
UPDATE Box_Office SET Budget_INR_Cr = 1900.00, Revenue_INR_Cr = 29237.06 WHERE Movie_ID = 6;
UPDATE Box_Office SET Budget_INR_Cr = 215.00, Revenue_INR_Cr = 585.00 WHERE Movie_ID = 7;
UPDATE Box_Office SET Budget_INR_Cr = 135.00, Revenue_INR_Cr = 300.00 WHERE Movie_ID = 8;
UPDATE Box_Office SET Budget_INR_Cr = 550.00, Revenue_INR_Cr = 1200.00 WHERE Movie_ID = 9;
UPDATE Box_Office SET Budget_INR_Cr = 175.00, Revenue_INR_Cr = 475.00 WHERE Movie_ID = 10;


INSERT INTO Movie_Genre (Movie_ID, Genre_ID) VALUES
(1, 1), (1, 5), (3, 1), (3, 5), -- Jawan, Pathaan: Action, Thriller
(2, 1), (2, 2),                  -- Baahubali: Action, Drama
(4, 2), (4, 4),                  -- Bigil: Drama, Comedy
(5, 1), (5, 5),                  
(6, 1), (6, 7),                  
(7, 2), (7, 3), (7, 8),          
(8, 1), (8, 5),                  
(9, 1), (9, 6), (9, 2),          
(10, 1), (10, 5);                

INSERT INTO Movie_Person_Role (Movie_ID, Person_ID, Role_Description) VALUES
(1, (SELECT Person_ID FROM Person WHERE Name='Shah Rukh Khan'), 'Lead Actor'), 
(1, (SELECT Person_ID FROM Person WHERE Name='Atlee'), 'Director'), 
(2, (SELECT Person_ID FROM Person WHERE Name='Prabhas'), 'Lead Actor'), 
(2, (SELECT Person_ID FROM Person WHERE Name='S.S. Rajamouli'), 'Director'), 
(3, (SELECT Person_ID FROM Person WHERE Name='Shah Rukh Khan'), 'Lead Actor'), 
(3, (SELECT Person_ID FROM Person WHERE Name='Deepika Padukone'), 'Lead Actress'), 
(4, (SELECT Person_ID FROM Person WHERE Name='Prabhas'), 'Lead Actor'),
(4, (SELECT Person_ID FROM Person WHERE Name='Atlee'), 'Director'),
(7, (SELECT Person_ID FROM Person WHERE Name='Deepika Padukone'), 'Lead Actress'), 
(7, (SELECT Person_ID FROM Person WHERE Name='Sanjay Leela Bhansali'), 'Director'),
(9, (SELECT Person_ID FROM Person WHERE Name='S.S. Rajamouli'), 'Director'),
(10, (SELECT Person_ID FROM Person WHERE Name='Shah Rukh Khan'), 'Lead Actor'); 


INSERT INTO Award (Movie_ID, Award_Name, Award_Year) VALUES
(1, 'Filmfare Best Actor', 2024),
(2, 'National Film Award for Best Feature Film', 2016),
(7, 'National Film Award for Best Music Direction', 2018),
(9, 'Golden Globe Best Original Song', 2023),
(10, 'Filmfare Best Action', 2020);