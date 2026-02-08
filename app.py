import streamlit as st
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")

if not api_key:
    st.error("❌ ANTHROPIC_API_KEY not found! Add it to .env or Streamlit Secrets.")
    st.stop()

# Import SuperBowlAgent and game_state
from superbowlagent import SuperBowlAgent, game_state

# Initialize agent
if "agent" not in st.session_state:
    st.session_state.agent = SuperBowlAgent()

agent = st.session_state.agent

# Get user timezone from browser (optional)
user_timezone = st.session_state.get("timezone", "America/New_York")

# Set page config
st.set_page_config(
    page_title="NFL Play Call - Super Bowl LX",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
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
            margin-bottom: 15px;
        }

        .fun-fact {
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 204, 255, 0.1) 100%);
            border: 1px dashed #00ff88;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
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

# Get current game time
game_time, quarter = agent.get_game_time(user_timezone)
local_time = agent.get_user_local_time(user_timezone)

# Status Bar
col1, col2, col3, col4 = st.columns(4)

with col1:
    status = "LIVE" if game_state["game_started"] else "PENDING"
    st.metric("🔴 Status", status)

with col2:
    st.metric("⏱️ Game Time", f"Q{quarter} • {game_time}")

with col3:
    possession = "🅿️ Patriots" if game_state['possession'] == "NE" else "🦅 Seahawks"
    st.metric("📍 Possession", possession)

with col4:
    st.metric("🕐 Local Time", local_time)

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
        <div style="width: 100%; background: rgba(255, 255, 255, 0.1); border-radius: 10px; overflow: hidden, height: 30px;">
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
        game_state["game_started"] = True
        st.rerun()

with col2:
    if st.button("🔄 Update", use_container_width=True):
        agent.simulate_game_update()
        st.rerun()

with col3:
    if st.button("⏹️ Stop", use_container_width=True):
        st.session_state.game_running = False
        st.rerun()

st.divider()

# Live Features
st.subheader("🎙️ Live Features")

tab1, tab2, tab3, tab4 = st.tabs(["Commentary", "NFL Basics", "Sentiment", "Fun Facts"])

with tab1:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #00ff88; margin-bottom: 12px;">🎙️ Play Commentary</h3>
        <p style="color: #ccc; line-height: 1.6;">"AND THERE'S THE TOUCHDOWN! The Patriots extend their lead with an incredible catch in the end zone! The crowd is absolutely going wild right now!"</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Generate Commentary", key="commentary"):
        try:
            agent.show_play_commentary()
            st.success("✅ Commentary generated!")
        except Exception as e:
            st.error(f"Error generating commentary: {e}")

with tab2:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #00ff88; margin-bottom: 12px;">🏈 NFL Basics</h3>
        <p style="color: #ccc; line-height: 1.6;">Learn about football concepts and rules!</p>
    </div>
    """, unsafe_allow_html=True)
    
    lesson_topic = st.selectbox(
        "Choose a topic to learn:",
        ["touchdown", "down", "penalty", "turnover", "sack", "field goal"],
        key="nfl_lesson"
    )
    
    if st.button("Explain Topic", key="explain"):
        try:
            agent.show_basic_nfl_lesson(lesson_topic)
            st.success("✅ Explanation generated!")
        except Exception as e:
            st.error(f"Error generating explanation: {e}")

with tab3:
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #00ff88; margin-bottom: 12px;">😍 Fan Sentiment Analysis</h3>
        <p style="color: #ccc; line-height: 1.6;">See what fans are saying on social media!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Analyze Sentiment", key="sentiment"):
        try:
            agent.show_sentiment_analysis()
            st.success("✅ Sentiment analyzed!")
        except Exception as e:
            st.error(f"Error analyzing sentiment: {e}")

with tab4:
    st.markdown("""
    <div class="fun-fact">
        <strong>📚 Super Bowl Fact:</strong> The Super Bowl is watched by over 100 million people worldwide, making it one of the most-watched sporting events! This is Super Bowl LX (60 in Roman numerals) - a historic game!
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Show Fun Fact", key="fun_fact"):
        try:
            agent.show_fun_fact()
            st.success("✅ Fun fact displayed!")
        except Exception as e:
            st.error(f"Error showing fun fact: {e}")

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