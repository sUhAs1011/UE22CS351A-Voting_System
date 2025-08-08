CREATE TABLE districts (
    district_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE voters (
    voter_id VARCHAR(255) NOT NULL PRIMARY KEY,
    aadhaar VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    email VARCHAR(255) NULL,
    district_id INT NULL,
    FOREIGN KEY (district_id) REFERENCES districts(district_id)
);

CREATE TABLE parties (
    party_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    symbol_details VARCHAR(255) NULL, -- For symbol description or URL
    leader_info VARCHAR(255) NULL    -- For party leader details
);

CREATE TABLE candidates (
    candidate_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    party_id INT NULL,
    district_id INT NULL,
    FOREIGN KEY (party_id) REFERENCES parties(party_id),
    FOREIGN KEY (district_id) REFERENCES districts(district_id)
);

CREATE TABLE votes (
    vote_id INT AUTO_INCREMENT PRIMARY KEY,
    voter_id VARCHAR(255) NOT NULL,
    candidate_id INT NOT NULL,
    FOREIGN KEY (voter_id) REFERENCES voters(voter_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
    UNIQUE(voter_id) -- Ensures a voter can only vote once
);

-- Optional: Add some initial admin/voter data for testing (Update as needed)

-- Example Districts
INSERT INTO districts (name) VALUES ('Bangalore North');
INSERT INTO districts (name) VALUES ('Bangalore South');
INSERT INTO districts (name) VALUES ('Bangalore Central');
INSERT INTO districts (name) VALUES ('Bangalore Rural');


-- Example Voter (update with DOB, email, district_id)
-- INSERT INTO voters (voter_id, aadhaar, password, name, dob, email, district_id) VALUES ('VOTER001', '123456789012', 'password123', 'John Doe', '1990-01-01', 'john.doe@example.com', 1);
-- INSERT INTO voters (voter_id, aadhaar, password, name, dob, email, district_id) VALUES ('VOTER002', '210987654321', 'securepass', 'Jane Smith', '1985-05-15', 'jane.smith@example.com', 2);

-- Example Parties
INSERT INTO parties (name, symbol_details, leader_info) VALUES ('Bharatiya Janata Party', 'Lotus Symbol', 'Leader A');
INSERT INTO parties (name, symbol_details, leader_info) VALUES ('Indian National Congress', 'Hand Symbol', 'Leader B');
INSERT INTO parties (name, symbol_details, leader_info) VALUES ('Janata Dal (Secular)', 'Woman Symbol', 'Leader C');


-- Example Candidates for each district
-- North District Candidates
INSERT INTO candidates (name, party_id, district_id) VALUES ('Rahul Sharma', 1, 1); -- Progressive Party, North District
INSERT INTO candidates (name, party_id, district_id) VALUES ('Priya Patel', 2, 1);  -- Liberty Alliance, North District
INSERT INTO candidates (name, party_id, district_id) VALUES ('Amit Kumar', 4, 1);   -- Independent Group, North District

-- South District Candidates
INSERT INTO candidates (name, party_id, district_id) VALUES ('Sneha Reddy', 3, 2); -- Green Initiative, South District
INSERT INTO candidates (name, party_id, district_id) VALUES ('Vikram Singh', 5, 2); -- Future Forward Party, South District
INSERT INTO candidates (name, party_id, district_id) VALUES ('Meera Iyer', 1, 2);   -- Progressive Party, South District

-- East District Candidates
INSERT INTO candidates (name, party_id, district_id) VALUES ('Arjun Das', 2, 3);   -- Liberty Alliance, East District
INSERT INTO candidates (name, party_id, district_id) VALUES ('Zara Khan', 3, 3);   -- Green Initiative, East District
INSERT INTO candidates (name, party_id, district_id) VALUES ('Raj Malhotra', 5, 3); -- Future Forward Party, East District

-- West Central District Candidates
INSERT INTO candidates (name, party_id, district_id) VALUES ('Anjali Gupta', 1, 4); -- Progressive Party, West Central District
INSERT INTO candidates (name, party_id, district_id) VALUES ('Karan Verma', 2, 4);  -- Liberty Alliance, West Central District
INSERT INTO candidates (name, party_id, district_id) VALUES ('Neha Joshi', 4, 4);   -- Independent Group, West Central District
INSERT INTO candidates (name, party_id, district_id) VALUES ('Ravi Tiwari', 3, 4);  -- Green Initiative, West Central District 