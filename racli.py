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
from datetime import datetime, timezone
from pypresence import Presence
from pypresence.types import ActivityType
from pypresence.types import StatusDisplayType

term = Terminal()



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
    
    #trying to measure the real lenght of the printable text by removing ansi escape and replacing emojis with ee
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
def buildandprint(x, y, username, pointe, pointt, title, con, achi_total, achi_earned, achi_text, rptext, motto, rp_date_str):
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
    status = f"{term.yellow2}Status: {rptext}{term.normal}"
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
    asd, _, ty = splitter(status, tx, ty, chsize)
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
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def set_buttons():
    config = configparser.ConfigParser()
    config.read('config.ini')
    def select1():
        button = input('\u001b[33mWould you like to enable the current game button on your Discord profile while playing?\u001b[31m(y/n): \u001b[35m')
        if button in ['y','Y','yes','Yes']:
            print('\u001b[33mCurrent game button enabled!\033[0m')
            config['BT']['gamepage'] = '1'
        elif button in ['n','N','no','No']:
            print('\u001b[33mCurrent game button disabled!\033[0m')
            config['BT']['gamepage'] = '0'
        else:
            print('\u001b[31mError! Yes or No!\033[0m')
            select1()
            
    def select2():
        button = input('\u001b[33mWould you like to enable the RA profile button on your Discord profile while playing?\u001b[31m(y/n): \u001b[35m')
        if button in ['y','Y','yes','Yes']:
            print('\u001b[33mRA profile button enabled!\033[0m')
            config['BT']['profile'] = '1'
        elif button in ['n','N','no','No']:
            print('\u001b[33mRA profile button disabled!\033[0m')
            config['BT']['profile'] = '0'
        else:
            print('\u001b[31mError! Yes or No!\033[0m')
            select2()
    select1()
    select2()
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
            
def set_interval():
    config = configparser.ConfigParser()
    config.read('config.ini')
    interval = input('\u001b[33mSet the update interval in seconds \u001b[31m(min. 20): \u001b[35m')
    try:
        interval = int(interval)
        if interval < 20:
            interval = 20
    except ValueError:
        interval = 20
    config['MISC']['interval'] = str(interval)
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    print(f'\u001b[33mUpdate interval succesfully set to \u001b[35m{interval} \033[0;33mseconds.\033[0m')
    
def set_timeout():
    config = configparser.ConfigParser()
    config.read('config.ini')
    print('\u001b[33mAfter the Rich Presence message date is older than the specified number of seconds, the script stops updating Discord rich presence.')
    print('\u001b[33mFor example, if the timeout is set to 300 (5 minutes), the script will stop updating Discord when the Rich Presence message is older than 5 minutes.')
    print('\u001b[33mEnter 0 to disable this feature.')
    timeout = input('\u001b[33mSet the timeout value in seconds \u001b[31m(0 to disable)\u001b[33m: \u001b[35m')
    try:
        timeout = int(timeout)
    except ValueError:
        timeout = 0
    config['MISC']['timeout'] = str(timeout)
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    print(f"\u001b[33mTimeout value successfully set to \u001b[35m{timeout} \033[0;33mseconds.\033[0m")
    
def set_charset():
    config = configparser.ConfigParser()
    config.read('config.ini')
    print('\u001b[33mSelect a preset of characters for drawing the image!\033[0m')
    print('\u001b[33m1. Pixel(default): \u001b[35m█  \u001b[31m(This one looks the best, imo)\033[0m')
    print('\u001b[33m2. Hash: \u001b[35m#\033[0m')
    print("""\u001b[33m3. "The Standard":\u001b[35m .-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@  \u001b[31m(idk, found on the internet, looks okay to me)\033[0m""")
    print("""\u001b[33m4. "The Simple":\u001b[35m .:-=+*#%@\033[0m""")
    print('\u001b[33m5. Custom: Write some characters into the \033[0;34mcharset.txt \u001b[33mfile. If you use multiple characters, try to arrange them from less visible to more visible, just like the other examples above.\033[0m')
    def decide():
        selected = input("\u001b[33mEntre the number of your selected preset:\u001b[35m")
        try:
            selected = int(selected)
        except ValueError:
            pass
        if selected in (1, 2, 3, 4, 5):
            config['MISC']['charset'] = str(selected)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            print('\033[0m')
        else:
            print('\u001b[33mPlease select a correct number from the options above.\033[0m')
            decide()
    decide()
    
def setup():
    config = configparser.ConfigParser()
    config.read('config.ini')    
    username = input("\u001b[33mEnter your RA Username: \u001b[35m")
    apikey = input("\u001b[33mEnter your RA Web API Key: \u001b[35m")
    appid = input("\u001b[33mEnter your Discord App ID: \u001b[35m")
    config['RA']['username'] = str(username)
    config['RA']['apikey'] = str(apikey)
    config['DC']['appid'] = str(appid)
    with open('config.ini', 'w') as configfile:
                config.write(configfile)
    print('\u001b[33mYour details have been successfully updated!\033[0m')
    
def main():
    #loading config values
    config = configparser.ConfigParser()
    config.read('config.ini')
    data = configparser.ConfigParser()
    data.read('data.ini')
    username = config.get('RA', 'username')
    apikey = config.get('RA', 'apikey')
    appid = config.get('DC', 'appid')
    interval = int(config.get('MISC', 'interval'))
    charset_x = config.get('MISC', 'charset')
    timeout = int(config.get('MISC', 'timeout'))
    
    #loading other values
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
   
    try:
        interval = int(config.get('MISC', 'interval'))
        if interval < 20:
            interval = 20
            config['MISC']['interval'] = '20'
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
    except ValueError:
        interval = 20
        config['MISC']['interval'] = '20'
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            
       
    start_time = int(time.time())
    current_game = None
    ra_userdata = None
    rpc_connected = True
    
    RPC = Presence(appid)
    RPC.connect()
    with term.hidden_cursor(), term.cbreak(), term.location(), term.fullscreen():
        termsize = [term.width, term.height]
        while True:
            while True:
                no_cache = get_no_cache_string()
                ra_userdata = ra_data(f"https://retroachievements.org/API/API_GetUserSummary.php?u={username}&y={apikey}&g=0&a=0&noCache={no_cache}")
                if ra_userdata == None:
                    break
                
                # Check timeout based on RichPresenceMsgDate
                if timeout != 0 and rpc_connected:
                    try:
                        rp_date_str = ra_userdata.get("RichPresenceMsgDate")
                        if rp_date_str:
                            # Parse API date as UTC (API returns UTC times)
                            rp_date = datetime.strptime(rp_date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                            current_date = datetime.now(timezone.utc)
                            time_diff = (current_date - rp_date).total_seconds()
                            if time_diff > timeout:
                                RPC.close()
                                rpc_connected = False
                    except (ValueError, KeyError, TypeError):
                        # If parsing fails, continue normally
                        pass
                
                    
                ra_game_data = ra_data(f"https://retroachievements.org/API/API_GetGame.php?z={username}&y={apikey}&i={ra_userdata['LastGameID']}")
                if ra_game_data == None:
                    break
                ra_game_prog = ra_data(f"https://retroachievements.org/API/API_GetUserProgress.php?y={apikey}&u={username}&i={ra_userdata['LastGameID']}")
                if ra_game_prog == None:
                    break
                ra_game_prog = ra_game_prog.get(f"{ra_userdata['LastGameID']}", {})
            
            
                if current_game != ra_userdata['LastGameID']:
                    if config.get('BT', 'gamepage') == '1':
                        button1 = {"label": "View on RetroAchievements", "url": f"https://retroachievements.org/game/{ra_userdata['LastGameID']}"}
                    else:
                        button1 = None
                    if config.get('BT', 'profile') == '1':    
                        button2 = {"label": f"{username}'s RA Page", "url": f"https://retroachievements.org/user/{username}"}  
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
                    start_time = int(time.time())
                
            
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
                cleartext(term.width,term.height)
                buildandprint(term.width, term.height, username, ra_userdata['TotalPoints'],ra_userdata['TotalTruePoints'], ra_game_data['GameTitle'], ra_game_data['ConsoleName'],ra_game_prog['NumPossibleAchievements'], achi_earned, achi_text, ra_userdata['RichPresenceMsg'], ra_userdata['Motto'], ra_userdata.get('RichPresenceMsgDate', ''))
            
                if rpc_connected:
                    RPC.update(
                        activity_type=ActivityType.PLAYING,
                        status_display_type=StatusDisplayType.NAME,
                        name= ra_game_data['GameTitle'],
                        details= trimmer(ra_userdata["RichPresenceMsg"]),
                        state= rpc_achi,
                        start=start_time,
                        large_image=f"https://media.retroachievements.org{ra_game_data['ImageIcon']}",
                        large_text=rpc_achi,
                        small_image=data.get('CI', str(ra_game_data['ConsoleID'])),
                        small_text=ra_game_data['ConsoleName'],
                        buttons=buttons_filtered
                    )
                for i in range(interval):
                    if termsize != [term.width, term.height]:
                        termsize = [term.width, term.height]
                        print(f"{term.clear()}")
                        pixels = resizer(image)
                        drawer(pixels, term.height)
                        buildandprint(term.width, term.height, username, ra_userdata['TotalPoints'],ra_userdata['TotalTruePoints'], ra_game_data['GameTitle'], ra_game_data['ConsoleName'],ra_game_prog['NumPossibleAchievements'],     achi_earned, achi_text, ra_userdata['RichPresenceMsg'], ra_userdata['Motto'], ra_userdata.get('RichPresenceMsgDate', ''))
                    time.sleep(1)
                
                # Break to outer loop if RPC is disconnected (timeout detected)
                if not rpc_connected:
                    break
        
            
            if timeout != 0 and not rpc_connected:
                while True:
                    for i in range(interval):
                        if termsize != [term.width, term.height]:
                            termsize = [term.width, term.height]
                            print(f"{term.clear()}")
                            pixels = resizer(image)
                            drawer(pixels, term.height)
                            buildandprint(term.width, term.height, username, ra_userdata['TotalPoints'],ra_userdata['TotalTruePoints'], ra_game_data['GameTitle'], ra_game_data['ConsoleName'],ra_game_prog['NumPossibleAchievements'],     achi_earned, achi_text, ra_userdata['RichPresenceMsg'], ra_userdata['Motto'], ra_userdata.get('RichPresenceMsgDate', ''))
                        time.sleep(1)
                    no_cache = get_no_cache_string()
                    ra_userdata = ra_data(f"https://retroachievements.org/API/API_GetUserSummary.php?u={username}&y={apikey}&g=0&a=0&noCache={no_cache}")
                    if ra_userdata == None:
                        break
                    # Check if RichPresenceMsgDate is fresh again
                    try:
                        rp_date_str = ra_userdata.get("RichPresenceMsgDate")
                        if rp_date_str:
                            # Parse API date as UTC (API returns UTC times)
                            rp_date = datetime.strptime(rp_date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                            current_date = datetime.now(timezone.utc)
                            time_diff = (current_date - rp_date).total_seconds()
                            if time_diff <= timeout:
                                # Rich Presence is fresh again, reconnect RPC
                                RPC.connect()
                                rpc_connected = True
                                start_time = int(time.time())
                                break
                    except (ValueError, KeyError, TypeError):
                        # If parsing fails, continue waiting
                        pass
            else:
                break
                       
    print("Something went wrong! Run the setup script (python racli.py -s) and make sure your details are correct.")
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--setup', action='store_true', help="run setup script")
    parser.add_argument('-c', '--charset', action='store_true', help="select charset presets or set it to custom")
    parser.add_argument('-i', '--interval', action='store_true', help="set update interval")
    parser.add_argument('-t', '--timeout', action='store_true', help="set timeout value")
    parser.add_argument('-b', '--buttons', action='store_true', help="enable or disable buttons on your discord profile")
    args = parser.parse_args()
    if args.setup:
        setup()
    elif args.charset:
        set_charset()
    elif args.interval:
        set_interval()
    elif args.timeout:
        set_timeout()
    elif args.buttons:
        set_buttons()
    else:
        main()
