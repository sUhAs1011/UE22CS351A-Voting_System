import streamlit as st
import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime, date # Added for age calculation

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'otp_generated' not in st.session_state:
    st.session_state.otp_generated = False
if 'otp_verified' not in st.session_state:
    st.session_state.otp_verified = False
if 'current_voter_id' not in st.session_state:
    st.session_state.current_voter_id = None
if 'current_voter_district_id' not in st.session_state: # For district-specific voting
    st.session_state.current_voter_district_id = None
if 'generated_otp_value' not in st.session_state:
    st.session_state.generated_otp_value = None
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# ---------------- Database Connection ----------------
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Suhas@#$10112003", # Ensure this is your actual password
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
        query_check = "SELECT * FROM voters WHERE aadhaar = %s OR voter_id = %s"
        cursor.execute(query_check, (aadhaar, voter_id))
        if cursor.fetchone():
            st.error("Aadhaar number or Voter ID already registered.")
            conn.close()
            return False
        
        age = calculate_age(dob)
        if age < 18:
            st.error("Voter must be at least 18 years old to register.")
            conn.close()
            return False

        query_insert = "INSERT INTO voters (name, aadhaar, voter_id, password, dob, email, district_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(query_insert, (name, aadhaar, voter_id, password, dob, email, district_id))
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
        query = "SELECT voter_id, name, district_id FROM voters WHERE aadhaar=%s AND voter_id=%s AND password=%s"
        cursor.execute(query, (aadhaar, voter_id, password))
        voter = cursor.fetchone()
        conn.close()
        return voter
    return None

# ---------------- Candidate Management ----------------
def get_candidates(district_id=None): # Can filter by district
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
            if e.errno == 1062: # Duplicate entry
                 st.error(f"Party name '{name}' already exists.")
            else:
                st.error(f"Failed to register party: {e}")
        finally:
            conn.close()

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

# ---------------- Results ----------------
def show_results():
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT cand.name as candidate_name, p.name as party_name, d.name as district_name, COUNT(v.vote_id) as total_votes
        FROM candidates cand
        LEFT JOIN votes v ON cand.candidate_id = v.candidate_id
        LEFT JOIN parties p ON cand.party_id = p.party_id
        LEFT JOIN districts d ON cand.district_id = d.district_id
        GROUP BY cand.candidate_id, p.name, d.name
        ORDER BY total_votes DESC, cand.name
        """
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        st.subheader("📊 Election Results")
        if results:
            # Consider pandas for better display if complex: pd.DataFrame(results)
            for res in results:
                st.write(f"🗳️ {res['candidate_name']} ({res['party_name'] if res['party_name'] else 'Independent'}) - District: {res['district_name'] if res['district_name'] else 'N/A'} - {res['total_votes']} vote(s)")
        else:
            st.write("No votes cast yet or no candidates with votes.")

# ---------------- UI ----------------
st.title("🗳️ Electronic Voting System")

menu_options = ["Voter Login", "Voter Sign Up", "Admin Panel", "View Results"]
menu = st.sidebar.selectbox("Menu", menu_options, key="main_menu")

# ---------- Voter Sign Up Panel ----------
if menu == "Voter Sign Up":
    st.subheader("📝 Voter Sign Up")
    districts_list = get_districts()
    district_options = {d['name']: d['district_id'] for d in districts_list}

    with st.form("signup_form"):
        name = st.text_input("Full Name")
        aadhaar = st.text_input("Aadhaar Number (12 digits)")
        voter_id = st.text_input("Create Voter ID (e.g., ABC1234567)")
        password = st.text_input("Create Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        dob = st.date_input("Date of Birth", min_value=date(1900,1,1), max_value=date.today())
        email = st.text_input("Email (Optional)")
        selected_district_name = st.selectbox("Select Your District", list(district_options.keys()))
        
        submitted = st.form_submit_button("Sign Up")

        if submitted:
            if not (name and aadhaar and voter_id and password and confirm_password and dob and selected_district_name):
                st.warning("Please fill all required fields.")
            elif len(aadhaar) != 12 or not aadhaar.isdigit():
                st.warning("Aadhaar number must be 12 digits.")
            elif password != confirm_password:
                st.warning("Passwords do not match.")
            else:
                district_id_to_save = district_options[selected_district_name]
                if register_voter(name, aadhaar, voter_id, password, dob, email, district_id_to_save):
                    st.rerun()

# ---------- Voter Panel (Login, OTP, Voting) ----------
elif menu == "Voter Login":
    st.subheader("🔐 Voter Panel")

    if st.session_state.logged_in and st.session_state.otp_verified:
        st.success(f"Welcome Voter {st.session_state.current_voter_id}! You can now cast your vote.")
        
        if check_if_voted(st.session_state.current_voter_id):
            st.info("You have already cast your vote. Thank you!")
        else:
            # Fetch candidates for the voter's district
            candidates = get_candidates(district_id=st.session_state.current_voter_district_id)
            if candidates:
                candidate_display_list = [f"{c['name']} ({c['party_name'] if c['party_name'] else 'Independent'})" for c in candidates]
                candidate_map = {f"{c['name']} ({c['party_name'] if c['party_name'] else 'Independent'})": c['candidate_id'] for c in candidates}

                st.write("Choose your candidate:")
                selected_candidate_display_name = st.radio(
                    "Candidates", candidate_display_list, key="candidate_radio_selection", label_visibility="collapsed"
                )
                if st.button("Cast Your Vote"):
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
            st.session_state.generated_otp_value = None
            st.rerun()

    elif st.session_state.otp_generated and not st.session_state.otp_verified:
        st.info(f"An OTP has been generated (for simulation): {st.session_state.generated_otp_value}")
        entered_otp = st.text_input("Enter OTP", key="otp_input_voter")
        if st.button("Verify OTP"):
            if verify_otp(entered_otp, st.session_state.generated_otp_value):
                st.session_state.otp_verified = True
                st.session_state.logged_in = True
                st.success("OTP Verified. Proceeding to vote.")
                st.rerun()
            else:
                st.error("Invalid OTP. Please try again or re-login.")
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
                        st.session_state.current_voter_district_id = voter_data['district_id'] # Store district_id
                        st.session_state.generated_otp_value = generate_otp_value()
                        st.session_state.otp_generated = True
                        st.success("Login successful! OTP generated.")
                        st.rerun()
                    else:
                        st.error("Invalid credentials or voter not found.")
                        st.session_state.otp_generated = False

# ---------- Admin Panel ----------
elif menu == "Admin Panel":
    st.subheader("🛠️ Admin Section")
    if not st.session_state.admin_logged_in:
        admin_user = st.text_input("Admin Username", key="admin_user_login")
        admin_pass = st.text_input("Admin Password", type="password", key="admin_pass_login")
        if st.button("Admin Login", key="admin_login_btn"):
            if authenticate_admin(admin_user, admin_pass):
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid admin credentials.")
    else:
        st.success("Admin login successful.")
        admin_menu_options = ["Add/View Candidate", "Register/View Party", "View Districts"]
        admin_action = st.sidebar.radio("Admin Actions", admin_menu_options, key="admin_action_radio")

        if admin_action == "Add/View Candidate":
            st.subheader("Manage Candidates")
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
                        party_id_to_save = party_options.get(selected_party_name) # Will be None if "Independent"
                        district_id_to_save_cand = district_options[selected_district_name_cand]
                        add_candidate(name, party_id_to_save, district_id_to_save_cand)
                        st.rerun()
                    else:
                        st.warning("Please enter candidate name and select district.")
            
            st.subheader("Registered Candidates")
            all_candidates = get_candidates() # Admin sees all
            if all_candidates:
                for cand in all_candidates:
                    st.write(f"ID: {cand['candidate_id']} | Name: {cand['name']} | Party: {cand['party_name'] if cand['party_name'] else 'Independent'} | District: {cand['district_name']}")
            else:
                st.info("No candidates registered yet.")

        elif admin_action == "Register/View Party":
            st.subheader("Manage Parties")
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
            
            st.subheader("Registered Parties")
            parties = get_parties()
            if parties:
                for p in parties:
                    st.write(f"ID: {p['party_id']} | Name: {p['name']} | Symbol: {p['symbol_details']} | Leader: {p['leader_info']}")
            else:
                st.info("No parties registered yet.")
        
        elif admin_action == "View Districts":
            st.subheader("Registered Districts")
            districts = get_districts()
            if districts:
                for d in districts:
                    st.write(f"ID: {d['district_id']} | Name: {d['name']}")
            else:
                st.info("No districts registered yet. (This should not happen if schema is correct)")

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
