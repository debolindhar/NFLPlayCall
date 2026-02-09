#!/usr/bin/env python3
"""
Super Bowl Live Agent
Real-time game updates, NFL explanations, sentiment tracking, and more!
Super Bowl LX: Patriots vs Seahawks - February 8, 2026
"""

import os
import json
import time
import random
import requests
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import anthropic
from zoneinfo import ZoneInfo

load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Super Bowl LX Start Time: February 8, 2026 at 6:30 PM ET
SUPER_BOWL_START_TIME = datetime(2026, 2, 8, 18, 30, 0)  # 6:30 PM ET
SUPER_BOWL_DURATION = 4 * 60 * 15  # 4 quarters * 60 minutes * 15 seconds per minute

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
    "game_start_timestamp": None,
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
        game_state["game_start_timestamp"] = time.time()
    
    def format_header(self, text: str):
        """Format section headers"""
        return f"\n{'='*60}\n{text}\n{'='*60}\n"
    
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
    
    def get_game_time(self, user_timezone="America/New_York"):
        """Calculate game time based on when the game started"""
        
        if not game_state["game_started"]:
            return "15:00", 1
        
        # Get elapsed time since game started (in seconds)
        elapsed_seconds = time.time() - game_state["game_start_timestamp"]
        
        # Each real second = 2 seconds of game time (speed up gameplay)
        game_seconds_elapsed = elapsed_seconds * 2
        
        # Calculate quarter and time remaining
        seconds_per_quarter = 15 * 60  # 15 minutes per quarter
        
        quarter = int(game_seconds_elapsed // seconds_per_quarter) + 1
        quarter = min(quarter, 4)  # Cap at quarter 4
        
        # Time remaining in current quarter
        seconds_in_quarter = int(game_seconds_elapsed % seconds_per_quarter)
        seconds_remaining = seconds_per_quarter - seconds_in_quarter
        
        minutes = seconds_remaining // 60
        seconds = seconds_remaining % 60
        
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        game_state["quarter"] = quarter
        game_state["time_remaining"] = time_str
        
        # End game at quarter 4, 0:00
        if quarter == 4 and minutes == 0 and seconds == 0:
            game_state["game_ended"] = True
        
        return time_str, quarter
    
    def get_user_local_time(self, user_timezone="America/New_York"):
        """Get current time in user's timezone"""
        try:
            tz = ZoneInfo(user_timezone)
            local_time = datetime.now(tz)
            return local_time.strftime("%I:%M %p %Z")
        except:
            return datetime.now().strftime("%I:%M %p")
    
    def simulate_game_update(self):
        """Fetch real live game data using Sports API"""
        self.update_count += 1
        
        try:
            # Try ESPN API
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            games = response.json().get("events", [])
            
            for game in games:
                competitors = game.get("competitions", [{}])[0].get("competitors", [])
                
                if len(competitors) >= 2:
                    team1 = competitors[0].get("team", {}).get("abbreviation", "")
                    team2 = competitors[1].get("team", {}).get("abbreviation", "")
                    
                    if (team1 in ["NE", "SEA"]) and (team2 in ["NE", "SEA"]):
                        
                        # Update scores
                        score1 = int(competitors[0].get("score", 0))
                        score2 = int(competitors[1].get("score", 0))
                        
                        if team1 == "NE":
                            game_state["current_score"]["NE"] = score1
                            game_state["current_score"]["SEA"] = score2
                        else:
                            game_state["current_score"]["SEA"] = score1
                            game_state["current_score"]["NE"] = score2
                        
                        # Get real ESPN time
                        clock = game.get("competitions", [{}])[0].get("status", {}).get("displayClock", "15:00")
                        if clock and ":" in clock:
                            game_state["time_remaining"] = clock
                        
                        # Get period
                        period = game.get("competitions", [{}])[0].get("status", {}).get("period", 1)
                        game_state["quarter"] = period
                        
                        # Get possession
                        possession_team = game.get("competitions", [{}])[0].get("situation", {}).get("possession", "NE")
                        game_state["possession"] = possession_team
                        
                        # Check status
                        status = game.get("status", {}).get("type", {}).get("description", "")
                        
                        if status == "Final":
                            game_state["game_ended"] = True
                        elif status == "Halftime":
                            if not game_state["halftime_passed"]:
                                game_state["halftime_passed"] = True
                        
                        game_state["game_started"] = True
                        return f"Update: {status}"
            
            # If ESPN data not available, use simulated time
            return self._fallback_simulation()
        
        except Exception as e:
            print(f"ESPN API Error: {e}")
            return self._fallback_simulation()
    
    def _fallback_simulation(self):
        """Fallback to simulated data with calculated time"""
        
        game_state["game_started"] = True
        
        # Use calculated game time
        time_str, quarter = self.get_game_time()
        
        # Simulate score changes
        if self.update_count % 10 == 0 and not game_state["game_ended"]:
            if random.choice([True, False]):
                game_state["current_score"]["NE"] += random.choice([3, 6, 7])
            else:
                game_state["current_score"]["SEA"] += random.choice([3, 6, 7])
        
        return f"Simulated: Q{quarter} {time_str}"
    
    def show_basic_nfl_lesson(self, lesson_topic: str):
        """Show beginner-friendly NFL explanations"""
        
        lesson_topic = lesson_topic.lower().strip()
        
        prompt = f"""
        Explain this NFL concept in VERY simple, beginner-friendly language for someone watching their FIRST Super Bowl.
        Topic: {lesson_topic}
        
        Requirements:
        - Use everyday analogies and comparisons
        - Keep it to 2-3 sentences MAX
        - Be fun and engaging
        - Avoid technical jargon
        - Use simple words a 10-year-old would understand
        
        Example for "touchdown":
        "A touchdown is when you get the ball into the opponent's end zone - like scoring in soccer! It's worth 6 points and is the best way to score in football."
        
        Now explain {lesson_topic}:
        """
        
        try:
            message = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=150,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            self.api_calls_made += 1
            
            explanation = message.content[0].text.strip()
            
            if not explanation:
                explanations = {
                    "touchdown": "A touchdown is when you get the ball into the opponent's end zone. It's worth 6 points and is the best way to score!",
                    "down": "A 'down' is one attempt to move the ball forward. Each team gets 4 downs to move the ball 10 yards.",
                    "penalty": "A penalty is when a player breaks the rules. The other team gets to move closer or get extra yards.",
                    "turnover": "A turnover happens when the other team gets the ball. This can happen by interception or fumble.",
                    "sack": "A sack is when the defense tackles the quarterback behind the line. It's a big defensive play!",
                    "field goal": "A field goal is when you kick the ball through the uprights. It's worth 3 points."
                }
                return explanations.get(lesson_topic, "That's an important part of football!")
            
            return explanation
            
        except Exception as e:
            print(f"Error generating explanation: {e}")
            # Return fallback explanations
            explanations = {
                "touchdown": "A touchdown is when you get the ball into the opponent's end zone. It's worth 6 points and is the best way to score!",
                "down": "A 'down' is one attempt to move the ball forward. Each team gets 4 downs to move the ball 10 yards.",
                "penalty": "A penalty is when a player breaks the rules. The other team gets to move closer or get extra yards.",
                "turnover": "A turnover happens when the other team gets the ball. This can happen by interception or fumble.",
                "sack": "A sack is when the defense tackles the quarterback behind the line. It's a big defensive play!",
                "field goal": "A field goal is when you kick the ball through the uprights. It's worth 3 points."
            }
            return explanations.get(lesson_topic, "That's an important part of football!")
    
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
        """Show interesting Super Bowl facts"""
        
        prompt = """
        Generate ONE interesting and fun fact about the Super Bowl, NFL, or football in general.
        Make it engaging and educational for someone new to football.
        Keep it to 1-2 sentences MAX.
        
        Examples:
        - "The Super Bowl is watched by over 100 million people worldwide!"
        - "NFL footballs are made of cow leather and weigh exactly 14-15 ounces"
        - "A Super Bowl ad costs $7 million for just 30 seconds!"
        
        Now generate a unique, interesting fact:
        """
        
        try:
            message = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=150,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            self.api_calls_made += 1
            
            fact = message.content[0].text.strip()
            
            if not fact:
                return "The Super Bowl is watched by over 100 million people worldwide!"
            
            return fact
            
        except Exception as e:
            print(f"Error generating fact: {e}")
            # Return fallback fact
            return "Did you know? A Super Bowl ad costs $7 million for just 30 seconds!"
    
    def show_sentiment_analysis(self):
        """Show social media sentiment analysis"""
        
        import random
        import json
        
        sentiment_topics = [
            f"Patriots leading {game_state['current_score']['NE']}-{game_state['current_score']['SEA']}",
            f"Quarter {game_state['quarter']} action",
            f"{game_state['possession']} team has possession",
            "defensive play from the Seahawks",
            "Patriots offensive efficiency",
            f"win probability at {game_state['win_probability']['NE']}% for Patriots",
            "exciting game momentum shifts",
            "quarterback performance",
        ]
        
        topic = random.choice(sentiment_topics)
        
        prompt = f"""
        Simulate what Twitter/X sentiment might be about this Super Bowl moment:
        Topic: {topic}
        
        Return ONLY a valid JSON object (nothing else) with these exact fields:
        - sentiment: "positive", "negative", or "mixed"
        - trending_hashtags: array of 3 hashtags (without #)
        - key_takeaway: one sentence summary
        
        Example format:
        {{"sentiment": "positive", "trending_hashtags": ["PatriotsLead", "SuperBowlLX", "TouchdownParty"], "key_takeaway": "Fans love the action"}}
        """
        
        try:
            message = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=200,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            self.api_calls_made += 1
            
            response_text = message.content[0].text.strip()
            
            # Parse JSON response
            sentiment_data = json.loads(response_text)
            
            # Validate the response has required fields
            if not all(key in sentiment_data for key in ["sentiment", "trending_hashtags", "key_takeaway"]):
                raise ValueError("Missing required fields in response")
            
            return sentiment_data
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            # Return fallback data with correct structure
            return {
                "sentiment": "positive",
                "trending_hashtags": ["PatriotsLead", "SuperBowlLX", "TouchdownParty"],
                "key_takeaway": "Fans are loving the intense action and big plays!"
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            # Return fallback data with correct structure
            return {
                "sentiment": "positive",
                "trending_hashtags": ["PatriotsLead", "SuperBowlLX", "TouchdownParty"],
                "key_takeaway": "Fans are loving the intense action and big plays!"
            }
    
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
        """Generate exciting play-by-play commentary"""
        print(self.format_header("🎙️ PLAY COMMENTARY"))
        
        prompt = f"""
        You are an ESPN sports commentator doing live Super Bowl commentary.
        Current game state: Patriots {game_state['current_score']['NE']} - Seahawks {game_state['current_score']['SEA']}
        Quarter: {game_state['quarter']}, Time: {game_state['time_remaining']}
        
        Generate ONE exciting, dynamic play-by-play commentary line (2-3 sentences MAX).
        Be enthusiastic and engaging! Sound like a real sports broadcaster.
        """
        
        try:
            message = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=150,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            self.api_calls_made += 1
            commentary = message.content[0].text
            print(f"\n{commentary}\n")
            return commentary
        except Exception as e:
            print(f"Error generating commentary: {e}")
            return "TOUCHDOWN! The crowd is going wild!"
    
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