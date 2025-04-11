from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', title='Game Tools & Overviews')

@app.route('/tools')
def tools():
    return render_template('tools.html', title='Game Tools')

@app.route('/overview')
def overview():
    return render_template('overview.html', title='Game Overview')

@app.route('/stats')
def stats():
    return render_template('stats.html', title='Game Stats')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    profile_data = None
    username = None
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            try:
                url = f"https://apps.runescape.com/runemetrics/profile/profile?user={username}&activities=20"
                response = requests.get(url)
                
                if response.status_code == 200:
                    profile_data = response.json()
                    # Check if profile exists (RuneMetrics returns empty objects for non-existent profiles)
                    if 'error' in profile_data:
                        error = f"Profile not found for username: {username}"
                        profile_data = None
                else:
                    error = f"Error fetching profile: HTTP {response.status_code}"
            except Exception as e:
                error = f"Error: {str(e)}"
    
    return render_template('profile.html', title='RuneScape Profile', 
                          profile_data=profile_data, username=username, error=error)

# Dictionary to map skill IDs to skill names
SKILL_NAMES = {
    0: "Attack", 1: "Defence", 2: "Strength", 3: "Constitution", 4: "Ranged",
    5: "Prayer", 6: "Magic", 7: "Cooking", 8: "Woodcutting", 9: "Fletching",
    10: "Fishing", 11: "Firemaking", 12: "Crafting", 13: "Smithing", 14: "Mining",
    15: "Herblore", 16: "Agility", 17: "Thieving", 18: "Slayer", 19: "Farming",
    20: "Runecrafting", 21: "Hunter", 22: "Construction", 23: "Summoning",
    24: "Dungeoneering", 25: "Divination", 26: "Invention", 27: "Archaeology",
    28: "Necromancy"
}

@app.template_filter('get_skill_name')
def get_skill_name(skill_id):
    return SKILL_NAMES.get(skill_id, f"Skill {skill_id}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
