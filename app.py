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
    /* Global Background & Font */
    .stApp {
        background-color: #0e1117;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Cyberpunk Stat Card */
    .stat-card {
        background: rgba(17, 25, 40, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.125);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 10px;
    }
    .stat-value {
        font-size: 32px;
        font-weight: bold;
        color: #00ff41; /* Neo Green */
        text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
    }
    .stat-label {
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #b3b3b3;
    }
    
    /* Progress Bar Styling */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #00c6ff, #0072ff);
    }
    
    /* Custom divider */
    hr {
        border-color: #333;
    }
    
    /* Button Hover Glow */
    div.stButton > button {
        border: 1px solid #333;
        background-color: #1a1a1a;
        color: #00ff41;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        border-color: #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
        color: #ffffff;
    }
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
        msg = f"⚠️ 系統警告：伺服器遭受攻擊！緊急修復花費 ${loss}。"
        log_event(msg, "bad")
        st.toast(msg, icon="🔥")
    elif dice == 20:
        gain = random.randint(2000, 10000)
        gs['stats']['wealth'] += gain
        gs['stats']['sanity'] += 10
        msg = f"💎 幸運事件：加密貨幣投資暴漲！獲得 ${gain}。"
        log_event(msg, "good")
        st.toast(msg, icon="🚀")
    elif dice == 10:
        gs['stats']['health'] -= 10
        msg = "⚠️ 系統警告：生物特徵異常。疑似感染流感病毒。"
        log_event(msg, "bad")
        st.toast(msg, icon="🦠")

# Actions
def do_action(action_type):
    stats = gs['stats']
    
    # Debug info
    st.write(f"DEBUG: Processing action '{action_type}'")

    if action_type == "REST":
        with st.spinner("🧘 正在冥想... 連接宇宙意識..."):
            time.sleep(1.5)
        stats['energy'] += 40
        stats['sanity'] += 10
        stats['health'] += 2
        # Cap stats
        stats['energy'] = min(stats['energy'], 100)
        
        msg = "系統充能完畢。體力與理智已恢復。"
        log_event(msg, "good")
        st.toast(msg, icon="🧘")
        return

    # ----------------------------------------------------------------
    # Logic for non-REST actions
    # ----------------------------------------------------------------
    
    # 1. Check Energy
    if stats['energy'] < 20:
        log_event("體力不足！請先休息或結束本月。", "bad")
        return

    # 2. Deduct Energy
    stats['energy'] -= 20
    
    # 3. Apply Effect
    if action_type == "WORK":
        with st.spinner("💼 正在執行高頻交易算法..."):
            time.sleep(1.0)
        income = 3000 + (stats['knowledge'] * 50)
        stats['wealth'] += income
        stats['sanity'] -= 5
        stats['health'] -= 2
        msg = f"專案交付成功。入帳 ${income}。"
        log_event(msg, "gain")
        st.toast(msg, icon="💸")
        
    elif action_type == "STUDY":
        with st.spinner("📚 正在下載神經網絡模型..."):
            time.sleep(1.0)
        stats['knowledge'] += 5
        stats['sanity'] -= 2
        msg = "腦容量升級。智力 +5。"
        log_event(msg, "info")
        st.toast(msg, icon="🧠")
        
    elif action_type == "GYM":
        with st.spinner("🏋️‍♀️ 正在強化外骨骼機甲..."):
            time.sleep(1.0)
        stats['health'] += 10
        stats['sanity'] += 5
        stats['energy'] -= 10 # Extra cost (Total -30)
        msg = "機體維護完成。健康 +10, 心情 +5。"
        log_event(msg, "good")
        st.toast(msg, icon="🦾")

# -----------------------------------------------------------------------------
# 5. UI Layout
# -----------------------------------------------------------------------------

# Sidebar - Stats Display
with st.sidebar:
    st.markdown(f"## 🗓️ Cycle: {gs['age']} // M-{gs['month']}")
    
    # Custom Function for Dynamic Status
    def get_status_icon(value, type="normal"):
        if value > 80: return "🟢" if type=="normal" else "⚡"
        if value > 40: return "🟡" if type=="normal" else "🔋"
        return "🔴" if type=="normal" else "🪫"

    # Meters
    st.markdown("### 🧬 生理監測 (Biometrics)")
    
    h_val = gs['stats']['health']
    st.write(f"Health: {h_val}% {get_status_icon(h_val)}")
    st.progress(max(0.0, min(1.0, h_val / 100)))
    
    s_val = gs['stats']['sanity']
    st.write(f"Sanity: {s_val}% {get_status_icon(s_val)}")
    st.progress(max(0.0, min(1.0, s_val / 100)))
    
    e_val = gs['stats']['energy']
    st.write(f"Energy: {e_val}% {get_status_icon(e_val, 'energy')}")
    st.progress(max(0.0, min(1.0, e_val / 100)))
    
    st.divider()
    
    # Counters
    st.markdown("### 💾 資源存量 (Assets)")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Credits (財富)", f"${gs['stats']['wealth']:,.0f}", delta="USD")
    with col2:
        st.metric("RAM (智力)", gs['stats']['knowledge'], delta="INT")
        
    if st.button("🔄 系統重置 (Reboot)"):
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
# Action Panel
st.subheader("選擇你的行動")
# Debug: Show button states
st.caption(f"Button States: Work={st.session_state.get('btn_work')} | Study={st.session_state.get('btn_study')} | Gym={st.session_state.get('btn_gym')} | Rest={st.session_state.get('btn_rest')}")

if st.button("💼 工作 (Work)", use_container_width=True, key="btn_work", help="賺錢，但會累"):
    do_action("WORK")

if st.button("📚 讀書 (Study)", use_container_width=True, key="btn_study", help="增加智力"):
    do_action("STUDY")

if st.button("🏋️‍♀️ 健身 (Gym)", use_container_width=True, key="btn_gym", help="增加健康"):
    do_action("GYM")

if st.button("🧘 休息 (Rest)", use_container_width=True, key="btn_rest", help="恢復心情與體力"):
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
