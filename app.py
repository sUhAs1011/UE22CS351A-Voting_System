import streamlit as st
import mysql.connector
from mysql.connector import Error
import random

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'otp_generated' not in st.session_state:
    st.session_state.otp_generated = False
if 'otp_verified' not in st.session_state:
    st.session_state.otp_verified = False
if 'current_voter_id' not in st.session_state:
    st.session_state.current_voter_id = None
if 'generated_otp_value' not in st.session_state:
    st.session_state.generated_otp_value = None

# ---------------- Database Connection ----------------
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Suhas@#$10112003",  # Reset to placeholder
            database="evoting_db"
        )
    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None

# ---------------- Admin Authentication ----------------
def authenticate_admin(username, password):
    return username == "admin" and password == "admin123"

# ---------------- Voter Registration ----------------
def register_voter(name, aadhaar, voter_id, password):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        # Check for existing aadhaar or voter_id
        query_check = "SELECT * FROM voters WHERE aadhaar = %s OR voter_id = %s"
        cursor.execute(query_check, (aadhaar, voter_id))
        if cursor.fetchone():
            st.error("Aadhaar number or Voter ID already registered.")
            conn.close()
            return False
        
        query_insert = "INSERT INTO voters (name, aadhaar, voter_id, password) VALUES (%s, %s, %s, %s)"
        try:
            cursor.execute(query_insert, (name, aadhaar, voter_id, password))
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
        cursor = conn.cursor(dictionary=True) # Fetch as dict
        query = "SELECT * FROM voters WHERE aadhaar=%s AND voter_id=%s AND password=%s"
        cursor.execute(query, (aadhaar, voter_id, password))
        voter = cursor.fetchone()
        conn.close()
        return voter # Returns voter data as dict or None
    return None

# ---------------- Candidate Management ----------------
def get_candidates():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT candidate_id, name, party FROM candidates")
        candidates = cursor.fetchall()
        conn.close()
        return candidates
    return []

def add_candidate(name, party):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO candidates (name, party) VALUES (%s, %s)", (name, party))
        conn.commit()
        conn.close()
        st.success(f"Candidate {name} added successfully!")

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
    return False # Assume not voted if DB error

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
        cursor = conn.cursor()
        query = """
        SELECT c.name, c.party, COUNT(v.vote_id) as total_votes
        FROM candidates c
        LEFT JOIN votes v ON c.candidate_id = v.candidate_id
        GROUP BY c.candidate_id
        ORDER BY total_votes DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        st.subheader("📊 Election Results")
        if results:
            for name, party, votes in results:
                st.write(f"🗳️ {name} ({party}) - {votes} vote(s)")
        else:
            st.write("No votes cast yet or no candidates.")

# ---------------- UI ----------------
st.title("🗳️ Electronic Voting System")

menu_options = ["Voter Login", "Voter Sign Up", "Admin Panel", "View Results"]
menu = st.sidebar.selectbox("Menu", menu_options)

# ---------- Voter Sign Up Panel ----------
if menu == "Voter Sign Up":
    st.subheader("📝 Voter Sign Up")
    with st.form("signup_form"):
        name = st.text_input("Full Name")
        aadhaar = st.text_input("Aadhaar Number (12 digits)")
        voter_id = st.text_input("Voter ID (e.g., ABC1234567)")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Sign Up")

        if submitted:
            if not (name and aadhaar and voter_id and password and confirm_password):
                st.warning("Please fill all fields.")
            elif len(aadhaar) != 12 or not aadhaar.isdigit():
                st.warning("Aadhaar number must be 12 digits.")
            elif password != confirm_password:
                st.warning("Passwords do not match.")
            else:
                if register_voter(name, aadhaar, voter_id, password):
                    # Optionally switch to login or show success message
                    pass


# ---------- Voter Panel (Login, OTP, Voting) ----------
elif menu == "Voter Login":
    st.subheader("🔐 Voter Panel")

    if st.session_state.logged_in and st.session_state.otp_verified:
        # ---- Voting Panel ----
        st.success(f"Welcome Voter {st.session_state.current_voter_id}! You can now cast your vote.")
        
        if check_if_voted(st.session_state.current_voter_id):
            st.info("You have already cast your vote. Thank you!")
        else:
            candidates = get_candidates()
            if candidates:
                # Create a list of display names for radio options and a mapping to their IDs
                candidate_display_list = [f"{cname} ({cparty})" for cid, cname, cparty in candidates]
                candidate_map = {f"{cname} ({cparty})": cid for cid, cname, cparty in candidates}

                st.write("Choose your candidate:") # Label for the radio group
                selected_candidate_display_name = st.radio(
                    "Candidates", 
                    candidate_display_list, 
                    key="candidate_radio_selection",
                    label_visibility="collapsed" # Hide the default "Candidates" label for st.radio itself
                )

                if st.button("Cast Your Vote"):
                    if selected_candidate_display_name:
                        selected_candidate_id = candidate_map[selected_candidate_display_name]
                        cast_vote(st.session_state.current_voter_id, selected_candidate_id)
                        st.rerun() # Rerun to update voted status
                    else:
                        st.warning("Please select a candidate before casting your vote.") # Should not happen with radio
            else:
                st.warning("No candidates available for voting at the moment.")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.otp_generated = False
            st.session_state.otp_verified = False
            st.session_state.current_voter_id = None
            st.session_state.generated_otp_value = None
            st.rerun()

    elif st.session_state.otp_generated and not st.session_state.otp_verified:
        # ---- OTP Verification Step ----
        st.info(f"An OTP has been generated (for simulation): {st.session_state.generated_otp_value}")
        entered_otp = st.text_input("Enter OTP", key="otp_input_voter")
        if st.button("Verify OTP"):
            if verify_otp(entered_otp, st.session_state.generated_otp_value):
                st.session_state.otp_verified = True
                st.session_state.logged_in = True # Mark as fully logged in
                st.success("OTP Verified. Proceeding to vote.")
                st.rerun()
            else:
                st.error("Invalid OTP. Please try again or re-login.")
                # Optionally allow re-login by resetting otp_generated state
                # st.session_state.otp_generated = False 
                # st.rerun()


    else: # Initial Login Step
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
                    voter = authenticate_voter(aadhaar, voter_id, password)
                    if voter:
                        st.session_state.current_voter_id = voter['voter_id'] # Store voter_id from dict
                        st.session_state.generated_otp_value = generate_otp_value()
                        st.session_state.otp_generated = True
                        st.success("Login successful! OTP generated.")
                        st.rerun()
                    else:
                        st.error("Invalid credentials or voter not found.")
                        st.session_state.otp_generated = False # Ensure reset if login fails

# ---------- Admin Panel ----------
elif menu == "Admin Panel":
    st.subheader("🛠️ Admin Login")
    admin_user = st.text_input("Admin Username", key="admin_user_login")
    admin_pass = st.text_input("Admin Password", type="password", key="admin_pass_login")

    if st.button("Admin Login", key="admin_login_btn"):
        if authenticate_admin(admin_user, admin_pass):
            st.success("Admin login successful.")
            st.session_state.admin_logged_in = True
        else:
            st.error("Invalid admin credentials.")
            st.session_state.admin_logged_in = False

    if st.session_state.get('admin_logged_in', False):
        admin_option = st.radio("Select Option", ["Add Candidate", "View Candidates"], key="admin_options")
        
        if admin_option == "Add Candidate":
            with st.form("add_candidate_form"):
                name = st.text_input("Candidate Name", key="cand_name_input")
                party = st.text_input("Party Name", key="cand_party_input")
                add_candidate_submit = st.form_submit_button("Add Candidate")
                if add_candidate_submit:
                    if name and party:
                        add_candidate(name, party)
                        st.rerun()
                    else:
                        st.warning("Please enter all candidate details.")
        elif admin_option == "View Candidates":
            candidates = get_candidates()
            if candidates:
                st.subheader("🧾 Registered Candidates")
                for cid, cname, cparty in candidates:
                    st.write(f"ID: {cid} | Name: {cname} | Party: {cparty}")
            else:
                st.info("No candidates registered yet.")
        
        if st.button("Admin Logout", key="admin_logout_btn"):
            st.session_state.admin_logged_in = False
            st.rerun()


# ---------- Results Panel ----------
elif menu == "View Results":
    show_results()

# Clear OTP related session state if user navigates away from Voter Login before OTP verification
if menu != "Voter Login" and st.session_state.otp_generated and not st.session_state.otp_verified:
    st.session_state.otp_generated = False
    st.session_state.generated_otp_value = None
    # st.session_state.current_voter_id = None # Decide if voter_id should be cleared too
    # st.rerun() # Consider if a rerun is needed here too
