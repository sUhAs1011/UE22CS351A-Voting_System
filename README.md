# DBMS Mini-Project

Our **DBMS Mini-Project**, titled *Voting System*, is an electronic voting platform developed as part of our fifth-semester coursework. This project leverages **Python** and **MySQL** as primary tools to implement a robust and secure voting system. The system uses **MySQL Connector** to establish a connection between Python and the database, enabling seamless CRUD (Create, Read, Update, Delete) operations using **DML (Data Manipulation Language)** commands.

The project comprises five main modules, each contributing to a comprehensive electronic voting system:

---

### **1. Sign-Up**
The **Sign-Up** module allows voters to register for the election process. During registration:
- Users provide their Aadhaar number, name, contact details, and other essential information.
- The system validates the details, ensuring only eligible voters (18+ years) are registered.
- A unique **Voter ID** is generated, which will be used for logging into the system.

---

### **2. Login**
The **Login** module serves as a portal for voters to access their accounts. Here:
- Voters provide their Aadhaar number, Voter ID, and password for authentication.
- Upon successful login, users can update their details or proceed to vote during the election period.

---

### **3. Party Registration**
This module is designed for candidates contesting in elections to:
- **Register their political party** with details like party name, symbol, and leader.
- Ensure that a party cannot be registered multiple times.
- Add or manage party candidates, provided the party leader is authenticated.

---

### **4. Voting & Viewing Results**
#### Voting:
- Authenticated voters cast their votes for candidates contesting in their respective districts.
- Once a vote is cast, it cannot be changed.

#### Viewing Results:
- The system calculates and displays election results in real-time.
- Voters can view the total votes garnered by each party in descending order of popularity.

---

### **5. Leave Portal**
The **Leave** option provides voters or candidates the ability to exit the portal safely after completing their tasks.

---

### **Key Features of the System**
- **Security:** Password-protected login ensures voter information is secure.
- **Data Integrity:** Parameterized queries protect against SQL injection attacks.
- **User Roles:** Distinct functionalities for voters and party leaders.
- **Comprehensive Validation:** Ensures data correctness (e.g., Aadhaar validation, age checks).

This project demonstrates our ability to integrate **Database Management Systems** with practical coding applications, fostering a secure and efficient digital election process.



