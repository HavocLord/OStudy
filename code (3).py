import streamlit as st
import json
import time
from pathlib import Path
import hashlib # Using hashlib just for user file naming, bcrypt for passwords
import bcrypt
from gtts import gTTS
import io
from PIL import Image # For potential future logo/image use

# --- Configuration & Constants ---
USER_DATA_DIR = Path(".user_data") # Directory to store user "databases" (INSECURE)
USER_DATA_DIR.mkdir(exist_ok=True) # Create dir if it doesn't exist
SESSION_TIMEOUT_SECONDS = 15 * 60 # 15 minutes idle timeout approximation

# --- Syllabus Structure (Placeholder - Needs massive content population) ---
# This is the core data structure. You MUST populate this extensively.
syllabus = {
    "Mathematics": {
        "Algebra": {
            "Quadratic Equations": {
                "detail": """
                    **Introduction:**
                    A quadratic equation is a polynomial equation of the second degree. The general form is ax² + bx + c = 0, where x represents an unknown, and a, b, and c represent known numbers, with a ≠ 0.

                    **Methods of Solving:**
                    1.  **Factorization:** Expressing the quadratic as a product of two linear factors.
                    2.  **Completing the Square:** Manipulating the equation to form a perfect square.
                    3.  **Quadratic Formula:** x = [-b ± sqrt(b² - 4ac)] / (2a). Derived from completing the square.

                    **Discriminant:**
                    The term b² - 4ac is called the discriminant (Δ). It tells us about the nature of the roots:
                    *   Δ > 0: Two distinct real roots.
                    *   Δ = 0: One real root (or two equal real roots).
                    *   Δ < 0: Two complex conjugate roots (no real roots).

                    **Examples:**
                    *   Solve x² - 5x + 6 = 0 by factorization: (x-2)(x-3) = 0 => x=2 or x=3.
                    *   Solve 2x² + 4x - 1 = 0 using the formula: x = [-4 ± sqrt(4² - 4*2*(-1))] / (2*2) = [-4 ± sqrt(24)] / 4 = [-4 ± 2*sqrt(6)] / 4 = [-1 ± sqrt(6)/2].
                """,
                "notes": """
                    *   **Key Formula:** x = [-b ± sqrt(b² - 4ac)] / (2a)
                    *   **Discriminant:** Δ = b² - 4ac (Nature of roots)
                    *   **Factorization:** Quickest if easily factorable.
                    *   **Remember:** 'a' cannot be zero.
                """,
                "flashcards": [
                    {"q": "General form of a quadratic equation?", "a": "ax² + bx + c = 0, a ≠ 0"},
                    {"q": "What is the quadratic formula?", "a": "x = [-b ± sqrt(b² - 4ac)] / (2a)"},
                    {"q": "What does the discriminant (Δ) tell us?", "a": "The nature of the roots (real/distinct, real/equal, complex)"},
                    {"q": "What is Δ if roots are real and equal?", "a": "Δ = 0"},
                ]
            },
            "Simultaneous Equations": {
                "detail": "Placeholder: Detailed explanation of solving linear and non-linear simultaneous equations...",
                "notes": "Placeholder: Key methods (Substitution, Elimination)...",
                "flashcards": [{"q": "Placeholder Q", "a": "Placeholder A"}]
            }
            # ... more Algebra subtopics
        },
        "Geometry": {
            "Circle Theorems": {
                "detail": "Placeholder: Angle at center, angle in semicircle, angles in same segment, cyclic quadrilaterals...",
                "notes": "Placeholder: Diagrams and key theorems...",
                "flashcards": [{"q": "Placeholder Q", "a": "Placeholder A"}]
            }
            # ... more Geometry subtopics
        }
        # ... more Maths topics
    },
    "Physics": {
        "Mechanics": {
            "Kinematics": {
                "detail": "Placeholder: Speed, velocity, acceleration, equations of motion (suvat)...",
                "notes": "Placeholder: Definitions, formulas, graphs (d-t, v-t)...",
                "flashcards": [{"q": "Define velocity", "a": "Rate of change of displacement"}]
            },
            # ... more Mechanics subtopics
        },
         # ... more Physics topics (e.g., Thermal Physics, Waves, Electricity)
    },
    "Chemistry": {
        "Atomic Structure": {
             "Protons, Neutrons, Electrons": {
                  "detail": "Placeholder: Location, relative mass, relative charge...",
                  "notes": "Placeholder: Key table, isotopes definition...",
                  "flashcards": [{"q": "Relative charge of electron?", "a": "-1"}]
             }
             # ...
        }
        # ... more Chemistry topics (e.g., Mole Concept, Periodic Table, Organic Chem)
    },
    "Computer Science": {
        "Programming Concepts": {
             "Variables and Data Types": {
                 "detail": "Placeholder: Integers, floats, strings, booleans, variable assignment...",
                 "notes": "Placeholder: Naming conventions, type casting...",
                 "flashcards": [{"q": "What is an integer?", "a": "A whole number"}]
             }
             # ... more Programming subtopics
        }
        # ... more CS topics (e.g., Hardware, Networking, Databases)
    },
    "Biology": {
         "Cell Biology": {
              "Animal vs Plant Cells": {
                   "detail": "Placeholder: Diagrams, organelles (nucleus, mitochondria, chloroplasts, cell wall...)",
                   "notes": "Placeholder: Key differences table...",
                   "flashcards": [{"q": "Function of chloroplasts?", "a": "Photosynthesis"}]
              }
              # ...
         }
         # ... more Biology topics (e.g., Transport, Respiration, Genetics)
    },
    "English": {
         "Composition": {
             "Narrative Writing": {
                 "detail": "Placeholder: Structure, character development, plot, setting, descriptive language...",
                 "notes": "Placeholder: Planning techniques, useful vocabulary...",
                 "flashcards": [{"q": "What is a plot?", "a": "The sequence of events in a story"}]
            }
         }
        # ... more English topics (e.g., Comprehension, Summary, Grammar)
    },
    "Pakistan Studies": {
         "History": {
              "The Pakistan Movement": {
                    "detail": "Placeholder: Key events, personalities (Allama Iqbal, Quaid-e-Azam), Lahore Resolution...",
                    "notes": "Placeholder: Timeline, key dates...",
                    "flashcards": [{"q": "When was the Lahore Resolution passed?", "a": "1940"}]
              }
              # ...
         }
         # ... more Pak Studies topics (e.g., Geography, Culture)
    },
    "Islamiat": {
        "Quranic Passages": {
             "Surah Al-Fatiha": {
                 "detail": "Placeholder: Translation, context, key themes...",
                 "notes": "Placeholder: Importance, main points...",
                 "flashcards": [{"q": "How many verses in Surah Al-Fatiha?", "a": "7"}]
             }
             # ...
        }
        # ... more Islamiat topics (e.g., Hadith, Pillars of Islam, History)
    },
}

# --- Helper Functions ---

def get_user_db_path(username):
    """Generates a filename based on username hash."""
    # Use hash to avoid potentially problematic chars in filenames
    username_hash = hashlib.sha256(username.encode()).hexdigest()[:16]
    return USER_DATA_DIR / f"{username_hash}.json"

def load_user_data():
    """Loads user credentials from the (insecure) user directory."""
    users = {}
    for user_file in USER_DATA_DIR.glob("*.json"):
        try:
            with open(user_file, 'r') as f:
                data = json.load(f)
                # Basic check if structure is as expected
                if "username" in data and "hashed_password" in data:
                     users[data["username"]] = data["hashed_password"]
        except (json.JSONDecodeError, IOError, KeyError):
            st.warning(f"Could not load or parse user file: {user_file.name}. Skipping.")
            # Optional: Add logic to handle corrupted files (e.g., delete or move)
    return users

def save_user_data(username, hashed_password):
    """Saves/updates a user's data in their individual (insecure) file."""
    user_file = get_user_db_path(username)
    user_info = {
        "username": username,
        "hashed_password": hashed_password.decode('utf-8') # Store hash as string
    }
    try:
        with open(user_file, 'w') as f:
            json.dump(user_info, f)
        return True
    except IOError:
        st.error("Failed to save user data.")
        return False

def hash_password(password):
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(stored_hash, provided_password):
    """Verifies a provided password against a stored bcrypt hash."""
    try:
        # bcrypt hashes are stored as strings, need to encode back to bytes
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))
    except ValueError: # Handle potential issues with invalid hash format
        return False

def generate_tts_audio(text):
    """Generates TTS audio bytes using gTTS."""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0) # Rewind file pointer
        return audio_fp.read()
    except Exception as e:
        st.error(f"Failed to generate audio: {e}")
        return None

def update_study_time(start_time_key="study_start_time"):
    """Calculates elapsed time and adds to total, resets start time."""
    if st.session_state.get(start_time_key) is not None:
        elapsed = time.time() - st.session_state[start_time_key]
        st.session_state.total_study_time += elapsed
        # Reset start time so it's not counted multiple times on reruns
        st.session_state[start_time_key] = None

# --- Initialize Session State ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.current_subject = None
    st.session_state.current_topic = None
    st.session_state.current_subtopic = None
    st.session_state.flashcard_index = 0
    st.session_state.flashcard_side = 'q' # 'q' for question, 'a' for answer
    st.session_state.total_study_time = 0.0
    st.session_state.last_interaction_time = time.time()
    st.session_state.study_start_time = None # When user starts viewing specific content


# --- Login/Registration Logic ---
if not st.session_state.logged_in:
    st.set_page_config(page_title="O-Level Study Hub - Login", layout="centered")
    st.title("📚 O-Level Study Hub")
    st.write("Welcome! Please log in or register.")

    users = load_user_data()
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            login_username = st.text_input("Username", key="login_user")
            login_password = st.text_input("Password", type="password", key="login_pass")
            login_button = st.form_submit_button("Login")

            if login_button:
                if login_username in users and verify_password(users[login_username], login_password):
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.session_state.last_interaction_time = time.time()
                    st.session_state.total_study_time = 0.0 # Reset study time on login
                    st.success("Login successful!")
                    st.rerun() # Rerun to show the main app
                else:
                    st.error("Incorrect username or password.")

    with register_tab:
         with st.form("register_form"):
            reg_username = st.text_input("Choose Username", key="reg_user")
            reg_password = st.text_input("Choose Password", type="password", key="reg_pass")
            reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm")
            register_button = st.form_submit_button("Register")

            if register_button:
                if not reg_username or not reg_password:
                    st.warning("Please enter both username and password.")
                elif reg_password != reg_password_confirm:
                    st.warning("Passwords do not match.")
                elif reg_username in users:
                    st.warning("Username already exists.")
                elif len(reg_password) < 6:
                     st.warning("Password must be at least 6 characters long.")
                else:
                    hashed = hash_password(reg_password)
                    if save_user_data(reg_username, hashed):
                        st.success(f"User '{reg_username}' registered successfully! Please log in.")
                        # Optionally clear form or switch tab
                    else:
                        st.error("Registration failed. Could not save user data.")
# --- Main Application (Logged In) ---
else:
    st.set_page_config(page_title=f"Study Hub - {st.session_state.username}", layout="wide")

    # --- Idle Time Check ---
    # Crude approximation: Check time since last interaction *during* a new interaction
    now = time.time()
    idle_duration = now - st.session_state.last_interaction_time
    if idle_duration > SESSION_TIMEOUT_SECONDS:
        # Don't log out automatically, just note potential idle time
        st.toast(f"Welcome back! You were inactive for ~{idle_duration/60:.1f} minutes.", icon="👋")
        # Add logic here if you want to track *confirmed* idle time vs active study time
    st.session_state.last_interaction_time = now # Update last interaction time

    # --- Sidebar Navigation ---
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.username}!")
        st.markdown("---")

        # Subject Selection
        st.header("My Subjects")
        selected_subject = st.radio(
            "Choose a subject:",
            options=list(syllabus.keys()),
            key="subject_selector",
            index=list(syllabus.keys()).index(st.session_state.current_subject) if st.session_state.current_subject else 0,
            format_func=lambda x: f"🎓 {x}" # Add emoji
        )

        # Update session state if subject changed
        if selected_subject != st.session_state.current_subject:
            update_study_time() # Stop timer for previous content
            st.session_state.current_subject = selected_subject
            st.session_state.current_topic = None # Reset lower levels
            st.session_state.current_subtopic = None
            st.session_state.flashcard_index = 0
            st.rerun() # Rerun to update topic list

        # Topic/Subtopic Selection (conditional)
        if st.session_state.current_subject:
            st.markdown("---")
            st.subheader(f"Topics in {st.session_state.current_subject}")
            subject_topics = list(syllabus[st.session_state.current_subject].keys())
            if subject_topics:
                 selected_topic = st.selectbox(
                     "Select Topic:",
                     options=subject_topics,
                     key="topic_selector",
                     index=subject_topics.index(st.session_state.current_topic) if st.session_state.current_topic else 0
                 )
                 if selected_topic != st.session_state.current_topic:
                      update_study_time() # Stop timer
                      st.session_state.current_topic = selected_topic
                      st.session_state.current_subtopic = None # Reset subtopic
                      st.session_state.flashcard_index = 0
                      st.rerun()

            if st.session_state.current_topic:
                st.markdown("---")
                st.subheader(f"Subtopics in {st.session_state.current_topic}")
                topic_subtopics = list(syllabus[st.session_state.current_subject][st.session_state.current_topic].keys())
                if topic_subtopics:
                    selected_subtopic = st.radio(
                         "Select Subtopic:",
                         options=topic_subtopics,
                         key="subtopic_selector",
                         index=topic_subtopics.index(st.session_state.current_subtopic) if st.session_state.current_subtopic else 0
                    )
                    if selected_subtopic != st.session_state.current_subtopic:
                         update_study_time() # Stop timer
                         st.session_state.current_subtopic = selected_subtopic
                         st.session_state.flashcard_index = 0
                         st.session_state.study_start_time = time.time() # Start timer for new content
                         st.rerun()
                else:
                     st.write("No subtopics available for this topic yet.")

        # Study Time Display
        st.markdown("---")
        st.header("Study Stats")
        total_seconds = st.session_state.total_study_time
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        st.metric("Approx. Study Time", f"{int(hours)}h {int(minutes)}m {int(seconds)}s")
        st.caption("Time spent actively viewing content.")


        # Logout Button
        st.markdown("---")
        if st.button("Logout", type="primary"):
            update_study_time() # Record time before logging out
            # Save progress/stats before logging out if needed (e.g., to user file)
            st.session_state.logged_in = False
            st.session_state.username = None
            # Clear sensitive session state keys
            keys_to_clear = ['current_subject', 'current_topic', 'current_subtopic', 'flashcard_index', 'flashcard_side', 'study_start_time']
            for key in keys_to_clear:
                 if key in st.session_state:
                     del st.session_state[key]
            st.rerun()


    # --- Main Content Area ---
    st.header(f"Subject: {st.session_state.current_subject or 'Select a Subject'}")
    st.subheader(f"Topic: {st.session_state.current_topic or 'Select a Topic'}")
    st.markdown("---")

    if st.session_state.current_subtopic:
        st.title(f"Subtopic: {st.session_state.current_subtopic}")

        subtopic_data = syllabus.get(st.session_state.current_subject, {}).get(st.session_state.current_topic, {}).get(st.session_state.current_subtopic, {})

        # Display Content using Tabs for organization
        detail_tab, notes_tab, flash_tab = st.tabs(["📖 Detailed Explanation", "📝 Revision Notes", "💡 Flashcards"])

        with detail_tab:
            content_detail = subtopic_data.get("detail", "No detailed explanation available yet.")
            st.markdown(content_detail) # Use markdown for formatting

            # TTS Button for Detail
            st.markdown("---")
            if st.button("🔊 Read Explanation Aloud", key="tts_detail"):
                with st.spinner("Generating audio..."):
                     audio_bytes = generate_tts_audio(content_detail)
                     if audio_bytes:
                         st.audio(audio_bytes, format='audio/mp3')
                     else:
                         st.error("Could not generate audio.")

        with notes_tab:
            content_notes = subtopic_data.get("notes", "No revision notes available yet.")
            st.markdown(content_notes)

            # TTS Button for Notes
            st.markdown("---")
            if st.button("🔊 Read Notes Aloud", key="tts_notes"):
                 with st.spinner("Generating audio..."):
                     audio_bytes = generate_tts_audio(content_notes)
                     if audio_bytes:
                         st.audio(audio_bytes, format='audio/mp3')
                     else:
                         st.error("Could not generate audio.")

        with flash_tab:
            flashcards = subtopic_data.get("flashcards", [])
            if flashcards:
                card_index = st.session_state.flashcard_index
                current_card = flashcards[card_index]

                # Display current card (Question or Answer)
                st.subheader(f"Flashcard {card_index + 1} / {len(flashcards)}")
                card_container = st.container() # To redraw card content easily
                with card_container:
                     if st.session_state.flashcard_side == 'q':
                         st.markdown(f"**Question:**\n> {current_card['q']}")
                     else:
                         st.markdown(f"**Answer:**\n> {current_card['a']}")

                # Flashcard Controls
                fc_col1, fc_col2, fc_col3 = st.columns(3)
                with fc_col1:
                    if st.button("⬅️ Previous", disabled=(card_index == 0), key="fc_prev"):
                        st.session_state.flashcard_index -= 1
                        st.session_state.flashcard_side = 'q' # Reset to question
                        st.rerun()
                with fc_col2:
                    flip_text = "Show Answer" if st.session_state.flashcard_side == 'q' else "Show Question"
                    if st.button(f"🔄 {flip_text}", key="fc_flip"):
                        st.session_state.flashcard_side = 'a' if st.session_state.flashcard_side == 'q' else 'q'
                        st.rerun()
                with fc_col3:
                     if st.button("Next ➡️", disabled=(card_index == len(flashcards) - 1), key="fc_next"):
                         st.session_state.flashcard_index += 1
                         st.session_state.flashcard_side = 'q' # Reset to question
                         st.rerun()
            else:
                st.write("No flashcards available for this subtopic yet.")

    elif st.session_state.current_topic:
         st.info("Select a subtopic from the sidebar to view its content.")
    elif st.session_state.current_subject:
        st.info("Select a topic from the sidebar.")
    else:
        st.info("Select a subject from the sidebar to begin learning!")

    # Simple footer or separator
    st.markdown("---")
    st.caption("O-Level Study Hub | Happy Learning!")