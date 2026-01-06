import streamlit as st
import random
import pandas as pd
import time

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="人生模擬器 RPG",
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
            'health': 100,        # Max 100 (健康)
            'knowledge': 10,      # Uncapped (智力)
            'wealth': 5000,       # Uncapped (財富)
            'sanity': 80,         # Max 100 (心情)
            'energy': 100         # Refills every turn (體力)
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
        log_event("你的健康歸零了... 遊戲結束。", "bad")
    if gs['stats']['sanity'] <= 0:
        gs['game_over'] = True
        log_event("你的理智斷線了... 精神崩潰。", "bad")

def advance_turn():
    """Proceed to next month."""
    # Aging
    gs['month'] += 1
    if gs['month'] > 12:
        gs['month'] = 1
        gs['age'] += 1
        log_event("生日快樂！你又長大了一歲。", "good")
    
    gs['turn'] += 1
    
    # Passive effects (Cost of living)
    cost_of_living = 1000 + (gs['age'] * 10) # Gets more expensive as you age
    gs['stats']['wealth'] -= cost_of_living
    log_event(f"支付每月生活費: ${cost_of_living}", "info")
    
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
        log_event(f"隨機事件：車子拋錨了！噴了 ${loss} 修車費。", "bad")
    elif dice == 20:
        gain = random.randint(2000, 10000)
        gs['stats']['wealth'] += gain
        gs['stats']['sanity'] += 10
        log_event(f"隨機事件：中發票了！獲得 ${gain}。", "good")
    elif dice == 10:
        gs['stats']['health'] -= 10
        log_event("隨機事件：感冒了... 健康 -10。", "bad")

# Actions
def do_action(action_type):
    stats = gs['stats']
    
    # Special handling for REST (recover energy, no cost)
    if action_type == "REST":
        with st.spinner("🧘 正在冥想... 呼... 吸..."):
            time.sleep(1.5)
        stats['energy'] += 40
        stats['sanity'] += 10
        stats['health'] += 2
        # Cap stats
        stats['energy'] = min(stats['energy'], 100)
        log_event("好好休息了一陣子。體力 +40, 心情 +10, 健康 +2。", "good")
        return

    # Standard check for other actions
    if stats['energy'] < 20:
        log_event("體力不足！請先休息或結束本月。", "bad")
        return

    # Deduct cost for non-rest actions
    stats['energy'] -= 20
    
    if action_type == "WORK":
        with st.spinner("💼 正在努力搬磚..."):
            time.sleep(1.0)
        income = 3000 + (stats['knowledge'] * 50)
        stats['wealth'] += income
        stats['sanity'] -= 5
        stats['health'] -= 2
        log_event(f"努力工作。獲得 ${income}。心情 -5, 健康 -2。", "gain")
        
    elif action_type == "STUDY":
        with st.spinner("📚 正在苦讀..."):
            time.sleep(1.0)
        stats['knowledge'] += 5
        stats['sanity'] -= 2
        log_event("鑽研新知識。智力 +5, 心情 -2。", "info")
        
    elif action_type == "GYM":
        with st.spinner("🏋️‍♀️ 正在舉重..."):
            time.sleep(1.0)
        stats['health'] += 10
        stats['sanity'] += 5
        stats['energy'] -= 10 # Extra cost (Total -30)
        log_event("去健身房揮灑汗水。健康 +10, 心情 +5。", "good")

# -----------------------------------------------------------------------------
# 5. UI Layout
# -----------------------------------------------------------------------------

# Sidebar - Stats Display
with st.sidebar:
    st.title(f"🗓️ 年齡: {gs['age']} (第 {gs['month']} 月)")
    
    # Meters
    st.write("❤️ 健康 (Health)")
    st.progress(max(0.0, min(1.0, gs['stats']['health'] / 100)))
    
    st.write("😊 心情 (Sanity)")
    st.progress(max(0.0, min(1.0, gs['stats']['sanity'] / 100)))
    
    st.write("⚡ 體力 (Energy)")
    st.progress(max(0.0, min(1.0, gs['stats']['energy'] / 100)))
    
    st.divider()
    
    # Counters
    col1, col2 = st.columns(2)
    with col1:
        st.metric("財富", f"${gs['stats']['wealth']:,.0f}")
    with col2:
        st.metric("智力", gs['stats']['knowledge'])
        
    if st.button("🔄 重置遊戲"):
        st.session_state.clear()
        st.rerun()

# Main Area
st.title("🧬 人生模擬器 RPG")

if gs['game_over']:
    st.error("💀 遊戲結束 (GAME OVER)")
    st.write(f"你活到了 {gs['age']} 歲。")
    st.stop()

# Action Panel
st.subheader("選擇你的行動")
col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    if st.button("💼 工作 (Work)", use_container_width=True, help="賺錢，但會累"):
        do_action("WORK")

with col_b:
    if st.button("📚 讀書 (Study)", use_container_width=True, help="增加智力"):
        do_action("STUDY")

with col_c:
    if st.button("🏋️‍♀️ 健身 (Gym)", use_container_width=True, help="增加健康"):
        do_action("GYM")

with col_d:
    if st.button("🧘 休息 (Rest)", use_container_width=True, help="恢復心情與體力"):
        do_action("REST")

st.divider()

# Turn Management
if gs['stats']['energy'] < 20:
    st.warning("⚠️ 體力快沒了！請結束本月以恢復體力。")
    
if st.button("🌙 結束本月 (下一回合)", type="primary"):
    with st.spinner("🌙 時光飛逝... 一個月過去了..."):
        time.sleep(1.2)
    advance_turn()
    st.rerun()

# Log Area
st.subheader("📜 人生紀錄")
log_container = st.container(height=300)
with log_container:
    for item in gs['history']:
        st.markdown(f"**{item['time']}** {item['icon']} {item['msg']}")

# Debug (Optional)
# st.json(gs)
