CREATE TABLE voters (
    voter_id VARCHAR(255) NOT NULL PRIMARY KEY,
    aadhaar VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) -- Added a name column as it's generally useful
);

CREATE TABLE candidates (
    candidate_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    party VARCHAR(255) NOT NULL
);

CREATE TABLE votes (
    vote_id INT AUTO_INCREMENT PRIMARY KEY,
    voter_id VARCHAR(255) NOT NULL,
    candidate_id INT NOT NULL,
    FOREIGN KEY (voter_id) REFERENCES voters(voter_id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
    UNIQUE(voter_id) -- Ensures a voter can only vote once
);

-- Optional: Add some initial admin/voter data for testing

-- Example Admin (though admin authentication in the script is not DB based)
-- INSERT INTO voters (voter_id, aadhaar, password, name) VALUES ('admin_user', '000000000000', 'admin_password', 'Admin User');

-- Example Voter
INSERT INTO voters (voter_id, aadhaar, password, name) VALUES ('VOTER001', '123456789012', 'password123', 'John Doe');
INSERT INTO voters (voter_id, aadhaar, password, name) VALUES ('VOTER002', '210987654321', 'securepass', 'Jane Smith');

-- Example Candidates
INSERT INTO candidates (name, party) VALUES ('Alice Wonderland', 'People's Party');
INSERT INTO candidates (name, party) VALUES ('Bob The Builder', 'Constructive Party');
INSERT INTO candidates (name, party) VALUES ('Charlie Brown', 'Good Grief Party'); 