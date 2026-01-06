import streamlit as st
import random
import pandas as pd
import time

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Life RPG: The Simulation",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. Custom CSS (Retro/Pixel Vibe)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .stat-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #4e4f57;
        text-align: center;
    }
    .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
    }
    .stat-label {
        font-size: 14px;
        color: #a0a0a0;
    }
    /* Button custom styling could go here */
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Game State Management
# -----------------------------------------------------------------------------
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        'turn': 1,
        'age': 18,
        'month': 1,
        'stats': {
            'health': 100,        # Max 100
            'knowledge': 10,      # Uncapped
            'wealth': 5000,       # Uncapped
            'sanity': 80,         # Max 100
            'energy': 100         # Refills every turn
        },
        'history': [],            # Log of events
        'game_over': False
    }

gs = st.session_state.game_state

# -----------------------------------------------------------------------------
# 4. Core Logic Functions
# -----------------------------------------------------------------------------
def log_event(message, type="info"):
    """Add a message to the history log."""
    icon = "ℹ️"
    if type == "good": icon = "✅"
    if type == "bad": icon = "⚠️"
    if type == "gain": icon = "💰"
    
    timestamp = f"Age {gs['age']} M{gs['month']}"
    gs['history'].insert(0, {"time": timestamp, "msg": message, "icon": icon})

def check_game_over():
    if gs['stats']['health'] <= 0:
        gs['game_over'] = True
        log_event("You died of poor health...", "bad")
    if gs['stats']['sanity'] <= 0:
        gs['game_over'] = True
        log_event("You had a mental breakdown...", "bad")

def advance_turn():
    """Proceed to next month."""
    # Aging
    gs['month'] += 1
    if gs['month'] > 12:
        gs['month'] = 1
        gs['age'] += 1
        log_event("Happy Birthday! You are a year older.", "good")
    
    gs['turn'] += 1
    
    # Passive effects (Cost of living)
    cost_of_living = 1000 + (gs['age'] * 10) # Gets more expensive as you age
    gs['stats']['wealth'] -= cost_of_living
    log_event(f"Paid monthly expenses: ${cost_of_living}", "info")
    
    # Random Events
    trigger_random_event()
    
    # Energy Reset
    gs['stats']['energy'] = 100
    
    # Caps check
    gs['stats']['health'] = min(gs['stats']['health'], 100)
    gs['stats']['sanity'] = min(gs['stats']['sanity'], 100)
    
    check_game_over()

def trigger_random_event():
    dice = random.randint(1, 20)
    if dice == 1:
        loss = random.randint(1000, 5000)
        gs['stats']['wealth'] -= loss
        gs['stats']['sanity'] -= 10
        log_event(f"Event: Car broke down! Lost ${loss}.", "bad")
    elif dice == 20:
        gain = random.randint(2000, 10000)
        gs['stats']['wealth'] += gain
        gs['stats']['sanity'] += 10
        log_event(f"Event: Won lottery ticket! Gained ${gain}.", "good")
    elif dice == 10:
        gs['stats']['health'] -= 10
        log_event("Event: Caught a flu. Health -10.", "bad")

# Actions
def do_action(action_type):
    stats = gs['stats']
    
    if stats['energy'] < 20:
        log_event("Not enough energy!", "bad")
        return

    stats['energy'] -= 20
    
    if action_type == "WORK":
        income = 3000 + (stats['knowledge'] * 50)
        stats['wealth'] += income
        stats['sanity'] -= 5
        stats['health'] -= 2
        log_event(f"Worked hard. Earned ${income}. Sanity -5.", "gain")
        
    elif action_type == "STUDY":
        stats['knowledge'] += 5
        stats['sanity'] -= 2
        log_event("Studied new skills. Knowledge +5.", "info")
        
    elif action_type == "REST":
        stats['sanity'] += 15
        stats['health'] += 5
        log_event("Took a break. Sanity +15, Health +5.", "good")
        
    elif action_type == "GYM":
        stats['health'] += 10
        stats['sanity'] += 5
        stats['energy'] -= 10 # Extra cost
        log_event("Hit the gym. Health +10. Feeling pumped!", "good")

# -----------------------------------------------------------------------------
# 5. UI Layout
# -----------------------------------------------------------------------------

# Sidebar - Stats Display
with st.sidebar:
    st.title(f"🗓️ Age: {gs['age']} (M{gs['month']})")
    
    # Meters
    st.write("❤️ Health")
    st.progress(gs['stats']['health'] / 100)
    
    st.write("😊 Sanity")
    st.progress(gs['stats']['sanity'] / 100)
    
    st.write("⚡ Energy")
    st.progress(gs['stats']['energy'] / 100)
    
    st.divider()
    
    # Counters
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Wealth", f"${gs['stats']['wealth']:,.0f}")
    with col2:
        st.metric("Knowledge", gs['stats']['knowledge'])
        
    if st.button("🔄 Restart Game"):
        st.session_state.clear()
        st.rerun()

# Main Area
st.title("🧬 Life RPG: Simulator")

if gs['game_over']:
    st.error("💀 GAME OVER")
    st.write(f"You survived until age {gs['age']}.")
    st.stop()

# Action Panel
st.subheader("Choose Your Activity")
col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    if st.button("💼 Work", use_container_width=True, help="Earn money, lose sanity"):
        do_action("WORK")

with col_b:
    if st.button("📚 Study", use_container_width=True, help="Gain knowledge"):
        do_action("STUDY")

with col_c:
    if st.button("🏋️‍♀️ Gym", use_container_width=True, help="Improve health"):
        do_action("GYM")

with col_d:
    if st.button("🧘 Rest", use_container_width=True, help="Recover sanity"):
        do_action("REST")

st.divider()

# Turn Management
if gs['stats']['energy'] < 20:
    st.warning("⚠️ Low Energy! End turn to recover.")
    
if st.button("🌙 End Month (Next Turn)", type="primary"):
    advance_turn()
    st.rerun()

# Log Area
st.subheader("📜 Life Log")
log_container = st.container(height=300)
with log_container:
    for item in gs['history']:
        st.markdown(f"**{item['time']}** {item['icon']} {item['msg']}")

# Debug (Optional)
# st.json(gs)
