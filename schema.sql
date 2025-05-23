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
INSERT INTO districts (name) VALUES ('North District');
INSERT INTO districts (name) VALUES ('South District');
INSERT INTO districts (name) VALUES ('East District');
INSERT INTO districts (name) VALUES ('West Central District');


-- Example Voter (update with DOB, email, district_id)
-- INSERT INTO voters (voter_id, aadhaar, password, name, dob, email, district_id) VALUES ('VOTER001', '123456789012', 'password123', 'John Doe', '1990-01-01', 'john.doe@example.com', 1);
-- INSERT INTO voters (voter_id, aadhaar, password, name, dob, email, district_id) VALUES ('VOTER002', '210987654321', 'securepass', 'Jane Smith', '1985-05-15', 'jane.smith@example.com', 2);

-- Example Parties
INSERT INTO parties (name, symbol_details, leader_info) VALUES ('Progressive Party', 'Star Symbol', 'Leader A');
INSERT INTO parties (name, symbol_details, leader_info) VALUES ('Liberty Alliance', 'Eagle Symbol', 'Leader B');
INSERT INTO parties (name, symbol_details, leader_info) VALUES ('Green Initiative', 'Tree Symbol', 'Leader C');
INSERT INTO parties (name, symbol_details, leader_info) VALUES ('Independent Group', 'Hand Symbol', 'Coordinator X');
INSERT INTO parties (name, symbol_details, leader_info) VALUES ('Future Forward Party', 'Arrow Symbol', 'Leader D');
