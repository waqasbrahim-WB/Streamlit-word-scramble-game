import streamlit as st
import random
import time

# -----------------------------
# App config
# -----------------------------
st.set_page_config(page_title="WB Word Scramble", page_icon="🎮", layout="centered")

# -----------------------------
# Game data
# -----------------------------
WORD_BANK = {
    "Animals": ["elephant", "giraffe", "kangaroo", "dolphin", "penguin", "crocodile", "rhinoceros", "chimpanzee"],
    "Fruits": ["banana", "strawberry", "pineapple", "watermelon", "mango", "orange", "grapes", "papaya"],
    "Countries": ["pakistan", "canada", "brazil", "germany", "japan", "france", "italy", "argentina"],
    "Tech": ["python", "streamlit", "database", "algorithm", "compiler", "function", "variable", "internet"],
}

DIFFICULTY_SETTINGS = {
    "Easy": {"time_limit": 30, "points": 10},
    "Medium": {"time_limit": 20, "points": 20},
    "Hard": {"time_limit": 12, "points": 35},
}

# -----------------------------
# Helpers
# -----------------------------
def scramble_word(word: str) -> str:
    chars = list(word)
    random.shuffle(chars)
    scrambled = "".join(chars)
    # Ensure scrambled isn't identical to original
    if scrambled == word:
        return scramble_word(word)
    return scrambled

def new_round():
    category = st.session_state.category
    word = random.choice(WORD_BANK[category]).lower()
    st.session_state.current_word = word
    st.session_state.scrambled = scramble_word(word)
    st.session_state.start_time = time.time()
    st.session_state.round_active = True
    st.session_state.feedback = ""
    st.session_state.user_guess = ""
    st.session_state.time_taken = None

def end_round(success: bool, time_taken: float):
    st.session_state.round_active = False
    st.session_state.time_taken = time_taken
    if success:
        st.session_state.score += DIFFICULTY_SETTINGS[st.session_state.difficulty]["points"]
        st.session_state.streak += 1
        st.session_state.feedback = f"✅ Correct! +{DIFFICULTY_SETTINGS[st.session_state.difficulty]['points']} points"
    else:
        st.session_state.streak = 0
        st.session_state.feedback = "❌ Time’s up or incorrect. Try the next one!"

def reset_game():
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.rounds_played = 0
    st.session_state.feedback = ""
    st.session_state.round_active = False
    st.session_state.user_guess = ""
    st.session_state.time_taken = None
    st.session_state.current_word = None
    st.session_state.scrambled = None
    st.session_state.start_time = None

# -----------------------------
# Initialize session state
# -----------------------------
if "score" not in st.session_state:
    st.session_state.score = 0
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "rounds_played" not in st.session_state:
    st.session_state.rounds_played = 0
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Easy"
if "category" not in st.session_state:
    st.session_state.category = "Animals"
if "round_active" not in st.session_state:
    st.session_state.round_active = False
if "current_word" not in st.session_state:
    st.session_state.current_word = None
if "scrambled" not in st.session_state:
    st.session_state.scrambled = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "feedback" not in st.session_state:
    st.session_state.feedback = ""
if "user_guess" not in st.session_state:
    st.session_state.user_guess = ""
if "time_taken" not in st.session_state:
    st.session_state.time_taken = None

# -----------------------------
# UI
# -----------------------------
st.title("🎮 WB Word Scramble")
st.caption("Unscramble the word before the timer runs out. Build your streak and score!")

with st.sidebar:
    st.header("Game settings")
    st.session_state.category = st.selectbox("Category", list(WORD_BANK.keys()), index=list(WORD_BANK.keys()).index(st.session_state.category))
    st.session_state.difficulty = st.selectbox("Difficulty", list(DIFFICULTY_SETTINGS.keys()), index=list(DIFFICULTY_SETTINGS.keys()).index(st.session_state.difficulty))
    st.button("🔄 Reset game", on_click=reset_game)

# Stats
col1, col2, col3 = st.columns(3)
col1.metric("Score", st.session_state.score)
col2.metric("Streak", st.session_state.streak)
col3.metric("Rounds", st.session_state.rounds_played)

# Start or next round
if not st.session_state.round_active:
    if st.button("▶️ Start / Next Round"):
        new_round()
        st.session_state.rounds_played += 1

# Active round UI
if st.session_state.round_active:
    time_limit = DIFFICULTY_SETTINGS[st.session_state.difficulty]["time_limit"]
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(time_limit - elapsed, 0)

    st.subheader(f"Category: {st.session_state.category} • Difficulty: {st.session_state.difficulty}")
    st.info(f"⏱️ Time remaining: {remaining}s")

    st.markdown(
        f"""
        <div style="font-size: 2rem; font-weight: 700; letter-spacing: 0.1rem; text-align:center; padding: 0.5rem; border: 2px dashed #4b9fea; border-radius: 8px;">
            {st.session_state.scrambled.upper()}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.session_state.user_guess = st.text_input("Your guess", value=st.session_state.user_guess, placeholder="Type the original word...").strip()

    c1, c2 = st.columns([1, 1])
    submit = c1.button("✅ Submit")
    give_up = c2.button("🏳️ Give up")

    # Timer auto-fail
    if remaining == 0 and st.session_state.round_active:
        end_round(success=False, time_taken=time_limit)
        st.warning("⏳ Time’s up!")

    # Submit logic
    if submit and st.session_state.round_active:
        time_taken = time.time() - st.session_state.start_time
        if st.session_state.user_guess.lower() == st.session_state.current_word.lower():
            end_round(success=True, time_taken=time_taken)
        else:
            st.error("Not quite—try again!")

    # Give up logic
    if give_up and st.session_state.round_active:
        end_round(success=False, time_taken=time_limit)

# Feedback and reveal
if st.session_state.feedback:
    st.success(st.session_state.feedback) if "Correct" in st.session_state.feedback else st.warning(st.session_state.feedback)

if not st.session_state.round_active and st.session_state.current_word:
    st.write(f"🔍 The word was: **{st.session_state.current_word}**")
    if st.session_state.time_taken is not None:
        st.write(f"⏱️ Time taken: **{int(st.session_state.time_taken)}s**")

st.divider()
st.caption("Built with Streamlit • WB_chatbot games")
