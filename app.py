import streamlit as st
import random
import time

# -----------------------------
# App config
# -----------------------------
st.set_page_config(page_title="WB Word Scramble", page_icon="🎮", layout="centered")

# -----------------------------
# Custom CSS for colorful design
# -----------------------------
PRIMARY = "#4B9FEA"
ACCENT = "#7C4DFF"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER = "#EF4444"
BG = "#0F172A"
CARD = "#111827"
TEXT = "#E5E7EB"
MUTED = "#9CA3AF"

CSS = f"""
<style>
.stApp {{
  background: linear-gradient(135deg, {BG} 0%, #0b1220 50%, #0a0f1a 100%);
  color: {TEXT};
  font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', Arial, sans-serif;
}}
.card {{
  background: {CARD};
  border: 1px solid #1F2937;
  border-radius: 14px;
  padding: 16px 18px;
  box-shadow: 0 6px 24px rgba(0,0,0,0.35);
}}
.scramble {{
  font-size: 2.2rem;
  font-weight: 700;
  letter-spacing: 0.15rem;
  text-align:center;
  padding: 0.8rem;
  border: 3px dashed {PRIMARY};
  border-radius: 12px;
  background: linear-gradient(135deg, {PRIMARY}, {ACCENT});
  color: white;
  box-shadow: 0 8px 20px rgba(76, 29, 149, 0.35);
}}
.stButton>button {{
  background: linear-gradient(135deg, {PRIMARY}, {ACCENT});
  color: white; border: none; border-radius: 10px;
  padding: 10px 16px; font-weight: 600;
  box-shadow: 0 8px 20px rgba(76, 29, 149, 0.35);
}}
.stButton>button:hover {{ filter: brightness(1.05); }}
hr {{ border: none; border-top: 1px solid #1F2937; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

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
for key, default in {
    "score": 0, "streak": 0, "rounds_played": 0, "difficulty": "Easy",
    "category": "Animals", "round_active": False, "current_word": None,
    "scrambled": None, "start_time": None, "feedback": "", "user_guess": "",
    "time_taken": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -----------------------------
# UI
# -----------------------------
st.markdown(f"""
<div class="card">
  <h1>🎮 WB Word Scramble</h1>
  <p style="color:{MUTED};">Unscramble the word before the timer runs out. Build your streak and score!</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Game settings")
    st.session_state.category = st.selectbox("Category", list(WORD_BANK.keys()), index=list(WORD_BANK.keys()).index(st.session_state.category))
    st.session_state.difficulty = st.selectbox("Difficulty", list(DIFFICULTY_SETTINGS.keys()), index=list(DIFFICULTY_SETTINGS.keys()).index(st.session_state.difficulty))
    st.button("🔄 Reset game", on_click=reset_game)

# Stats
col1, col2, col3 = st.columns(3)
col1.metric("🏆 Score", st.session_state.score)
col2.metric("🔥 Streak", st.session_state.streak)
col3.metric("🎲 Rounds", st.session_state.rounds_played)

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

    st.subheader(f"📂 Category: {st.session_state.category} • 🎚️ Difficulty: {st.session_state.difficulty}")
    st.info(f"⏱️ Time remaining: {remaining}s")

    st.markdown(f"<div class='scramble'>{st.session_state.scrambled.upper()}</div>", unsafe_allow_html=True)

    st.session_state.user_guess = st.text_input("💡 Your guess", value=st.session_state.user_guess, placeholder="Type the original word...").strip()

    c1, c2 = st.columns([1, 1])
    submit = c1.button("✅ Submit")
    give_up = c2.button("🏳️ Give up")

    if remaining == 0 and st.session_state.round_active:
        end_round(success=False, time_taken=time_limit)
        st.warning("⏳ Time’s up!")

    if submit and st.session_state.round_active:
        time_taken = time.time() - st.session_state.start_time
        if st.session_state.user_guess.lower() == st.session_state.current_word.lower():
            end_round(success=True, time_taken=time_taken)
        else:
            st.error("Not quite—try again!")

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
st.caption("✨ Built with Streamlit • WB_chatbot games")
