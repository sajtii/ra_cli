import time
import argparse
import configparser
import requests
import os
from datetime import datetime, timezone
from pypresence import Presence
from pypresence.types import ActivityType
from pypresence.types import StatusDisplayType

appid = "1478833716725022866"

#trimming the rich presence message for discord in case it is too long. Temporary for now, till I find a better solution.
def trimmer(text):
    if len(text.encode("utf_16_le")) <= 256:
        return text
    else:
        final = ""
        size = 0
        for i in text:
            size += len(i.encode("utf_16_le"))
            if size > 250:
                return final + "..."
            final += i

def get_no_cache_string():
    """Generate datetime string in format ddMMyyyyHHmmss for cache busting"""
    now = datetime.now()
    return now.strftime('%d%m%Y%H%M%S')

def ra_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None

def clear_term():
    os.system('cls' if os.name == 'nt' else 'clear')

def switch(a):
    if a == "0":
        return "1"
    else:
        return "0"

def settings():
    config = configparser.ConfigParser()
    config.read('config.ini')
    username = config.get('RA', 'username')
    apikey = config.get('RA', 'apikey')
    bt_prof = config.get('BT', 'profile')
    bt_gpage = config.get('BT', 'gamepage')
    interval = config.get('MISC', 'interval')
    timeout = config.get('MISC', 'timeout')

    while True:
        clear_term()
        print(f"1. Username: {username}")
        print(f"2. API Key: {apikey}")
        print(f"3. Update interval: {interval} seconds")
        print(f"4. Timeout: {timeout}{" seconds" if int(timeout) > 0 else " (disabled)"}")
        print(f"5. Buttons")
        print("")
        print("6. Save & Exit")
        print("7. Exit without saving")
        print("")
        choice = input("> ")
        print("")
        if choice == "1":
            clear_term()
            username = input("Enter your RA Username: ")
        elif choice == "2":
            clear_term()
            apikey = input("Enter your RA Web API Key: ")
        elif choice == "3":
            clear_term()
            interval = input('Set the update interval in seconds (min. 5): ')
            try:
                interval = int(interval)
                if interval < 5:
                    interval = 5
            except ValueError:
                interval = 5
        elif choice == "4":
            clear_term()
            print('After the Rich Presence message date is older than the specified number of seconds, the script stops updating Discord rich presence.')
            print('For example, if the timeout is set to 300 (5 minutes), the script will stop updating Discord when the Rich Presence message is older than 5 minutes.')
            print('Enter 0 to disable this feature.')
            print('The minimum value is 130 because things on RA seem to get updated every 2 minutes after you launch into a game.')
            timeout = input('Set the timeout value in seconds (0 to disable): ')
            try:
                t = int(timeout)
                if 0 < t < 130:
                    timeout = "130"
            except ValueError:
                timeout = "0"

        elif choice == "5":
            while True:
                clear_term()
                print("Here you can enable or disable different buttons on your profile.")
                print("One leads to your RA profile page, the other to the page of the game you currently playing.")
                print("Note: You can't see them on your own profile, but others will do so don't panic.")
                print("")
                print(f"1. Current game button: {"Enabled" if bt_gpage == "1" else "Disabled"}")
                print(f"2. RA profile button: {"Enabled" if bt_prof == "1" else "Disabled"}")
                print("3. Back")
                print("")
                choice = input("> ")
                print("")
                if choice == "1":
                    bt_gpage = switch(bt_gpage)
                elif choice == "2":
                    bt_prof = switch(bt_prof)
                elif choice == "3":
                    break

        elif choice == "6":
            config['RA']['username'] = str(username)
            config['RA']['apikey'] = str(apikey)
            config['BT']['profile'] = str(bt_prof)
            config['BT']['gamepage'] = str(bt_gpage)
            config['MISC']['interval'] = str(interval)
            config['MISC']['timeout'] = str(timeout)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            clear_term()
            break
        elif choice == "7":
            clear_term()
            break
    
def main():
    #loading config values
    config = configparser.ConfigParser()
    config.read('config.ini')
    data = configparser.ConfigParser()
    data.read('data.ini')
    username = config.get('RA', 'username')
    apikey = config.get('RA', 'apikey')
    bt_prof = config.get('BT', 'profile')
    bt_game = config.get('BT', 'gamepage')
    try:
        interval = int(config.get('MISC', 'interval'))
        if interval < 5:
            interval = 5
    except ValueError:
        interval = 5
    try:
        timeout = int(config.get('MISC', 'timeout'))
        if 0 < timeout < 130:
            timeout = 130
    except ValueError:
        timeout = 0

    current_game = None
    RPC = Presence(appid)
    rpc_connected = False
    rpc_status = 0
    rpc_st_text = ["Inactive", "Active", "", "Error!"]
    login = True

    start_time = None
    achi_earned = ""
    achi_text = ""

    log_points = None
    log_game_title = None
    log_num_achi = None
    log_rpc_status = None
    log_rpc_text = None

    while True:
        #fetching data from RA
        no_cache = get_no_cache_string()
        ra_userdata = ra_data(f"https://retroachievements.org/API/API_GetUserSummary.php?u={username}&y={apikey}&g=0&a=0&noCache={no_cache}")
        if ra_userdata == None:
            rpc_status = 3
        else:
            if login:
                login = False
                print(f"Logged in as: {username}")
                if ra_userdata['Motto'] != "":
                    print(f"{ra_userdata['Motto']}")

            rp_date_str = ra_userdata.get("RichPresenceMsgDate")
            rp_date = datetime.strptime(rp_date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            current_date = datetime.now(timezone.utc)
            time_diff = (current_date - rp_date).total_seconds()
            if time_diff <= timeout or timeout == 0:
                rpc_status = 1
            else:
                rpc_status = 0

        if rpc_status not in [0, 3]:
            ra_game_data = ra_data(f"https://retroachievements.org/API/API_GetGame.php?z={username}&y={apikey}&i={ra_userdata['LastGameID']}")
            if ra_game_data == None:
                rpc_status = 3
            ra_game_prog = ra_data(f"https://retroachievements.org/API/API_GetUserProgress.php?y={apikey}&u={username}&i={ra_userdata['LastGameID']}")
            if ra_game_prog == None:
                rpc_status = 3
            else:
                ra_game_prog = ra_game_prog.get(f"{ra_userdata['LastGameID']}", {})

        if rpc_status not in [0, 3]:
            if current_game != ra_userdata['LastGameID']:
                if bt_game == '1':
                    button1 = {"label": "View on RetroAchievements",
                               "url": f"https://retroachievements.org/game/{ra_userdata['LastGameID']}"}
                else:
                    button1 = None
                if bt_prof == '1':
                    button2 = {"label": f"{username}'s RA Page",
                               "url": f"https://retroachievements.org/user/{username}"}
                else:
                    button2 = None
                buttons = [button1, button2]
                if button1 == None and button2 == None:
                    buttons_filtered = None
                else:
                    buttons_filtered = [d for d in buttons if d is not None]
                current_game = ra_userdata['LastGameID']


            if ra_game_prog['NumAchieved'] == 0:
                achi_earned = 0
                achi_text = "None"
                rpc_achi = f"\uD83C\uDFC6 0/{ra_game_prog['NumPossibleAchievements']} (None)"
            elif ra_game_prog['NumAchievedHardcore'] < ra_game_prog['NumAchieved']:
                achi_earned = ra_game_prog['NumAchieved']
                achi_text = "Softcore"
                rpc_achi = f"\uD83C\uDFC6 {ra_game_prog['NumAchieved']}/{ra_game_prog['NumPossibleAchievements']} (Softcore)"
            else:
                achi_earned = ra_game_prog['NumAchievedHardcore']
                achi_text = "Hardcore"
                rpc_achi = f"\uD83C\uDFC6 {ra_game_prog['NumAchievedHardcore']}/{ra_game_prog['NumPossibleAchievements']} (Hardcore)"


        if rpc_status == 1:
            if not rpc_connected:
                RPC.connect()
                rpc_connected = True
                start_time = int(time.time())
            RPC.update(
                activity_type=ActivityType.PLAYING,
                status_display_type=StatusDisplayType.NAME,
                name=ra_game_data['GameTitle'],
                details=trimmer(ra_userdata["RichPresenceMsg"]),
                state=rpc_achi,
                start=start_time,
                large_image=f"https://media.retroachievements.org{ra_game_data['ImageIcon']}",
                large_text=rpc_achi,
                small_image=data.get('CI', str(ra_game_data['ConsoleID'])),
                small_text=ra_game_data['ConsoleName'],
                buttons=buttons_filtered
            )
        elif rpc_status in [0, 3]:
            if rpc_connected:
                RPC.clear()
                RPC.close()
                rpc_connected = False

        if rpc_status == 1:
            if log_points != ra_userdata['TotalPoints']:
                log_points = ra_userdata['TotalPoints']
                print(f"Total points: {ra_userdata['TotalPoints']} ({ra_userdata['TotalTruePoints']})")

            if log_game_title != current_game:
                log_game_title = current_game
                print(f"Playing: {ra_game_data['GameTitle']}")
                print(f"Console: {ra_game_data['ConsoleName']}")
                log_num_achi = achi_earned
                print(f"Achivements: {achi_earned}/{ra_game_prog['NumPossibleAchievements']} ({achi_text})")

            if log_num_achi != achi_earned:
                log_num_achi = achi_earned
                print(f"Achivements: {achi_earned}/{ra_game_prog['NumPossibleAchievements']} ({achi_text})")

            if log_rpc_text != ra_userdata['RichPresenceMsg']:
                log_rpc_text = ra_userdata['RichPresenceMsg']
                print(f"Details: {ra_userdata['RichPresenceMsg']}")

        if log_rpc_status != rpc_status:
            log_rpc_status = rpc_status
            print(f"RPC Status: {rpc_st_text[rpc_status]}")

        for i in range(interval):
            time.sleep(1)

    print("Something went wrong! Check your settings (python racli.py -s) and make sure your details are correct.")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--settings', action='store_true')
    args = parser.parse_args()
    if args.settings:
        settings()
    else:
        main()
