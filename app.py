import streamlit as st
import atexit
from PIL import ImageGrab  # Add this import
import time  # Add this import
import os  # Add this import
import base64  # Add this import

# Page Configuration must be first
st.set_page_config(
    page_title="Quiz Research App",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils.api import OpenDBAPI
from utils.db import Database
import json
import requests

# Initialize Database singleton with absolute path
@st.cache_resource
def init_db():
    db = Database(db_path='quiz_app.db')  # Specify absolute path
    return db

# Clear cache to ensure the latest version of the Database class is used
st.cache_resource.clear()

# Get database instance
db = init_db()

# Ensure connection is released when the script reruns
if 'db_initialized' not in st.session_state:
    db.release_connection()
    st.session_state.db_initialized = True

# Category Mapping
CATEGORIES = {
    "General Knowledge": 9,
    "Entertainment: Books": 10,
    "Entertainment: Film": 11,
    "Entertainment: Music": 12,
    "Entertainment: Musicals & Theatres": 13,
    "Entertainment: Television": 14,
    "Entertainment: Video Games": 15,
    "Entertainment: Board Games": 16,
    "Science & Nature": 17,
    "Science: Computers": 18,
    "Science: Mathematics": 19,
    "Mythology": 20,
    "Sports": 21,
    "Geography": 22,
    "History": 23,
    "Politics": 24,
    "Art": 25,
    "Celebrities": 26,
    "Animals": 27,
    "Vehicles": 28,
    "Entertainment: Comics": 29,
    "Science: Gadgets": 30,
    "Entertainment: Japanese Anime & Manga": 31,
    "Entertainment: Cartoon & Animations": 32,
    "Any Category": None
}

# Initialize Session State
if 'crossed_questions' not in st.session_state:
    st.session_state.crossed_questions = []
if 'ticked_questions' not in st.session_state:
    st.session_state.ticked_questions = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'questions' not in st.session_state:
    st.session_state.questions = []

# User Authentication
st.sidebar.header("User Authentication")
username = st.sidebar.text_input("Enter your username", value="0")
if username == "":
    username = "0"

# Check if username exists, if not and not "0", add to database
if username != "0":
    if not db.add_user(username):
        st.sidebar.error("Username already taken. Please choose another one.")
        st.stop()
user_id = db.get_user_id(username)

# Sidebar - Reset Database (for testing purposes)
if st.sidebar.button("Reset Database"):
    db.reset_database()
    st.sidebar.success("Database reset successfully. Please reload the app.")

# Sidebar - Selection
st.sidebar.header("Quiz Parameters")
with st.sidebar.form(key='parameters'):
    category = st.selectbox("Category", list(CATEGORIES.keys()))
    difficulty = st.selectbox("Difficulty", ["Any", "Easy", "Medium", "Hard"])
    q_type = st.selectbox("Type", ["Any", "Multiple Choice", "True / False"])
    amount = st.slider("Number of Questions", 1, 49, 10)
    submit = st.form_submit_button("Fetch Questions")

# Fetch Questions
if submit:
    selected_category = CATEGORIES[category]
    selected_difficulty = None if difficulty == "Any" else difficulty.lower()
    selected_type = None
    if q_type == "Multiple Choice":
        selected_type = "multiple"
    elif q_type == "True / False":
        selected_type = "boolean"

    api = OpenDBAPI(amount=amount, category=selected_category,
                   difficulty=selected_difficulty, question_type=selected_type)
    try:
        data = api.fetch_questions()
        st.session_state.questions = data.get('results', [])
        st.session_state.current_question = 0
        # Store fetched questions in the database and save the history_id
        for question in st.session_state.questions:
            history_id = db.add_question_history(user_id, question)
            question['history_id'] = history_id  # Store the history_id in the question dict
    except requests.exceptions.HTTPError as e:
        st.error(f"Error fetching questions: {e}")

# Add custom CSS
st.markdown("""
<style>
    /* Remove ALL white spaces and padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Fix sidebar padding */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Remove top margin from sidebar header */
    .css-163ttbj {
        margin-top: 1rem;
    }
    
    /* Remove the Streamlit header to eliminate white box */
    header.css-1avcm0n.edgvbvh3 {
        visibility: hidden;
    }
    
    /* Alternatively, target the header more specifically */
    .css-1aumxhk.e1fqkh3o3 {
        display: none;
    }
    
    .main > div {
        padding-top: 1rem !important;
    }
    
    /* Enhanced question card with shadow */
    .question-text {
        font-size: 20px !important;
        padding: 15px;
        line-height: 1.5;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    .metadata {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
    }

    /* History Section Styling */
    .history-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .history-section {
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Mobile Optimizations */
    @media (max-width: 768px) {
        .question-text {
            font-size: 18px !important;
            padding: 15px;
        }

        .option-list {
            font-size: 16px;
            padding: 10px;
        }

        .metadata {
            padding: 10px;
        }

        .history-section {
            padding: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Add custom CSS for Footer and Remove White Space
st.markdown("""
<style>
    /* Remove top white block (Streamlit header) */
    /* 
    header.css-1avcm0n.edgvbvh3 {
        display: none !important;
    }
    
    .css-1aumxhk.e1fqkh3o3 {
        display: none;
    }
    */

    /* Remove the Streamlit footer */
    footer {
        visibility: hidden;
        height: 0px !important;
    }

    /* Custom Footer Styling */
    .custom-footer {
        text-align: center;
        color: gray;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #ddd;
        font-size: 0.9rem;
    }

    /* Center align all main content */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        max-width: 700px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Update the custom CSS section
st.markdown("""
<style>
    /* Main container styling */
    .block-container {
        padding: 2rem 1rem !important;
        max-width: 800px !important;
        margin: 0 auto;
    }
    
    /* Clean background */
    .stApp {
        background: #f8f9fa;
    }
    
    /* Question card styling */
    .question-text {
        font-size: 1.2rem !important;
        padding: 1.5rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    /* Metadata styling */
    .metadata {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Options styling */
    .option-list {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }

    /* Button styling */
    .stButton button {
        width: 100%;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: transform 0.2s;
    }

    /* Custom footer */
    .custom-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem;
        background: white;
        text-align: center;
        border-top: 1px solid #e9ecef;
        z-index: 100;
    }

    /* History section */
    .history-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }

    .history-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }

    /* Sidebar improvements */
    .css-1d391kg {
        padding: 2rem 1rem;
    }

    /* Typography improvements */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a;
        margin: 1rem 0;
    }

    /* Info boxes */
    .stAlert {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 8px;
    }

    /* Add padding at bottom to prevent content being hidden by footer */
    .main {
        padding-bottom: 4rem;
    }
</style>
""", unsafe_allow_html=True)

# Display Questions
if st.session_state.questions:
    question = st.session_state.questions[st.session_state.current_question]
    
    # Metadata section
    st.markdown("""
    <div class="metadata">
        <b>Category:</b> {} <br>
        <b>Type:</b> {} <br>
        <b>Difficulty:</b> {}
    </div>
    """.format(
        question.get('category'),
        question.get('type').capitalize(),
        question.get('difficulty').capitalize()
    ), unsafe_allow_html=True)
    
    # Question section
    st.markdown('<div class="question-text">{}</div>'.format(question['question']), unsafe_allow_html=True)
    
    # Options section
    options = question.get('incorrect_answers', []) + [question.get('correct_answer')]
    if question.get('type') == 'boolean':
        options = ["True", "False"]
    
    st.markdown("### Options")
    option_text = ""
    for idx, option in enumerate(options):
        option_text += f"{chr(97+idx)}) {option}<br>"
    st.markdown(f'<div class="option-list">{option_text}</div>', unsafe_allow_html=True)
    
    # Answer section
    st.info(f"**Answer:** {question['correct_answer']}")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Previous", key="previous", use_container_width=True) and st.session_state.current_question > 0:
            st.session_state.current_question -= 1
    with col2:
        if st.button("❌ Reject", key="reject", use_container_width=True):
            db.update_question_status(question['history_id'], "rejected")
            st.write(f"Debug: Rejected Question - {question['question']}")  # Debug statement
            st.session_state.questions.pop(st.session_state.current_question)
            if st.session_state.current_question >= len(st.session_state.questions):
                st.session_state.current_question = max(0, len(st.session_state.questions) - 1)
    with col3:
        if st.button("✅ Accept", key="accept", use_container_width=True):
            db.update_question_status(question['history_id'], "accepted")
            st.write(f"Debug: Accepted Question - {question['question']}")  # Debug statement
            # Take a screenshot of the question
            screenshot = ImageGrab.grab()
            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)  # Ensure the directory exists
            screenshot_path = os.path.join(screenshot_dir, f"question_{question['history_id']}.png")
            screenshot.save(screenshot_path)
            st.write(f"Screenshot saved to {screenshot_path}")
            # Automatically start the download
            with open(screenshot_path, "rb") as file:
                base64_image = base64.b64encode(file.read()).decode()
                href = f'<a href="data:image/png;base64,{base64_image}" download="question_{question['history_id']}.png"></a>'
                st.markdown(href, unsafe_allow_html=True)
                st.markdown(f'<script>document.querySelector("a").click();</script>', unsafe_allow_html=True)
            st.session_state.questions.pop(st.session_state.current_question)
            if st.session_state.current_question >= len(st.session_state.questions):
                st.session_state.current_question = max(0, len(st.session_state.questions) - 1)
                
    # Next button in a separate row for better mobile layout
    if st.button("➡️ Next", key="next", use_container_width=True) and st.session_state.current_question < len(st.session_state.questions) - 1:
        st.session_state.current_question += 1
else:
    st.info("No questions available. Please fetch questions to start the quiz.")

# Enhanced History Section
st.sidebar.header("History")
if st.sidebar.button("Show History"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="history-section">', unsafe_allow_html=True)
        st.subheader("❌ Rejected Questions")
        rejected_questions = db.get_user_history_by_status(user_id, "rejected")
        st.write(f"Debug: Rejected Questions - {rejected_questions}")  # Debug statement
        for q in rejected_questions:
            st.markdown('<div class="history-card">', unsafe_allow_html=True)
            st.write(f"📌 **Category:** {q.get('category')}")
            st.write(q['question'])
            st.write(f"💡 **Answer:** {q['correct_answer']}")
            if st.button("✅ Undo", key=f"undo_{q['id']}"):
                db.update_question_status(q['id'], "accepted")  # Use the history_id
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="history-section">', unsafe_allow_html=True)
        st.subheader("✅ Accepted Questions")
        accepted_questions = db.get_user_history_by_status(user_id, "accepted")
        st.write(f"Debug: Accepted Questions - {accepted_questions}")  # Debug statement
        for q in accepted_questions:
            st.markdown('<div class="history-card">', unsafe_allow_html=True)
            st.write(f"📌 **Category:** {q.get('category')}")
            st.write(q['question'])
            st.write(f"💡 **Answer:** {q['correct_answer']}")
            screenshot_path = f"screenshots/question_{q['id']}.png"
            if os.path.exists(screenshot_path):
                st.image(screenshot_path, caption=f"Screenshot of Question {q['id']}")
                with open(screenshot_path, "rb") as file:
                    btn = st.download_button(
                        label="Download Screenshot",
                        data=file,
                        file_name=f"question_{q['id']}.png",
                        mime="image/png"
                    )
            if st.button("❌ Remove", key=f"remove_{q['id']}"):
                db.update_question_status(q['id'], "rejected")  # Use the history_id
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="custom-footer">
    Made with ❤️ by <a href="https://github.com/a3ro-dev" target="_blank">a3ro-dev</a>
</div>
""", unsafe_allow_html=True)

# Update the shutdown handler
def shutdown():
    db.release_connection()  # Ensure connection is released
    db.close()
    st.session_state.db_initialized = False

atexit.register(shutdown)