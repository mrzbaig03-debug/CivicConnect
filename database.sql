CREATE DATABASE civicconnect;

USE civicconnect;

CREATE TABLE representatives (

    rep_id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(100) UNIQUE,

    mobile VARCHAR(15) UNIQUE,

    ward_id INT NOT NULL,

    designation VARCHAR(50) DEFAULT 'Representative',

    password VARCHAR(255) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ward_id)
    REFERENCES wards(ward_id)

);

SHOW TABLES;

CREATE TABLE complaints (

    complaint_id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    ward_id INT NOT NULL,

    rep_id INT,

    category VARCHAR(100) NOT NULL,

    title VARCHAR(150) NOT NULL,

    description TEXT NOT NULL,

    image_path VARCHAR(255),

    status ENUM('Pending','In Progress','Resolved','Rejected')
    DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
    REFERENCES users(user_id),

    FOREIGN KEY (ward_id)
    REFERENCES wards(ward_id),

    FOREIGN KEY (rep_id)
    REFERENCES representatives(rep_id)

);

SHOW TABLES;

CREATE TABLE complaint_updates (

    update_id INT AUTO_INCREMENT PRIMARY KEY,

    complaint_id INT NOT NULL,

    updated_by VARCHAR(50),

    old_status VARCHAR(50),

    new_status VARCHAR(50),

    remarks TEXT,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (complaint_id)
    REFERENCES complaints(complaint_id)

);

SHOW TABLES;

CREATE TABLE admins (

    admin_id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(100) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

SHOW TABLES;

 USE civicconnect;

CREATE TABLE complaints (

    complaint_id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT,

    complaint_type VARCHAR(100) NOT NULL,

    complaint_title VARCHAR(150) NOT NULL,

    description TEXT NOT NULL,

    area VARCHAR(100) NOT NULL,

    ward_no INT NOT NULL,

    image VARCHAR(255),

    status VARCHAR(30) DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id)

); 

DESCRIBE complaints;

ALTER TABLE complaints
DROP FOREIGN KEY complaints_ibfk_2;

SHOW CREATE TABLE complaints;

DESCRIBE complaints;

ALTER TABLE complaints
ADD area VARCHAR(100) AFTER description;

SHOW CREATE TABLE complaints;

DESCRIBE users;

USE civicconnect;

DESCRIBE complaints;

SHOW TABLES;
DESCRIBE users;
DESCRIBE complaints;
DESCRIBE wards;
DESCRIBE representatives;
DESCRIBE announcements;
USE civicconnect;
SELECT * FROM wards;
USE civicconnect;

-- Wards
INSERT INTO wards (ward_number, ward_name, area_name) VALUES
(11, 'Ward 11', 'Islampura, Millat Nagar, Rehmat Nagar, Haider Bagh'),
(12, 'Ward 12', 'Bhagwan Gali, Umar Colony, Khudbe Nagar, Pakiza Nagar');

-- Representatives (Ward 11 → ward_id 1, Ward 12 → ward_id 2, agar wards table khali thi)
INSERT INTO representatives (full_name, email, mobile, ward_id, designation, password) VALUES
('Azam Khan', 'azam.khan@civicconnect.com', '9876543210', 1, 'Representative', 'rep123'),
('Ansar Khan', 'ansar.khan@civicconnect.com', '9876543211', 1, 'Representative', 'rep123'),
('Masood Khan', 'masood.khan@civicconnect.com', '9876543212', 1, 'Representative', 'rep123'),
('Rahim Khan', 'rahim.khan@civicconnect.com', '9876543213', 1, 'Representative', 'rep123'),
('Altaf Sir', 'altaf.sir@civicconnect.com', '9876543214', 2, 'Representative', 'rep123'),
('Ibrahim Khan', 'ibrahim.khan@civicconnect.com', '9876543215', 2, 'Representative', 'rep123'),
('Imran Khan', 'imran.khan@civicconnect.com', '9876543216', 2, 'Representative', 'rep123'),
('Abdul Gaffar', 'abdul.gaffar@civicconnect.com', '9876543217', 2, 'Representative', 'rep123');

USE civicconnect;

UPDATE representatives SET full_name='Sk Shadul', email='sk.shadul@civicconnect.com' WHERE email='azam.khan@civicconnect.com';
UPDATE representatives SET full_name='Sk Bilal', email='sk.bilal@civicconnect.com' WHERE email='ansar.khan@civicconnect.com';
UPDATE representatives SET full_name='Ayra Fatima', email='ayra.fatima@civicconnect.com' WHERE email='masood.khan@civicconnect.com';
UPDATE representatives SET full_name='Safura Fatima', email='safura.fatima@civicconnect.com' WHERE email='rahim.khan@civicconnect.com';

UPDATE representatives SET full_name='Sk Samir', email='sk.samir@civicconnect.com' WHERE email='altaf.sir@civicconnect.com';
UPDATE representatives SET full_name='Syed Yasir', email='syed.yasir@civicconnect.com' WHERE email='ibrahim.khan@civicconnect.com';
UPDATE representatives SET full_name='Hajra Begum', email='hajra.begum@civicconnect.com' WHERE email='imran.khan@civicconnect.com';
UPDATE representatives SET full_name='Khan Sadaf', email='khan.sadaf@civicconnect.com' WHERE email='abdul.gaffar@civicconnect.com';

SELECT * FROM representatives; 

USE civicconnect;

ALTER TABLE complaints
ADD COLUMN work_photo_path VARCHAR(255) NULL AFTER image_path;

USE civicconnect;

CREATE TABLE announcements (
    announcement_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    ward_id INT NULL,
    posted_by VARCHAR(100) DEFAULT 'CivicConnect Admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id)
);

USE civicconnect;

-- Add area column to representatives (each rep handles one specific area)
ALTER TABLE representatives
ADD COLUMN area VARCHAR(100) NULL AFTER ward_id;

-- Assign each representative to their specific area
UPDATE representatives SET area='Islampura' WHERE email='sk.shadul@civicconnect.com';
UPDATE representatives SET area='Millat Nagar' WHERE email='sk.bilal@civicconnect.com';
UPDATE representatives SET area='Rehmat Nagar' WHERE email='ayra.fatima@civicconnect.com';
UPDATE representatives SET area='Haider Bagh' WHERE email='safura.fatima@civicconnect.com';

UPDATE representatives SET area='Bhagwan Gali' WHERE email='sk.samir@civicconnect.com';
UPDATE representatives SET area='Umar Colony' WHERE email='syed.yasir@civicconnect.com';
UPDATE representatives SET area='Khudbe Nagar' WHERE email='hajra.begum@civicconnect.com';
UPDATE representatives SET area='Pakiza Nagar' WHERE email='khan.sadaf@civicconnect.com';

SELECT rep_id, full_name, area, ward_id FROM representatives;

USE civicconnect;

-- Add Ward 13 (Madina Nagar)
INSERT INTO wards (ward_number, ward_name, area_name)
VALUES (13, 'Ward 13', 'Madina Nagar');

-- Add 4 representatives (corporators) for Ward 13
INSERT INTO representatives (full_name, email, mobile, ward_id, area, designation, password) VALUES
('Aqeem Khan', 'aqeem.khan@civicconnect.com', '8766030046', (SELECT ward_id FROM wards WHERE ward_number = 13), 'Madina Nagar', 'Representative', 'rep123'),
('Azem Baig', 'azem.baig@civicconnect.com', '8993342666', (SELECT ward_id FROM wards WHERE ward_number = 13), 'Madina Nagar', 'Representative', 'rep123'),
('Nida Darr', 'nida.darr@civicconnect.com', '9991838343', (SELECT ward_id FROM wards WHERE ward_number = 13), 'Madina Nagar', 'Representative', 'rep123'),
('Mahin Sk', 'mahin.sk@civicconnect.com', '7837723932', (SELECT ward_id FROM wards WHERE ward_number = 13), 'Madina Nagar', 'Representative', 'rep123');

-- Verify
SELECT * FROM wards WHERE ward_number = 13;
SELECT rep_id, full_name, mobile, email, area FROM representatives WHERE ward_id = (SELECT ward_id FROM wards WHERE ward_number = 13);