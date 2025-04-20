from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
import os

app = Flask(__name__)

# Get clan name from environment variable or use default
clan_name = os.environ.get('CLAN_NAME', 'Bladblazers!')

@app.route('/')
def home():
    return render_template('home.html', title='Game Tools & Overviews', clan_name=clan_name)

@app.route('/tools')
def tools():
    return render_template('tools.html', title='RS3 Tools', clan_name=clan_name)

@app.route('/rs-tools')
def rs_tools():
    return render_template('rs_tools.html', title='RS3 Player Data', clan_name=clan_name)

@app.route('/timeline', methods=['GET', 'POST'])
def timeline():
    timeline_data = []
    usernames = None
    user_colors = {}
    error = None
    
    if request.method == 'POST':
        usernames = request.form.get('usernames', '')
    else:
        # Check for usernames in cookie
        usernames = request.cookies.get('last_timeline_usernames', '')
    
    if usernames:
        # Split the comma-separated usernames and remove whitespace
        username_list = [name.strip() for name in usernames.split(',') if name.strip()]
        
        # Generate muted colors for each username
        colors = [
            "#e6b8af", "#f4cccc", "#fce5cd", "#fff2cc", "#d9ead3", 
            "#d0e0e3", "#c9daf8", "#cfe2f3", "#d9d2e9", "#ead1dc",
            "#dd7e6b", "#ea9999", "#f9cb9c", "#ffe599", "#b6d7a8", 
            "#a2c4c9", "#a4c2f4", "#9fc5e8", "#b4a7d6", "#d5a6bd"
        ]
        
        # Assign colors to usernames
        for i, username in enumerate(username_list):
            user_colors[username] = colors[i % len(colors)]
        
        # Fetch activities for each username
        all_activities = []
        for username in username_list:
            try:
                url = f"https://apps.runescape.com/runemetrics/profile/profile?user={username}&activities=20"
                response = requests.get(url)
                
                if response.status_code == 200:
                    profile_data = response.json()
                    # Check if profile exists
                    if 'error' in profile_data:
                        error = f"Profile not found for username: {username}"
                        continue
                    
                    # Add username to each activity
                    if 'activities' in profile_data:
                        for activity in profile_data['activities']:
                            activity['username'] = username
                            all_activities.append(activity)
                else:
                    error = f"Error fetching profile for {username}: HTTP {response.status_code}"
            except Exception as e:
                error = f"Error: {str(e)}"
        
        # Sort all activities by date (most recent first)
        # The date format in the API is like "27-Apr-2023 21:13"
        from datetime import datetime
        
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, "%d-%b-%Y %H:%M")
            except:
                # Fallback to a default date if parsing fails
                return datetime(1970, 1, 1)
        
        all_activities.sort(key=lambda x: parse_date(x.get('date', '')), reverse=True)
        timeline_data = all_activities
    
    resp = make_response(render_template('timeline.html', title='RuneScape Activity Timeline', 
                        timeline_data=timeline_data, usernames=usernames, 
                        user_colors=user_colors, error=error, clan_name=clan_name))
    
    # Set cookie if usernames were provided via POST
    if request.method == 'POST' and usernames:
        resp.set_cookie('last_timeline_usernames', usernames, max_age=60*60*24*30)  # 30 days
    
    return resp

@app.route('/highscores', methods=['GET', 'POST'])
def highscores():
    highscores_data = None
    username = None
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
    else:
        # Check for username in cookie
        username = request.cookies.get('last_highscores_username')
    
    if username:
        try:
            # URL encode the username
            encoded_username = requests.utils.quote(username)
            url = f"https://secure.runescape.com/m=hiscore/index_lite.ws?player={encoded_username}"
            response = requests.get(url)
            
            if response.status_code == 200:
                # Parse the high scores data
                highscores_data = parse_highscores(response.text)
            else:
                error = f"Error fetching high scores: HTTP {response.status_code}"
        except Exception as e:
            error = f"Error: {str(e)}"
    
    resp = make_response(render_template('highscores.html', title='RuneScape High Scores', 
                        highscores_data=highscores_data, username=username, error=error, clan_name=clan_name))
    
    # Set cookie if username was provided via POST
    if request.method == 'POST' and username:
        resp.set_cookie('last_highscores_username', username, max_age=60*60*24*30)  # 30 days
    
    return resp

def parse_highscores(data):
    # Define the order of skills and activities in the high scores data
    skills = [
        "Total", "Attack", "Defence", "Strength", "Constitution", "Ranged",
        "Prayer", "Magic", "Cooking", "Woodcutting", "Fletching", "Fishing",
        "Firemaking", "Crafting", "Smithing", "Mining", "Herblore", "Agility",
        "Thieving", "Slayer", "Farming", "Runecrafting", "Hunter", "Construction",
        "Summoning", "Dungeoneering", "Divination", "Invention", "Archaeology", "Necromancy"
    ]
    
    activities = [
        "Bounty Hunter", "Bounty Hunter Rogues", "Dominion Tower",
        "The Crucible", "Castle Wars", "Barbarian Assault attackers", "Barbarian Assault defenders",
        "Barbarian Assault collectors", "Barbarian Assault healers", "Dual Arena Tournaments", "Mobilising Armies", 
        "Conquest", "Fist of Guthix", "GG: Resource Race", "GG: Athletics",
        "WE2: Armadyl Lifetime Contribution", "WE2: Bandos Lifetime Contribution", "WE2: Armadyl PvP Kills", 
        "WE2: Bandos PvP Kills", "Heist Guard Level", "Heist Robber Level", "CFP: 5 Game Average", "RuneScore",
        "Clue scrolls (easy)", "Clue scrolls (medium)", "Clue scrolls (hard)",
        "Clue scrolls (elite)", "Clue scrolls (master)"
    ]
    
    # Split the data into lines
    lines = data.strip().split('\n')
    
    result = {
        'skills': {},
        'activities': {}
    }
    
    # Parse skills data (first 30 lines)
    for i in range(min(len(skills), len(lines))):
        parts = lines[i].split(',')
        if len(parts) >= 3:
            rank = int(parts[0]) if parts[0] != '-1' else -1
            level = int(parts[1]) if parts[1] != '-1' else -1
            xp = int(parts[2]) if parts[2] != '-1' else -1
            
            result['skills'][skills[i]] = {
                'rank': rank,
                'level': level,
                'xp': xp
            }
    
    # Parse activities data (remaining lines)
    for i in range(len(skills), min(len(skills) + len(activities), len(lines))):
        activity_index = i - len(skills)
        if activity_index < len(activities):
            parts = lines[i].split(',')
            if len(parts) >= 2:
                rank = int(parts[0]) if parts[0] != '-1' else -1
                score = int(parts[1]) if parts[1] != '-1' else -1
                
                result['activities'][activities[activity_index]] = {
                    'rank': rank,
                    'score': score
                }
    
    return result


@app.route('/compare', methods=['GET', 'POST'])
def compare():
    profile_data1 = None
    profile_data2 = None
    username1 = None
    username2 = None
    error = None
    
    if request.method == 'POST':
        username1 = request.form.get('username1')
        username2 = request.form.get('username2')
    else:
        # Check for usernames in cookies
        username1 = request.cookies.get('last_compare_username1')
        username2 = request.cookies.get('last_compare_username2')
    
    # Fetch profile 1 if username1 is provided
    if username1:
        try:
            url1 = f"https://apps.runescape.com/runemetrics/profile/profile?user={username1}&activities=20"
            response1 = requests.get(url1)
            
            if response1.status_code == 200:
                profile_data1 = response1.json()
                # Check if profile exists
                if 'error' in profile_data1:
                    error = f"Profile not found for username: {username1}"
                    profile_data1 = None
            else:
                error = f"Error fetching profile for {username1}: HTTP {response1.status_code}"
        except Exception as e:
            error = f"Error fetching profile 1: {str(e)}"
    
    # Fetch profile 2 if username2 is provided
    if username2:
        try:
            url2 = f"https://apps.runescape.com/runemetrics/profile/profile?user={username2}&activities=20"
            response2 = requests.get(url2)
            
            if response2.status_code == 200:
                profile_data2 = response2.json()
                # Check if profile exists
                if 'error' in profile_data2:
                    error = f"Profile not found for username: {username2}"
                    profile_data2 = None
            else:
                error = f"Error fetching profile for {username2}: HTTP {response2.status_code}"
        except Exception as e:
            error = f"Error fetching profile 2: {str(e)}"
    
    resp = make_response(render_template('compare.html', title='Compare RuneScape Profiles', 
                        profile_data1=profile_data1, profile_data2=profile_data2,
                        username1=username1, username2=username2, error=error, clan_name=clan_name))
    
    # Set cookies if usernames were provided via POST
    if request.method == 'POST':
        if username1:
            resp.set_cookie('last_compare_username1', username1, max_age=60*60*24*30)  # 30 days
        if username2:
            resp.set_cookie('last_compare_username2', username2, max_age=60*60*24*30)  # 30 days
    
    return resp


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    profile_data = None
    username = None
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
    else:
        # Check for username in cookie
        username = request.cookies.get('last_profile_username')
    
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
    
    resp = make_response(render_template('profile.html', title='RuneScape Profile', 
                        profile_data=profile_data, username=username, error=error, clan_name=clan_name))
    
    # Set cookie if username was provided via POST
    if request.method == 'POST' and username:
        resp.set_cookie('last_profile_username', username, max_age=60*60*24*30)  # 30 days
    
    return resp


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

# XP required for each level
XP_TABLE = [
    0, 83, 174, 276, 388, 512, 650, 801, 969, 1154, 1358, 1584, 1833, 2107, 2411, 2746, 3115, 3523, 3973, 4470,
    5018, 5624, 6291, 7028, 7842, 8740, 9730, 10824, 12031, 13363, 14833, 16456, 18247, 20224, 22406, 24815, 27473,
    30408, 33648, 37224, 41171, 45529, 50339, 55649, 61512, 67983, 75127, 83014, 91721, 101333, 111945, 123660,
    136594, 150872, 166636, 184040, 203254, 224466, 247886, 273742, 302288, 333804, 368599, 407015, 449428, 496254,
    547953, 605032, 668051, 737627, 814445, 899257, 992895, 1096278, 1210421, 1336443, 1475581, 1629200, 1798808,
    1986068, 2192818, 2421087, 2673114, 2951373, 3258594, 3597792, 3972294, 4385776, 4842295, 5346332, 5902831,
    6517253, 7195629, 7944614, 8771558, 9684577, 10692629, 11805606, 13034431, 14391160, 15889109, 17542976, 
    19368992, 21385073, 23611006, 26068632, 28782069, 31777943, 35085654, 38737661, 42769801, 47221641, 52136869,
    57563718, 63555443, 70170840, 77474828, 85539082, 94442737, 104273167, 115126838, 127110260, 140341028,
    154948977, 171077457, 188884740, 200000000
]

# XP required for each level for Invention (Elite skill)
INVENTION_XP_TABLE = [
    0, 830, 1861, 2902, 3980, 5126, 6390, 7787, 9400, 11275, 13605, 16372, 19656, 23546, 28138, 33520, 39809, 
    47109, 55535, 64802, 77190, 90811, 106221, 123573, 143025, 164742, 188893, 215651, 245196, 277713, 316311, 
    358547, 404634, 454796, 509259, 568254, 632019, 700797, 774834, 854383, 946227, 1044569, 1149696, 1261903, 
    1381488, 1508756, 1644015, 1787581, 1939773, 2100917, 2283490, 2476369, 2679907, 2894505, 3120508, 3358307, 
    3608290, 3870846, 4146374, 4435275, 4758122, 5096111, 5449685, 5819299, 6205407, 6608473, 7028964, 7467354, 
    7924122, 8399751, 8925664, 9472665, 10041285, 10632061, 11245538, 11882262, 12542789, 13227679, 13937496, 
    14672812, 15478994, 16313404, 17176661, 18069395, 18992239, 19945833, 20930821, 21947856, 22997593, 24080695, 
    25259906, 26475754, 27728955, 29020233, 30350318, 31719944, 33129852, 34580790, 36073511, 37608773, 39270442, 
    40978509, 42733789, 44537107, 46389292, 48291180, 50243611, 52247435, 54303504, 56412678, 58575823, 60793812, 
    63067521, 65397835, 67785643, 70231841, 72737330, 75303019, 77929820, 80618654, 83370445, 86186124, 89066630, 
    92012904, 95025896, 98106559, 101255855, 104474750, 107764216, 111125230, 114558777, 118065845, 121647430, 
    125304532, 129038159, 132849323, 136739041, 140708338, 144758242, 148889790, 153104021, 157401983, 161784728, 
    166253312, 170808801, 175452262, 180184770, 185007406, 189921255, 194927409, 200000000
]

@app.template_filter('get_skill_name')
def get_skill_name(skill_id):
    return SKILL_NAMES.get(skill_id, f"Skill {skill_id}")

@app.template_filter('get_xp_progress')
def get_xp_progress(level, xp, skill_name=None):
    """Calculate the XP progress percentage for the current level"""
    if xp >= 200000000:  # Max XP
        return 100
    
    # Use Invention XP table for Invention skill
    if skill_name == "Invention":
        xp_table = INVENTION_XP_TABLE
    else:
        xp_table = XP_TABLE
    
    # Find the current level based on XP
    current_level = 1
    for i in range(1, len(xp_table)):
        if xp >= xp_table[i-1] and xp < xp_table[i]:
            current_level = i
            break
    
    # If XP is at max level
    if current_level >= len(xp_table) - 1:
        return 100
    
    current_level_xp = xp_table[current_level - 1]
    next_level_xp = xp_table[current_level]
    
    xp_for_level = next_level_xp - current_level_xp
    xp_gained = xp - current_level_xp
    
    progress = (xp_gained / xp_for_level) * 100
    return min(max(0, progress), 100)  # Ensure between 0-100

if __name__ == '__main__':
    # To run with Docker:
    # 1. Build: docker compose build
    # 2. Run: docker compose up
    app.run(host='0.0.0.0', port=5000, debug=True)
