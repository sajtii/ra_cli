from blessed import Terminal
from PIL import Image, ImageEnhance
import math
import time
import sys
import argparse
import re
import configparser
import requests
import io
import os
from datetime import datetime, timezone
from pypresence import Presence
from pypresence.types import ActivityType
from pypresence.types import StatusDisplayType

term = Terminal()
appid = "1478833716725022866"

#Characterpicker for drawing the image
def charpicker(h):
    global charset
    charArr = list(charset)
    l = len(charArr)
    mul = l/256
    return charArr[math.floor(h*mul)]

#print() but better
def printer(text):
    sys.stdout.write(u'{0}'.format(text))
    sys.stdout.flush() 

#resizing and enchancing the image
def resizer(img):
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    img = img.resize((term.height,term.height),Image.LANCZOS, reducing_gap=4.0)
    img = img.convert('RGB')
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.1)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.1)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.5)
    return img.load()

#draws the main image
def drawer(pixels, size):
    for y in range(size):
        xb = 0
        for x in range(size):
            r,g,b = pixels[x,y]
            grey = int((r*0.299 + g*0.587 + b*0.114))
            #grey = int((r/3 + g/3 + b/3))
            printer(term.move_xy(xb, y)+term.color_rgb(r, g, b)(charpicker(grey)))
            xb=xb+1
            printer(term.move_xy(xb, y)+term.color_rgb(r, g, b)(charpicker(grey)))
            xb=xb+1

#splitting the text in case it is too long
def splitter(text, tx, ty, chsize):
    finaltext=''
    
    #trying to measure the real length of the printable text by removing ansi escape and replacing emojis with ee
    #I use 2 characters for spacers because it seems emojis take up 2 character slots
    junk = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|\(B)')
    emoji = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+", flags=re.UNICODE)
    evaulated = junk.sub('', text)
    evaulated = emoji.sub('ee', evaulated)
    ntx = tx
    nty = ty
    current_chunk = ''
    current_size = 0
    chunk_size = chsize
    if len(evaulated)+1 > chunk_size:      
        text = text.split()
        evaulated = evaulated.split()
        for i in range(len(evaulated)):
            if current_size + len(evaulated[i]) + 2 <= chunk_size: 
                current_chunk += text[i]+' '
                current_size += len(evaulated[i]) + 1
            else:
                finaltext += f"{term.move_xy(ntx, nty)}" + current_chunk
                nty += 1
                current_chunk = text[i]+' '
                current_size = len(evaulated[i]) + 1
        if current_chunk:
            finaltext +=f"{term.move_xy(ntx, nty)}" + current_chunk
            nty += 1
        current_chunk = ''
        current_size = 0
        return finaltext, ntx, nty
    else:
        finaltext += f"{term.move_xy(ntx, nty)}" + text
        nty += 1
        return finaltext, ntx, nty

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

#highlits the rich presence message
def highlighter(text):
    dark_orchid = f'{term.darkorchid1}'
    red = f'{term.red}'
    green = f'{term.green2}'
    deepskyblue = f'{term.deepskyblue}'
    reset = f'{term.normal}'
    
    def color_wrap(color, text):
        return f"{color}{text}"

    colored_text = []
    current_color = deepskyblue 
    used_color = None


    for char in text:
        if char in "[]:.|-()":
            if char == '|':
                current_color = red
            else:
                current_color = dark_orchid
        elif char.isdigit():
            current_color = green
        else:
            current_color = deepskyblue
        
        if current_color == used_color:
            colored_text.append(char)
        else:
            colored_text.append(color_wrap(current_color, char))
            used_color = current_color
    colored_text.append(reset)
    return ''.join(colored_text)

#builds the printable data
def buildandprint(x, y, username, pointe, pointt, title, con, achi_total, achi_earned, achi_text, rptext, motto, rp_date_str, status):
    tx = 2*y+1
    ty = 0
    chsize = x-2*y
    rptext = highlighter(rptext)
    if motto != "":
        motto = f"{term.purple}{motto}{term.normal}"
    else:
        motto = ""
    login = f"{term.yellow2}Logged in as: {term.deepskyblue}{username}{term.normal}"
    points = f"{term.yellow2}Total points: {term.green2}{pointe} {term.darkorchid1}({term.webgreen}{pointt}{term.darkorchid1}){term.normal}"
    playing = f"{term.yellow2}Playing: {term.deepskyblue}{title}{term.normal}"
    console = f"{term.yellow2}Console: {term.deepskyblue}{con}{term.normal}"
    achi = f"{term.yellow2}Achievements: {term.green2}{achi_earned}{term.darkorchid1}/{term.green2}{achi_total} {term.darkorchid1}({achi_text}{term.darkorchid1}){term.normal}"
    details = f"{term.yellow2}Details: {rptext}{term.normal}"
    rp_status = f"{term.yellow2}RPC Status: {status}{term.normal}"
    rp_date = f"{term.yellow2}Status date: {term.deepskyblue}{rp_date_str if rp_date_str else 'N/A'}{term.normal}"

    finaltext = ''
    asd, _, ty = splitter(login, tx, ty, chsize)
    finaltext += asd
    if motto != "":
        asd, _, ty = splitter(motto, tx, ty, chsize)
        finaltext += asd
    asd, _, ty = splitter(points, tx, ty, chsize)
    finaltext += asd
    asd, _, ty = splitter(playing, tx, ty, chsize)
    finaltext += asd
    asd, _, ty = splitter(console, tx, ty, chsize)
    finaltext += asd
    asd, _, ty = splitter(achi, tx, ty, chsize)
    finaltext += asd
    asd, _, ty = splitter(details, tx, ty, chsize)
    finaltext += asd
    asd, _, ty = splitter(rp_status, tx, ty, chsize)
    finaltext += asd
    asd, _, ty = splitter(rp_date, tx, ty, chsize)
    finaltext += asd
    printer(finaltext)

#clears the texts
def cleartext(x, y):
    tx = 2*y+1
    for a in range(y-1):
        printer(f"{term.move_xy(tx, a)}{term.clear_eol()}")

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
    charset = config.get('MISC', 'charset')
    interval = config.get('MISC', 'interval')
    timeout = config.get('MISC', 'timeout')

    while True:
        clear_term()
        try:
            ch_text = ["Pixel", "Hash", "Standard", "Simple", "Custom"][int(charset) - 1]
        except ValueError:
            charset = "1"
            ch_text = "Pixel"
        print(f"\u001b[33m1. Username:\u001b[35m {username}\033[0m")
        print(f"\u001b[33m2. API Key:\u001b[35m {apikey}\033[0m")
        print(f"\u001b[33m3. Update interval:\u001b[35m {interval} seconds\033[0m")
        print(f"\u001b[33m4. Timeout: \u001b[35m{timeout}{" seconds" if int(timeout) > 0 else "\u001b[31m (disabled)"}\033[0m")
        print(f"\u001b[33m5. Charset:\u001b[35m {ch_text}\033[0m")
        print(f"\u001b[33m6. Buttons\033[0m")
        print("")
        print("\u001b[33m7. Save & Exit\033[0m")
        print("\u001b[33m8. Exit without saving\033[0m")
        print("")
        choice = input("\u001b[33m> \u001b[35m")
        print("\033[0m")
        if choice == "1":
            clear_term()
            username = input("\u001b[33mEnter your RA Username: \u001b[35m")
        elif choice == "2":
            clear_term()
            apikey = input("\u001b[33mEnter your RA Web API Key: \u001b[35m")
        elif choice == "3":
            clear_term()
            interval = input('\u001b[33mSet the update interval in seconds \u001b[31m(min. 5): \u001b[35m')
            try:
                interval = int(interval)
                if interval < 5:
                    interval = 5
            except ValueError:
                interval = 5
        elif choice == "4":
            clear_term()
            print('\u001b[33mAfter the Rich Presence message date is older than the specified number of seconds, the script stops updating Discord rich presence.\033[0m')
            print('\u001b[33mFor example, if the timeout is set to 300 (5 minutes), the script will stop updating Discord when the Rich Presence message is older than 5 minutes.\033[0m')
            print('\u001b[33mEnter 0 to disable this feature.\033[0m')
            print('\u001b[33mThe minimum value is 130 because things on RA seem to get updated every 2 minutes after you launch into a game.')
            timeout = input('\u001b[33mSet the timeout value in seconds \u001b[31m(0 to disable)\u001b[33m: \u001b[35m')
            try:
                t = int(timeout)
                if 0 < t < 130:
                    timeout = "130"
            except ValueError:
                timeout = "0"

        elif choice == "5":
            while True:
                clear_term()
                print('\u001b[33mSelect a preset of characters for drawing the image!\033[0m')
                print('\u001b[33m1. Pixel(default): \u001b[35m█  \u001b[31m(This one looks the best, imo)\033[0m')
                print('\u001b[33m2. Hash: \u001b[35m#\033[0m')
                print("""\u001b[33m3. "The Standard":\u001b[35m .-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@  \u001b[31m(idk, found on the internet, looks okay to me)\033[0m""")
                print("""\u001b[33m4. "The Simple":\u001b[35m .:-=+*#%@\033[0m""")
                print('\u001b[33m5. Custom: Write some characters into the \033[0;34mcharset.txt \u001b[33mfile. If you use multiple characters, try to arrange them from less visible to more visible, just like the other examples above.\033[0m')
                selected = input("\u001b[33mEntre the number of your selected preset:\u001b[35m")
                if selected in ("1", "2", "3", "4", "5"):
                    charset = selected
                    break

        elif choice == "6":
            while True:
                clear_term()
                print("\u001b[33mHere you can enable or disable different buttons on your profile.\033[0m")
                print("\u001b[33mOne leads to your RA profile page, the other to the page of the game you currently playing.\033[0m")
                print("\u001b[33mNote: You can't see them on your own profile, but others will do so don't panic.\033[0m")
                print("")
                print(f"\u001b[33m1. Current game button: {"\u001b[32mEnabled" if bt_gpage == "1" else "\u001b[31mDisabled"}\033[0m")
                print(f"\u001b[33m2. RA profile button: {"\u001b[32mEnabled" if bt_prof == "1" else "\u001b[31mDisabled"}\033[0m")
                print("\u001b[33m3. Back\033[0m")
                print("")
                choice = input("\u001b[33m> \u001b[35m")
                print("\033[0m")
                if choice == "1":
                    bt_gpage = switch(bt_gpage)
                elif choice == "2":
                    bt_prof = switch(bt_prof)
                elif choice == "3":
                    break

        elif choice == "7":
            config['RA']['username'] = str(username)
            config['RA']['apikey'] = str(apikey)
            config['BT']['profile'] = str(bt_prof)
            config['BT']['gamepage'] = str(bt_gpage)
            config['MISC']['charset'] = str(charset)
            config['MISC']['interval'] = str(interval)
            config['MISC']['timeout'] = str(timeout)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            clear_term()
            break
        elif choice == "8":
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
    charset_x = config.get('MISC', 'charset')
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

    global charset
    if charset_x == '1':
        charset = '█'
    elif charset_x == '2':
        charset = '#'
    elif charset_x == '3':
        charset = """ .-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"""
    elif charset_x == '4':
        charset = """ .:-=+*#%@"""
    elif charset_x == '5':
        try:
            with open('charset.txt', 'r') as file:
                charset = file.read()
                charset = charset.replace('\n', '').replace('\r', '')
        except Exception:
            charset = '█'
    else:
        charset = '█'

    image = Image.new("RGB", (5, 5), color=(0, 0, 0))
    current_game = None
    ra_userdata = None
    rpc_status = 0 #0 inactive/disconnected, 1 active, 3 error
    fp = True
    rpc_connected = False
    rpc_st_text = [f"{term.grey}Inactive", f"{term.green2}Active","", f"{term.red}Error!"]
    RPC = Presence(appid)

    start_time = None
    total_points = ""
    total_true_points = ""
    game_title = ""
    console_name = ""
    achi_max = ""
    achi_earned = ""
    achi_text = ""
    term_rpc_msg = ""
    motto = ""
    rpc_date = ""

    with term.hidden_cursor(), term.cbreak(), term.location(), term.fullscreen():
        termsize = [term.width, term.height]
        while True:
            #fetching data from RA
            no_cache = get_no_cache_string()
            ra_userdata = ra_data(f"https://retroachievements.org/API/API_GetUserSummary.php?u={username}&y={apikey}&g=0&a=0&noCache={no_cache}")
            if ra_userdata == None:
                rpc_status = 3
            else:
                total_points = ra_userdata['TotalPoints']
                total_true_points = ra_userdata['TotalTruePoints']
                motto = ra_userdata['Motto']
                rpc_date = ra_userdata.get('RichPresenceMsgDate', '')

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
                    print(f"{term.clear()}")
                    current_game = ra_userdata['LastGameID']
                    image = Image.open(io.BytesIO(requests.get(f"https://media.retroachievements.org{ra_game_data['ImageIcon']}").content))
                    pixels = resizer(image)
                    drawer(pixels, term.height)

                game_title = ra_game_data['GameTitle']
                console_name = ra_game_data['ConsoleName']
                achi_max = ra_game_prog['NumPossibleAchievements']
                term_rpc_msg = ra_userdata['RichPresenceMsg']

                if ra_game_prog['NumAchieved'] == 0:
                    achi_earned = 0
                    achi_text = f"{term.white}None"
                    rpc_achi = f"\uD83C\uDFC6 0/{ra_game_prog['NumPossibleAchievements']} (None)"
                elif ra_game_prog['NumAchievedHardcore'] < ra_game_prog['NumAchieved']:
                    achi_earned = ra_game_prog['NumAchieved']
                    achi_text = f"{term.hotpink}Softcore"
                    rpc_achi = f"\uD83C\uDFC6 {ra_game_prog['NumAchieved']}/{ra_game_prog['NumPossibleAchievements']} (Softcore)"
                else:
                    achi_earned = ra_game_prog['NumAchievedHardcore']
                    achi_text = f"{term.red}Hardcore"
                    rpc_achi = f"\uD83C\uDFC6 {ra_game_prog['NumAchievedHardcore']}/{ra_game_prog['NumPossibleAchievements']} (Hardcore)"

                cleartext(term.width, term.height)
                buildandprint(term.width, term.height, username, total_points, total_true_points, game_title,console_name, achi_max, achi_earned, achi_text, term_rpc_msg, motto, rpc_date, rpc_st_text[rpc_status])

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

            #frist print to display Error just in case
            if rpc_status in [0, 3] and fp == True:
                fp = False
                pixels = resizer(image)
                drawer(pixels, term.height)
                cleartext(term.width, term.height)
                buildandprint(term.width, term.height, username, total_points, total_true_points, game_title,console_name, achi_max, achi_earned, achi_text, term_rpc_msg, motto, rpc_date, rpc_st_text[rpc_status])

            for i in range(interval):
                if termsize != [term.width, term.height]:
                    termsize = [term.width, term.height]
                    print(f"{term.clear()}")
                    pixels = resizer(image)
                    drawer(pixels, term.height)
                    cleartext(term.width, term.height)
                    buildandprint(term.width, term.height, username, total_points, total_true_points, game_title, console_name, achi_max, achi_earned, achi_text, term_rpc_msg, motto, rpc_date, rpc_st_text[rpc_status])
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
