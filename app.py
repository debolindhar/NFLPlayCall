import streamlit as st
import requests
import time
from threading import Thread
from superbowlagent import SuperBowlAgent, game_state

# Initialize agent
if "agent" not in st.session_state:
    st.session_state.agent = SuperBowlAgent()

agent = st.session_state.agent

# Set page config
st.set_page_config(
    page_title="NFL Play Call - Super Bowl LX",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with team colors
st.markdown("""
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #001a4d 0%, #003366 100%);
            color: #fff;
        }

        .main {
            background: linear-gradient(135deg, #001a4d 0%, #003366 100%);
        }

        header {
            text-align: center;
            margin-bottom: 40px;
        }

        h1 {
            font-size: 3em;
            font-weight: 900;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            letter-spacing: 2px;
            background: linear-gradient(45deg, #00ff88, #00ccff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .status-bar {
            background: rgba(0, 51, 102, 0.8);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid #00ff88;
        }

        .status-item {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .status-label {
            color: #00ccff;
            font-size: 0.9em;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .status-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #00ff88;
        }

        .live-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #ff0000;
            border-radius: 50%;
            animation: pulse 1s infinite;
            margin-right: 8px;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        .patriots-card {
            background: rgba(0, 43, 92, 0.9);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            border: 2px solid #b0b7bc;
            box-shadow: 0 0 20px rgba(176, 183, 188, 0.3);
        }

        .seahawks-card {
            background: rgba(12, 44, 86, 0.9);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            border: 2px solid #69be28;
            box-shadow: 0 0 20px rgba(105, 190, 40, 0.3);
        }

        .team-score {
            font-size: 4em;
            font-weight: 900;
            margin: 20px 0;
        }

        .patriots-score {
            color: #b0b7bc;
            text-shadow: 0 0 10px #002B5C;
        }

        .seahawks-score {
            color: #69be28;
            text-shadow: 0 0 10px #0C2C56;
        }

        .feature-card {
            background: rgba(0, 51, 102, 0.9);
            border-radius: 15px;
            padding: 25px;
            border-left: 4px solid #00ff88;
            backdrop-filter: blur(10px);
            margin-bottom: 15px;
        }

        .fun-fact {
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 204, 255, 0.1) 100%);
            border: 1px dashed #00ff88;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }

        footer {
            text-align: center;
            padding-top: 30px;
            border-top: 1px solid #00ff88;
            color: #00ccff;
            opacity: 0.7;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 40px;">
    <h1>🏈 NFL Play Call</h1>
    <p style="font-size: 1.2em; color: #00ff88;">Super Bowl LX Live Experience</p>
</div>
""", unsafe_allow_html=True)

# Status Bar
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🔴 Status", "LIVE")

with col2:
    st.metric("⏱️ Game Time", f"Q{game_state['quarter']} • {game_state['time_remaining']}")

with col3:
    possession = "🅿️ Patriots" if game_state['possession'] == "NE" else "🦅 Seahawks"
    st.metric("📍 Possession", possession)

with col4:
    st.metric("📅 Date", "Feb 8, 2026")

st.divider()

# Scoreboard
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="patriots-card">
        <div style="font-size: 3em; margin-bottom: 15px;">🅿️</div>
        <div style="font-size: 1.5em; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">New England Patriots</div>
        <div class="team-score patriots-score">{game_state['current_score']['NE']}</div>
        <div style="margin-top: 15px; color: #b0b7bc;">↑ Momentum</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="seahawks-card">
        <div style="font-size: 3em; margin-bottom: 15px;">🦅</div>
        <div style="font-size: 1.5em; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">Seattle Seahawks</div>
        <div class="team-score seahawks-score">{game_state['current_score']['SEA']}</div>
        <div style="margin-top: 15px; color: #69be28;">Regrouping</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Win Probability
col1, col2 = st.columns(2)

with col1:
    ne_prob = game_state['win_probability']['NE']
    st.markdown(f"""
    <div style="background: rgba(0, 51, 102, 0.9); border-radius: 15px; padding: 20px;">
        <div style="color: #00ccff; margin-bottom: 10px;">Patriots Win Probability</div>
        <div style="width: 100%; background: rgba(255, 255, 255, 0.1); border-radius: 10px; overflow: hidden; height: 30px;">
            <div style="width: {ne_prob}%; background: linear-gradient(90deg, #002B5C, #b0b7bc); height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">{ne_prob}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    sea_prob = game_state['win_probability']['SEA']
    st.markdown(f"""
    <div style="background: rgba(0, 51, 102, 0.9); border-radius: 15px; padding: 20px;">
        <div style="color: #00ccff; margin-bottom: 10px;">Seahawks Win Probability</div>
        <div style="width: 100%; background: rgba(255, 255, 255, 0.1); border-radius: 10px; overflow: hidden; height: 30px;">
            <div style="width: {sea_prob}%; background: linear-gradient(90deg, #0C2C56, #69be28); height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">{sea_prob}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Game Controls
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Start Game", use_container_width=True):
        st.session_state.game_running = True
        st.rerun()

with col2:
    if st.button("🔄 Update", use_container_width=True):
        agent.simulate_game_update()
        st.rerun()

with col3:
    if st.button("⏹️ Stop", use_container_width=True):
        st.session_state.game_running = False

st.divider()

# Features
st.subheader("🎙️ Live Features")

tab1, tab2, tab3, tab4 = st.tabs(["Commentary", "NFL Basics", "Sentiment", "Facts"])

with tab1:
    st.markdown("""
    <div class="feature-card">
        <h3>🎙️ Play Commentary</h3>
        <p>"AND THERE'S THE TOUCHDOWN! The Patriots extend their lead with an incredible catch in the end zone! The crowd is absolutely going wild right now!"</p>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="feature-card">
        <h3>🏈 NFL Basics: Touchdowns</h3>
        <p>A touchdown is when a team gets the ball into the opponent's end zone. It's worth 6 points and is the main way to score big in football!</p>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div class="feature-card">
        <h3>😍 Fan Sentiment: POSITIVE</h3>
        <p><strong>Trending:</strong> #PatriotsLead #SuperBowlLX #TouchdownParty<br><br>Fans are loving the fast-paced action and big plays!</p>
    </div>
    """, unsafe_allow_html=True)

with tab4:
    st.markdown("""
    <div class="fun-fact">
        <strong>📚 Super Bowl Fact:</strong> The Super Bowl is watched by over 100 million people worldwide, making it one of the most-watched sporting events! This is Super Bowl LX (60 in Roman numerals) - a historic game!
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Footer
st.markdown("""
<div style="text-align: center; padding-top: 30px; border-top: 1px solid #00ff88; color: #00ccff; opacity: 0.7;">
    <p>🏆 NFL Play Call - Your AI-Powered Super Bowl Companion 🏆</p>
    <p style="font-size: 0.9em; margin-top: 10px;">Real-time updates • Beginner-friendly insights • Live sentiment analysis</p>
</div>
""", unsafe_allow_html=True)

# Auto-update
if st.session_state.get("game_running", False):
    if not game_state["game_ended"]:
        agent.simulate_game_update()
        time.sleep(2)
        st.rerun()