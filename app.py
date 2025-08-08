import streamlit as st
import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime, date
import hashlib
import re

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'otp_generated' not in st.session_state:
    st.session_state.otp_generated = False
if 'otp_verified' not in st.session_state:
    st.session_state.otp_verified = False
if 'current_voter_id' not in st.session_state:
    st.session_state.current_voter_id = None
if 'current_voter_district_id' not in st.session_state:
    st.session_state.current_voter_district_id = None
if 'current_voter_name' not in st.session_state:
    st.session_state.current_voter_name = None
if 'generated_otp_value' not in st.session_state:
    st.session_state.generated_otp_value = None
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# ---------------- Security & Validation Functions ----------------
def hash_password(password):
    """Hash password using SHA-256 for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_aadhaar(aadhaar):
    """Validate Aadhaar number format"""
    if not aadhaar.isdigit() or len(aadhaar) != 12:
        return False
    return True

def validate_email(email):
    """Validate email format"""
    if not email:
        return True  # Email is optional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_voter_id(voter_id):
    """Validate Voter ID format (alphanumeric, 8-12 characters)"""
    if len(voter_id) < 8 or len(voter_id) > 12:
        return False
    if not re.match(r'^[A-Za-z0-9]+$', voter_id):
        return False
    return True

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

# ---------------- Database Connection ----------------
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Suhas@#$10112003",
            database="voting"
        )
    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None

# ---------------- Helper: Calculate Age ----------------
def calculate_age(born_date):
    if born_date is None:
        return 0
    today = date.today()
    return today.year - born_date.year - ((today.month, today.day) < (born_date.month, born_date.day))

# ---------------- Helper: Get Districts ----------------
def get_districts():
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT district_id, name FROM districts ORDER BY name")
        districts = cursor.fetchall()
        conn.close()
        return districts
    return []

# ---------------- Helper: Get Parties ----------------
def get_parties():
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT party_id, name FROM parties ORDER BY name")
        parties = cursor.fetchall()
        conn.close()
        return parties
    return []

# ---------------- Admin Authentication ----------------
def authenticate_admin(username, password):
    return username == "admin" and password == "admin123"

# ---------------- Voter Registration ----------------
def register_voter(name, aadhaar, voter_id, password, dob, email, district_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        
        # Enhanced validation
        if not validate_aadhaar(aadhaar):
            st.error("Invalid Aadhaar number format. Must be 12 digits.")
            conn.close()
            return False
            
        if not validate_voter_id(voter_id):
            st.error("Invalid Voter ID format. Must be 8-12 alphanumeric characters.")
            conn.close()
            return False
            
        if not validate_email(email):
            st.error("Invalid email format.")
            conn.close()
            return False
        
        # Check for existing aadhaar or voter_id
        query_check = "SELECT * FROM voters WHERE aadhaar = %s OR voter_id = %s"
        cursor.execute(query_check, (aadhaar, voter_id))
        if cursor.fetchone():
            st.error("Aadhaar number or Voter ID already registered.")
            conn.close()
            return False
        
        # Age validation
        age = calculate_age(dob)
        if age < 18:
            st.error("Voter must be at least 18 years old to register.")
            conn.close()
            return False

        # Hash password for security
        hashed_password = hash_password(password)
        
        query_insert = "INSERT INTO voters (name, aadhaar, voter_id, password, dob, email, district_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(query_insert, (name, aadhaar, voter_id, hashed_password, dob, email, district_id))
            conn.commit()
            st.success("Voter registered successfully! Please login.")
            conn.close()
            return True
        except Error as e:
            st.error(f"Registration failed: {e}")
            conn.close()
            return False
    return False

# ---------------- Voter Authentication ----------------
def authenticate_voter(aadhaar, voter_id, password):
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        hashed_password = hash_password(password)
        query = "SELECT voter_id, name, district_id FROM voters WHERE aadhaar=%s AND voter_id=%s AND password=%s"
        cursor.execute(query, (aadhaar, voter_id, hashed_password))
        voter = cursor.fetchone()
        conn.close()
        return voter
    return None

# ---------------- Update Voter Details ----------------
def update_voter_details(voter_id, name, email, district_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            query = "UPDATE voters SET name = %s, email = %s, district_id = %s WHERE voter_id = %s"
            cursor.execute(query, (name, email, district_id, voter_id))
            conn.commit()
            st.success("Voter details updated successfully!")
            return True
        except Error as e:
            st.error(f"Failed to update details: {e}")
            return False
        finally:
            conn.close()
    return False

# ---------------- Candidate Management ----------------
def get_candidates(district_id=None):
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT c.candidate_id, c.name, p.name as party_name, d.name as district_name 
            FROM candidates c
            LEFT JOIN parties p ON c.party_id = p.party_id
            LEFT JOIN districts d ON c.district_id = d.district_id
        """
        params = []
        if district_id:
            query += " WHERE c.district_id = %s"
            params.append(district_id)
        query += " ORDER BY c.name"
        cursor.execute(query, params)
        candidates = cursor.fetchall()
        conn.close()
        return candidates
    return []

def add_candidate(name, party_id, district_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO candidates (name, party_id, district_id) VALUES (%s, %s, %s)", (name, party_id, district_id))
            conn.commit()
            st.success(f"Candidate {name} added successfully!")
        except Error as e:
            st.error(f"Failed to add candidate: {e}")
        finally:
            conn.close()

# ---------------- Party Management ---------------------
def add_party(name, symbol, leader):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO parties (name, symbol_details, leader_info) VALUES (%s, %s, %s)", (name, symbol, leader))
            conn.commit()
            st.success(f"Party '{name}' registered successfully!")
        except Error as e:
            if e.errno == 1062:  # Duplicate entry
                st.error(f"Party name '{name}' already exists.")
            else:
                st.error(f"Failed to register party: {e}")
        finally:
            conn.close()

def get_party_statistics():
    """Get party-wise vote statistics"""
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT p.name as party_name, COUNT(v.vote_id) as total_votes
        FROM parties p
        LEFT JOIN candidates c ON p.party_id = c.party_id
        LEFT JOIN votes v ON c.candidate_id = v.candidate_id
        GROUP BY p.party_id, p.name
        ORDER BY total_votes DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
    return []

# ---------------- OTP Generation (Value Only) ----------------
def generate_otp_value():
    return random.randint(100000, 999999)

# ---------------- OTP Verification ----------------
def verify_otp(entered_otp, expected_otp):
    return str(entered_otp) == str(expected_otp)

# ---------------- Check if Voted ----------------
def check_if_voted(voter_id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM votes WHERE voter_id = %s", (voter_id,))
        has_voted = cursor.fetchone() is not None
        conn.close()
        return has_voted
    return False

# ---------------- Cast Vote ----------------
def cast_vote(voter_id, candidate_id):
    if check_if_voted(voter_id):
        st.warning("You have already voted.")
        return
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO votes (voter_id, candidate_id) VALUES (%s, %s)", (voter_id, candidate_id))
            conn.commit()
            st.success("Your vote has been cast successfully.")
        except Error as e:
            st.error(f"Failed to cast vote: {e}")
        finally:
            conn.close()

# ---------------- Enhanced Results ----------------
def show_results():
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Individual candidate results
        query_candidates = """
        SELECT cand.name as candidate_name, p.name as party_name, d.name as district_name, COUNT(v.vote_id) as total_votes
        FROM candidates cand
        LEFT JOIN votes v ON cand.candidate_id = v.candidate_id
        LEFT JOIN parties p ON cand.party_id = p.party_id
        LEFT JOIN districts d ON cand.district_id = d.district_id
        GROUP BY cand.candidate_id, p.name, d.name
        ORDER BY total_votes DESC, cand.name
        """
        cursor.execute(query_candidates)
        candidate_results = cursor.fetchall()
        
        # Party-wise statistics
        party_stats = get_party_statistics()
        
        # District-wise statistics
        query_districts = """
        SELECT d.name as district_name, COUNT(v.vote_id) as total_votes
        FROM districts d
        LEFT JOIN candidates c ON d.district_id = c.district_id
        LEFT JOIN votes v ON c.candidate_id = v.candidate_id
        GROUP BY d.district_id, d.name
        ORDER BY total_votes DESC
        """
        cursor.execute(query_districts)
        district_results = cursor.fetchall()
        
        conn.close()
        
        st.subheader("📊 Election Results")
        
        # Party-wise Results
        st.write("### 🏛️ Party-wise Results")
        if party_stats:
            for party in party_stats:
                st.write(f"🏛️ **{party['party_name']}**: {party['total_votes']} votes")
        else:
            st.write("No party statistics available.")
        
        st.write("---")
        
        # District-wise Results
        st.write("### 🗺️ District-wise Results")
        if district_results:
            for district in district_results:
                st.write(f"🗺️ **{district['district_name']}**: {district['total_votes']} votes")
        else:
            st.write("No district statistics available.")
        
        st.write("---")
        
        # Individual Candidate Results
        st.write("### 👥 Individual Candidate Results")
        if candidate_results:
            for res in candidate_results:
                st.write(f"🗳️ **{res['candidate_name']}** ({res['party_name'] if res['party_name'] else 'Independent'}) - District: {res['district_name'] if res['district_name'] else 'N/A'} - **{res['total_votes']} votes**")
        else:
            st.write("No votes cast yet or no candidates with votes.")

# ---------------- UI ----------------
st.title("🗳️ Electronic Voting System")
st.markdown("### Secure • Transparent • Reliable")

# Add system status
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("System Status", "🟢 Online")
with col2:
    st.metric("Security Level", "🔒 High")
with col3:
    st.metric("Database", "🟢 Connected")

menu_options = ["Voter Login", "Voter Sign Up", "Admin Panel", "View Results"]
menu = st.sidebar.selectbox("Menu", menu_options, key="main_menu")

# ---------- Voter Sign Up Panel ----------
if menu == "Voter Sign Up":
    st.subheader("📝 Voter Registration")
    st.info("Please provide accurate information. All fields marked with * are required.")
    
    districts_list = get_districts()
    district_options = {d['name']: d['district_id'] for d in districts_list}

    with st.form("signup_form"):
        name = st.text_input("Full Name *")
        aadhaar = st.text_input("Aadhaar Number (12 digits) *")
        voter_id = st.text_input("Create Voter ID (8-12 alphanumeric characters) *")
        password = st.text_input("Create Password *", type="password")
        confirm_password = st.text_input("Confirm Password *", type="password")
        dob = st.date_input("Date of Birth *", min_value=date(1900,1,1), max_value=date.today())
        email = st.text_input("Email (Optional)")
        selected_district_name = st.selectbox("Select Your District *", list(district_options.keys()))
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            # Enhanced validation
            if not (name and aadhaar and voter_id and password and confirm_password and dob and selected_district_name):
                st.warning("Please fill all required fields.")
            elif not validate_aadhaar(aadhaar):
                st.warning("Aadhaar number must be exactly 12 digits.")
            elif not validate_voter_id(voter_id):
                st.warning("Voter ID must be 8-12 alphanumeric characters.")
            elif password != confirm_password:
                st.warning("Passwords do not match.")
            elif not validate_email(email):
                st.warning("Please enter a valid email address.")
            else:
                # Password strength validation
                is_strong, message = validate_password_strength(password)
                if not is_strong:
                    st.warning(message)
                else:
                    district_id_to_save = district_options[selected_district_name]
                    if register_voter(name, aadhaar, voter_id, password, dob, email, district_id_to_save):
                        st.rerun()

# ---------- Voter Panel (Login, OTP, Voting) ----------
elif menu == "Voter Login":
    st.subheader("🔐 Voter Authentication")

    if st.session_state.logged_in and st.session_state.otp_verified:
        st.success(f"Welcome, {st.session_state.current_voter_name}!")
        
        # Voter Dashboard
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Voter ID:** {st.session_state.current_voter_id}")
            st.write(f"**District:** {st.session_state.current_voter_district_id}")
        with col2:
            if check_if_voted(st.session_state.current_voter_id):
                st.warning("⚠️ You have already voted")
            else:
                st.success("✅ Eligible to vote")
        
        # Update Profile Option
        if st.expander("Update Profile"):
            with st.form("update_profile"):
                new_name = st.text_input("Name", value=st.session_state.current_voter_name)
                new_email = st.text_input("Email")
                districts_list = get_districts()
                district_options = {d['name']: d['district_id'] for d in districts_list}
                new_district = st.selectbox("District", list(district_options.keys()))
                
                if st.form_submit_button("Update Profile"):
                    district_id = district_options[new_district]
                    if update_voter_details(st.session_state.current_voter_id, new_name, new_email, district_id):
                        st.session_state.current_voter_name = new_name
                        st.session_state.current_voter_district_id = district_id
                        st.rerun()
        
        # Voting Section
        if check_if_voted(st.session_state.current_voter_id):
            st.info("You have already cast your vote. Thank you!")
        else:
            st.write("### 🗳️ Cast Your Vote")
            candidates = get_candidates(district_id=st.session_state.current_voter_district_id)
            if candidates:
                candidate_display_list = [f"{c['name']} ({c['party_name'] if c['party_name'] else 'Independent'})" for c in candidates]
                candidate_map = {f"{c['name']} ({c['party_name'] if c['party_name'] else 'Independent'})": c['candidate_id'] for c in candidates}

                selected_candidate_display_name = st.radio(
                    "Choose your candidate:", candidate_display_list, key="candidate_radio_selection"
                )
                
                if st.button("Cast Your Vote", type="primary"):
                    if selected_candidate_display_name:
                        selected_candidate_id = candidate_map[selected_candidate_display_name]
                        cast_vote(st.session_state.current_voter_id, selected_candidate_id)
                        st.rerun()
            else:
                st.warning("No candidates available for your district at the moment.")

        if st.button("Logout", key="voter_logout"):
            st.session_state.logged_in = False
            st.session_state.otp_generated = False
            st.session_state.otp_verified = False
            st.session_state.current_voter_id = None
            st.session_state.current_voter_district_id = None
            st.session_state.current_voter_name = None
            st.session_state.generated_otp_value = None
            st.rerun()

    elif st.session_state.otp_generated and not st.session_state.otp_verified:
        st.info(f"🔐 OTP Verification Required")
        st.info(f"An OTP has been generated (for simulation): **{st.session_state.generated_otp_value}**")
        entered_otp = st.text_input("Enter OTP", key="otp_input_voter")
        if st.button("Verify OTP"):
            if verify_otp(entered_otp, st.session_state.generated_otp_value):
                st.session_state.otp_verified = True
                st.session_state.logged_in = True
                st.success("✅ OTP Verified. Proceeding to vote.")
                st.rerun()
            else:
                st.error("❌ Invalid OTP. Please try again.")
    else: 
        with st.form("login_form"):
            st.subheader("Login to Vote")
            aadhaar = st.text_input("Aadhaar Number")
            voter_id = st.text_input("Voter ID")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if not (aadhaar and voter_id and password):
                    st.warning("Please enter all credentials.")
                else:
                    voter_data = authenticate_voter(aadhaar, voter_id, password)
                    if voter_data:
                        st.session_state.current_voter_id = voter_data['voter_id']
                        st.session_state.current_voter_district_id = voter_data['district_id']
                        st.session_state.current_voter_name = voter_data['name']
                        st.session_state.generated_otp_value = generate_otp_value()
                        st.session_state.otp_generated = True
                        st.success("✅ Login successful! OTP generated.")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials or voter not found.")
                        st.session_state.otp_generated = False

# ---------- Admin Panel ----------
elif menu == "Admin Panel":
    st.subheader("🛠️ Administrative Panel")
    
    if not st.session_state.admin_logged_in:
        st.info("Please login with admin credentials to access administrative functions.")
        admin_user = st.text_input("Admin Username", key="admin_user_login")
        admin_pass = st.text_input("Admin Password", type="password", key="admin_pass_login")
        if st.button("Admin Login", key="admin_login_btn"):
            if authenticate_admin(admin_user, admin_pass):
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ Invalid admin credentials.")
    else:
        st.success("✅ Admin login successful.")
        
        # Admin Dashboard
        col1, col2, col3 = st.columns(3)
        with col1:
            districts = get_districts()
            st.metric("Districts", len(districts))
        with col2:
            parties = get_parties()
            st.metric("Parties", len(parties))
        with col3:
            candidates = get_candidates()
            st.metric("Candidates", len(candidates))
        
        admin_menu_options = ["Add/View Candidate", "Register/View Party", "View Districts", "System Statistics"]
        admin_action = st.sidebar.radio("Admin Actions", admin_menu_options, key="admin_action_radio")

        if admin_action == "Add/View Candidate":
            st.subheader("👥 Manage Candidates")
            parties_list = get_parties()
            party_options = {p['name']: p['party_id'] for p in parties_list}
            districts_list = get_districts()
            district_options = {d['name']: d['district_id'] for d in districts_list}

            with st.form("add_candidate_form"):
                name = st.text_input("Candidate Name", key="cand_name_input")
                selected_party_name = st.selectbox("Select Party", ["Independent"] + list(party_options.keys()), key="cand_party_select")
                selected_district_name_cand = st.selectbox("Select District", list(district_options.keys()), key="cand_dist_select")
                add_candidate_submit = st.form_submit_button("Add Candidate")
                if add_candidate_submit:
                    if name and selected_district_name_cand:
                        party_id_to_save = party_options.get(selected_party_name)
                        district_id_to_save_cand = district_options[selected_district_name_cand]
                        add_candidate(name, party_id_to_save, district_id_to_save_cand)
                        st.rerun()
                    else:
                        st.warning("Please enter candidate name and select district.")
            
            st.subheader("📋 Registered Candidates")
            all_candidates = get_candidates()
            if all_candidates:
                for cand in all_candidates:
                    st.write(f"🆔 **{cand['candidate_id']}** | 👤 **{cand['name']}** | 🏛️ **{cand['party_name'] if cand['party_name'] else 'Independent'}** | 🗺️ **{cand['district_name']}**")
            else:
                st.info("No candidates registered yet.")

        elif admin_action == "Register/View Party":
            st.subheader("🏛️ Manage Political Parties")
            with st.form("add_party_form"):
                p_name = st.text_input("Party Name", key="party_name_input")
                p_symbol = st.text_input("Symbol Details (e.g., description or image URL)", key="party_symbol_input")
                p_leader = st.text_input("Leader Information", key="party_leader_input")
                add_party_submit = st.form_submit_button("Register Party")
                if add_party_submit:
                    if p_name:
                        add_party(p_name, p_symbol, p_leader)
                        st.rerun()
                    else:
                        st.warning("Party name is required.")
            
            st.subheader("📋 Registered Parties")
            parties = get_parties()
            if parties:
                for p in parties:
                    st.write(f"🆔 **{p['party_id']}** | 🏛️ **{p['name']}** | 🎯 **{p['symbol_details']}** | 👑 **{p['leader_info']}**")
            else:
                st.info("No parties registered yet.")
        
        elif admin_action == "View Districts":
            st.subheader("🗺️ Registered Districts")
            districts = get_districts()
            if districts:
                for d in districts:
                    st.write(f"🆔 **{d['district_id']}** | 🗺️ **{d['name']}**")
            else:
                st.info("No districts registered yet.")
        
        elif admin_action == "System Statistics":
            st.subheader("📊 System Statistics")
            
            # Party Statistics
            party_stats = get_party_statistics()
            if party_stats:
                st.write("### 🏛️ Party-wise Vote Distribution")
                for party in party_stats:
                    st.write(f"🏛️ **{party['party_name']}**: {party['total_votes']} votes")
            
            # Total votes cast
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as total_votes FROM votes")
                total_votes = cursor.fetchone()[0]
                conn.close()
                st.write(f"### 📈 Total Votes Cast: **{total_votes}**")

        if st.sidebar.button("Admin Logout", key="admin_logout_btn"):
            st.session_state.admin_logged_in = False
            st.rerun()

# ---------- Results Panel ----------
elif menu == "View Results":
    show_results()

# Clear OTP related session state if user navigates away
if menu != "Voter Login" and st.session_state.otp_generated and not st.session_state.otp_verified:
    st.session_state.otp_generated = False
    st.session_state.generated_otp_value = None

# Footer
st.markdown("---")
st.markdown("**Electronic Voting System** | Secure • Transparent • Reliable")
st.markdown("Developed as part of DBMS Mini-Project | Fifth Semester")
