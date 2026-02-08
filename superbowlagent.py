#!/usr/bin/env python3
"""
Super Bowl Live Agent
Real-time game updates, NFL explanations, sentiment tracking, and more!
Super Bowl LX: Patriots vs Seahawks - February 8, 2026
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Optional
import anthropic
from dotenv import load_dotenv

load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Game state tracking
game_state = {
    "current_score": {"NE": 0, "SEA": 0},
    "quarter": 1,
    "time_remaining": "15:00",
    "game_started": False,
    "game_ended": False,
    "previous_score": {"NE": 0, "SEA": 0},
    "possession": "NE",
    "commercials_seen": [],
    "halftime_passed": False,
    "notable_plays": [],
    "player_stats": {},
    "win_probability": {"NE": 55, "SEA": 45},
}

NFL_CONTEXT = {
    "teams": {
        "NE": {"name": "New England Patriots", "color": "Navy Blue & Silver"},
        "SEA": {"name": "Seattle Seahawks", "color": "Navy Blue & Neon Green"}
    },
    "positions": {
        "QB": "Quarterback - Throws the ball",
        "RB": "Running Back - Runs with the ball",
        "WR": "Wide Receiver - Catches the ball downfield",
        "TE": "Tight End - Block and catch",
        "OL": "Offensive Line - Protects QB",
        "DL": "Defensive Line - Rush the QB",
        "LB": "Linebacker - Defend the middle",
        "CB": "Cornerback - Cover receivers",
        "S": "Safety - Last line of defense"
    },
    "fun_facts": [
        "The Super Bowl is watched by over 100 million people worldwide!",
        "This is the 60th Super Bowl (hence 'LX' in Roman numerals)",
        "The winning team gets the Lombardi Trophy, named after legendary coach Vince Lombardi",
        "Super Bowl ads cost millions of dollars for 30 seconds of airtime",
        "The average Super Bowl viewer watches for 4+ hours",
        "Patriots have won 6 Super Bowls (most in NFL history at their peak)",
        "Seahawks are known for their 'Legion of Boom' defense",
        "The Super Bowl halftime show draws viewers even from non-sports fans"
    ]
}

class SuperBowlAgent:
    def __init__(self):
        self.update_count = 0
        self.api_calls_made = 0
        
    def format_header(self, text: str):
        """Format section headers"""
        return f"\n{'='*60}\n{text.center(60)}\n{'='*60}\n"
    
    def get_score_display(self):
        """Display current score"""
        ne_score = game_state["current_score"]["NE"]
        sea_score = game_state["current_score"]["SEA"]
        
        display = f"""
        NEW ENGLAND PATRIOTS    {ne_score}
        SEATTLE SEAHAWKS       {sea_score}
        
        Quarter: {game_state['quarter']} | Time: {game_state['time_remaining']}
        """
        return display
    
    def generate_eli5_explanation(self, topic: str) -> str:
        """Generate beginner-friendly NFL explanations using Claude"""
        prompt = f"""
        The user is NEW to American football and the NFL. They're watching their first Super Bowl.
        
        Explain this concept in VERY simple, beginner-friendly language (ELI5 style):
        Topic: {topic}
        
        Keep it to 2-3 sentences MAX. Use everyday analogies. Be fun and engaging!
        """
        
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        self.api_calls_made += 1
        return message.content[0].text
    
    def generate_commentary(self, play_description: str) -> str:
        """Generate exciting color commentary for plays"""
        prompt = f"""
        Write exciting, brief color commentary (like an NFL commentator) for this Super Bowl play.
        Be energetic but informative. 2-3 sentences MAX.
        
        Play: {play_description}
        
        Make it sound like you're announcing on ESPN!
        """
        
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        self.api_calls_made += 1
        return message.content[0].text
    
    def analyze_sentiment(self, topic: str) -> dict:
        """Analyze social media sentiment (simulated with Claude)"""
        prompt = f"""
        Simulate what Twitter/X sentiment might be about this Super Bowl moment:
        Topic: {topic}
        
        Return a JSON object with:
        - sentiment: "positive", "negative", or "mixed"
        - trending_hashtags: list of 3 trending hashtags
        - key_takeaway: one sentence summary
        
        Return ONLY valid JSON, no other text.
        """
        
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        self.api_calls_made += 1
        
        try:
            return json.loads(message.content[0].text)
        except:
            return {
                "sentiment": "mixed",
                "trending_hashtags": ["#SuperBowlLX", "#PatriotsVsSeahawks", "#SB60"],
                "key_takeaway": "Fans are engaged!"
            }
    
    def get_win_probability_explanation(self):
        """Explain why win probability is what it is"""
        ne_prob = game_state["win_probability"]["NE"]
        sea_prob = game_state["win_probability"]["SEA"]
        leader = "Patriots" if game_state["current_score"]["NE"] > game_state["current_score"]["SEA"] else "Seahawks"
        
        prompt = f"""
        Current Super Bowl situation:
        - Patriots have {ne_prob}% win probability
        - Seahawks have {sea_prob}% win probability
        - {leader} are leading
        - Quarter: {game_state['quarter']}
        
        In 1-2 sentences, explain why these odds make sense in simple terms for a football beginner.
        """
        
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        self.api_calls_made += 1
        return message.content[0].text
    
    def simulate_game_update(self):
        """Fetch real live game data from ESPN API"""
        try:
            # ESPN API endpoint for NFL scoreboard
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            events = data.get("events", [])
            
            # Find Super Bowl game (Patriots vs Seahawks)
            for event in events:
                competitions = event.get("competitions", [])
                if not competitions:
                    continue
                
                comp = competitions[0]
                competitors = comp.get("competitors", [])
                
                if len(competitors) < 2:
                    continue
                
                # Get team info
                team1 = competitors[0].get("team", {})
                team2 = competitors[1].get("team", {})
                
                abbr1 = team1.get("abbreviation", "")
                abbr2 = team2.get("abbreviation", "")
                
                # Check if this is our Super Bowl game
                if (abbr1 in ["NE", "SEA"]) and (abbr2 in ["NE", "SEA"]):
                    
                    # Update scores
                    score1 = int(competitors[0].get("score", 0))
                    score2 = int(competitors[1].get("score", 0))
                    
                    if abbr1 == "NE":
                        game_state["current_score"]["NE"] = score1
                        game_state["current_score"]["SEA"] = score2
                    else:
                        game_state["current_score"]["SEA"] = score1
                        game_state["current_score"]["NE"] = score2
                    
                    # Get game status
                    status = comp.get("status", {})
                    period = status.get("period", 1)
                    game_state["quarter"] = period
                    
                    # Get game clock
                    display_clock = status.get("displayClock", "15:00")
                    game_state["time_remaining"] = display_clock
                    
                    # Get possession
                    situation = comp.get("situation", {})
                    possession = situation.get("possession", "NE")
                    game_state["possession"] = possession
                    
                    # Update win probability if available
                    odds = comp.get("odds", [])
                    if odds:
                        for odd in odds:
                            if odd.get("provider", {}).get("name") == "ESPN":
                                win_prob = odd.get("awayTeamOdds", {}).get("winProbability")
                                if win_prob:
                                    if abbr1 == "NE":
                                        game_state["win_probability"]["NE"] = int(float(win_prob) * 100)
                                        game_state["win_probability"]["SEA"] = 100 - game_state["win_probability"]["NE"]
                                    else:
                                        game_state["win_probability"]["SEA"] = int(float(win_prob) * 100)
                                        game_state["win_probability"]["NE"] = 100 - game_state["win_probability"]["SEA"]
                    
                    # Check game status
                    status_type = status.get("type", "")
                    
                    if status_type == "final":
                        game_state["game_ended"] = True
                        return "🏆 GAME OVER! Final score is official!"
                    elif status_type == "halftime":
                        if not game_state["halftime_passed"]:
                            game_state["halftime_passed"] = True
                            return "⏸️ HALFTIME! Teams heading to locker room for the legendary halftime show!"
                    elif status_type == "in_progress":
                        if not game_state["game_started"]:
                            game_state["game_started"] = True
                            return "🚀 KICKOFF! The game has started!"
                        
                        # Detect score changes
                        ne_prev = game_state["previous_score"]["NE"]
                        sea_prev = game_state["previous_score"]["SEA"]
                        
                        ne_curr = game_state["current_score"]["NE"]
                        sea_curr = game_state["current_score"]["SEA"]
                        
                        if ne_curr > ne_prev:
                            game_state["previous_score"]["NE"] = ne_curr
                            points = ne_curr - ne_prev
                            if points == 7:
                                return "🎉 TOUCHDOWN PATRIOTS! The crowd erupts!"
                            elif points == 6:
                                return "🏈 PATRIOTS SCORE! Attempting PAT..."
                            elif points == 3:
                                return "⚽ FIELD GOAL PATRIOTS!"
                            elif points == 2:
                                return "💪 SAFETY PATRIOTS!"
                        
                        if sea_curr > sea_prev:
                            game_state["previous_score"]["SEA"] = sea_curr
                            points = sea_curr - sea_prev
                            if points == 7:
                                return "🎉 TOUCHDOWN SEAHAWKS! Incredible play!"
                            elif points == 6:
                                return "🏈 SEAHAWKS SCORE! PAT coming..."
                            elif points == 3:
                                return "⚽ FIELD GOAL SEAHAWKS!"
                            elif points == 2:
                                return "💪 SAFETY SEAHAWKS!"
                        
                        return f"📊 Live Update: Q{game_state['quarter']} | {game_state['time_remaining']}"
            
            return self._fallback_simulation()
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️ ESPN API unavailable: {e}")
            return self._fallback_simulation()
        
        except Exception as e:
            print(f"⚠️ Error parsing ESPN data: {e}")
            return self._fallback_simulation()
    
    def _fallback_simulation(self):
        """Fallback to simulated data if ESPN API is unavailable"""
        if game_state["quarter"] == 1 and game_state["time_remaining"] == "15:00":
            game_state["game_started"] = True
            return "KICKOFF! The game has started!"
        
        # Simulate score changes every few updates
        if self.update_count % 3 == 0 and not game_state["game_ended"]:
            if self.update_count % 6 == 0:
                game_state["current_score"]["NE"] += 7
                return "TOUCHDOWN PATRIOTS! Crowd goes wild!"
            else:
                game_state["current_score"]["SEA"] += 3
                return "Field goal for the Seahawks! Points on the board!"
        
        # Update quarter and time
        if self.update_count % 8 == 0 and game_state["quarter"] < 4:
            game_state["quarter"] += 1
            game_state["time_remaining"] = "15:00"
            return f"END OF QUARTER {game_state['quarter']-1}! Moving to Quarter {game_state['quarter']}"
        
        if self.update_count % 2 == 0:
            # Decrement time
            mins, secs = map(int, game_state["time_remaining"].split(":"))
            secs -= 30
            if secs < 0:
                secs += 60
                mins -= 1
            game_state["time_remaining"] = f"{mins:02d}:{secs:02d}"
        
        # Halftime at end of Q2
        if game_state["quarter"] == 2 and self.update_count % 10 == 0 and not game_state["halftime_passed"]:
            game_state["halftime_passed"] = True
            return "HALFTIME! Time for the legendary halftime show!"
        
        # Check if game is ending
        if game_state["quarter"] == 4 and game_state["time_remaining"] == "00:00":
            game_state["game_ended"] = True
            return "GAME OVER!"
        
        return None
    
    def show_basic_nfl_lesson(self, lesson_topic: str):
        """Show NFL education snippets"""
        print(self.format_header(f"🏈 NFL BASICS: {lesson_topic.upper()}"))
        
        explanations = {
            "down": "Football is played in 4 chances (called 'downs') to move the ball 10 yards. If you do, you get 4 more chances!",
            "touchdown": "A touchdown is worth 6 points and happens when you get the ball into the end zone. It's the main way to score!",
            "penalty": "Breaking the rules? The opposing team gets extra yards for free.",
            "turnover": "A turnover is when the other team gets the ball - could be an interception or fumble.",
            "sack": "This is when the defense tackles the quarterback before he throws the ball!",
        }
        
        if lesson_topic.lower() in explanations:
            print(f"\n{explanations[lesson_topic.lower()]}\n")
        else:
            print(self.generate_eli5_explanation(lesson_topic))
    
    def show_player_spotlight(self):
        """Feature interesting player stats"""
        print(self.format_header("⭐ PLAYER SPOTLIGHT"))
        
        prompt = """
        Give a quick, fun fact about one of these Super Bowl players or positions.
        Make it engaging for someone new to football. 1-2 sentences.
        Just mention an interesting stat or fun tidbit!
        """
        
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        self.api_calls_made += 1
        print(f"\n{message.content[0].text}\n")
    
    def show_fun_fact(self):
        """Display Super Bowl fun facts"""
        import random
        fact = random.choice(NFL_CONTEXT["fun_facts"])
        print(f"\n📚 Fun Fact: {fact}\n")
    
    def show_sentiment_analysis(self):
        """Show social media sentiment"""
        print(self.format_header("📊 SOCIAL MEDIA SENTIMENT"))
        
        play = "recent big play" if self.update_count % 2 == 0 else "touchdown celebration"
        sentiment = self.analyze_sentiment(play)
        
        emoji = "😍" if sentiment["sentiment"] == "positive" else "😤" if sentiment["sentiment"] == "negative" else "🤔"
        
        print(f"\nSentiment: {sentiment['sentiment'].upper()} {emoji}")
        print(f"Trending: {', '.join(sentiment['trending_hashtags'])}")
        print(f"What fans are saying: {sentiment['key_takeaway']}\n")
    
    def show_commercial_break(self):
        """Show Super Bowl commercial intel"""
        if not game_state["halftime_passed"]:
            print(self.format_header("📺 COMMERCIAL BREAK"))
            print("\n🎬 Super Bowl commercials cost ~$7 million for 30 seconds!")
            print("These ads are often more talked about than the game itself.")
            print("Brands release their ads strategically during the Super Bowl.\n")
    
    def show_halftime_info(self):
        """Show halftime information"""
        if game_state["halftime_passed"]:
            print(self.format_header("🎪 HALFTIME SHOW"))
            print("\n🌟 The Super Bowl halftime show is one of the most-watched performances!")
            print("Typically features a top music artist with elaborate production.")
            print("More people stay for halftime than any other TV broadcast!\n")
    
    def show_game_status(self):
        """Show current game status with all info"""
        print(self.format_header("⚡ LIVE GAME STATUS"))
        print(self.get_score_display())
        
        print(f"Possession: {NFL_CONTEXT['teams'][game_state['possession']]['name']}")
        print(f"Win Probability: Patriots {game_state['win_probability']['NE']}% | Seahawks {game_state['win_probability']['SEA']}%")
        print(f"\n📈 Why these odds? {self.get_win_probability_explanation()}")
    
    def show_play_commentary(self):
        """Generate exciting commentary for recent plays"""
        print(self.format_header("🎙️ PLAY-BY-PLAY COMMENTARY"))
        
        plays = [
            "Patriots complete a 25-yard pass to their receiver",
            "Seahawks defense sacks the quarterback for a 8-yard loss",
            "Field goal attempt from 45 yards out",
            "Running back breaks through for a 12-yard gain"
        ]
        
        import random
        play = random.choice(plays)
        
        commentary = self.generate_commentary(play)
        print(f"\n{play}")
        print(f"Commentary: {commentary}\n")
    
    def run_update_cycle(self):
        """Run one cycle of updates"""
        self.update_count += 1
        
        print(f"\n\n{'*' * 60}")
        print(f"UPDATE #{self.update_count} - {datetime.now().strftime('%I:%M %p')}")
        print(f"{'*' * 60}")
        
        # Show game status
        self.show_game_status()
        
        # Simulate game update
        update_msg = self.simulate_game_update()
        if update_msg:
            print(f"\n🔔 {update_msg}")
        
        # Random feature based on update count
        feature = self.update_count % 7
        
        if feature == 0:
            self.show_play_commentary()
        elif feature == 1:
            self.show_basic_nfl_lesson("touchdown")
        elif feature == 2:
            self.show_sentiment_analysis()
        elif feature == 3:
            self.show_player_spotlight()
        elif feature == 4:
            self.show_fun_fact()
        elif feature == 5:
            self.show_commercial_break()
        elif feature == 6 and game_state["halftime_passed"]:
            self.show_halftime_info()
        
        # Stats summary every 5 updates
        if self.update_count % 5 == 0:
            print(self.format_header("📊 GAME STATS SUMMARY"))
            print(f"Total AI API calls made: {self.api_calls_made}")
            print(f"Updates processed: {self.update_count}")
            print(f"Game quarter: {game_state['quarter']}")
            print()
        
        if game_state["game_ended"]:
            self.show_final_summary()
            return False
        
        return True
    
    def show_final_summary(self):
        """Show game final summary"""
        print(self.format_header("🏆 GAME FINAL SUMMARY 🏆"))
        
        ne_score = game_state["current_score"]["NE"]
        sea_score = game_state["current_score"]["SEA"]
        
        print(f"\nFinal Score:")
        print(f"New England Patriots: {ne_score}")
        print(f"Seattle Seahawks: {sea_score}")
        
        if ne_score > sea_score:
            winner = "Patriots"
        else:
            winner = "Seahawks"
        
        print(f"\n🎉 SUPER BOWL CHAMPION: {winner}! 🎉")
        print(f"\nTotal updates: {self.update_count}")
        print(f"Total API calls: {self.api_calls_made}")
        print("\nThanks for experiencing your first Super Bowl with Claude!")

def main():
    """Main execution"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║          SUPER BOWL LX LIVE AGENT                         ║
    ║   Patriots vs Seahawks - February 8, 2026                ║
    ║                                                          ║
    ║   Features:                                             ║
    ║   • Real-time game updates                              ║
    ║   • Beginner-friendly NFL explanations                  ║
    ║   • Play-by-play commentary                             ║
    ║   • Social media sentiment analysis                     ║
    ║   • Player spotlights                                   ║
    ║   • Win probability tracking                            ║
    ║   • Commercial & halftime info                          ║
    ║   • Fun facts & exciting moments                        ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    agent = SuperBowlAgent()
    
    print("\n⏳ Game is about to start! Updates will begin shortly...\n")
    time.sleep(300)
    
    # Run update cycle - for demo, run 10 cycles, but can be continuous
    while True:
        try:
            should_continue = agent.run_update_cycle()
            
            if not should_continue:
                break
            
            # In real scenario, this would be much longer (every few minutes)
            # For demo, 2 seconds between updates
            print("\n⏳ Next update in 2 seconds...")
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for watching! Come back for next year's Super Bowl!")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()