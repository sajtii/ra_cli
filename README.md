# Sajti's CLI for RetroAchievements Discord Rich Presence
A little software which lets you share your RetroAchievements activity with your friends on Discord.

## Requirements
- Python3 or [Docker](#docker)
- ```pip install -r requirements.txt```
	- `blessed` https://pypi.org/project/blessed/
  	- `configparser` https://pypi.org/project/configparser/
  	- `pypresence` https://pypi.org/project/pypresence/
  	- `pillow` https://pypi.org/project/pillow/
- From RetroAchievements, your username and your API key

## Features
- Detailed Rich Presence on your Discord profile (name of the game, details about what you're currently doing in the game, icons, etc.)
- Two clickable buttons (only others can see them): One leads to the RA page of the game you're currently playing; the other leads to your RA profile. You can enable or disable them using `python racli.py -s`.
- A CLI that provides some information, fetches the icon of your current game and attempts to recreate it in the terminal or command line you're using.
- Character presets for recreating the game icon, or you can create your own by editing `charset.txt`.
- A little automation feature called `timeout`. It tries to detect when you are actually playing and activates or deactivates the rich presence accordingly. It is disabled by default.

## Usage
After installing the requirements and ensuring you have all the necessary data, start by launching the setup script with `python racli.py -s` from terminal. Navigate using the corresponding numbers, provide the requested details, and you're good to go. Or, if you prefer you can manually modify config.ini, but be careful, as incorrect changes could break the code. Also, never ever modify `data.ini`.

When you have provided all your details, you can launch the script without flags by running `python racli.py`.

> [!IMPORTANT]
> The [Docker](#docker) container requires manual editing of `config.ini` because it runs non-interactively.  Alternatively you may run `python racli.py -s` manually as shown above and copy the generated `config.ini` into the Docker bind mount path in the [docker-compose.yml](docker-compose.yml) file.

## Screenshots
|![3.bmp](https://github.com/user-attachments/files/26075803/3.bmp)|![4.bmp](https://github.com/user-attachments/files/26075813/4.bmp)|![2](https://github.com/user-attachments/assets/070c4e64-f51e-481a-b7e5-c0a374b16c4e)|
|---|---|---|
|![1.bmp](https://github.com/user-attachments/files/26075856/1.bmp)|![5.bmp](https://github.com/user-attachments/files/26075862/5.bmp)|![2.bmp](https://github.com/user-attachments/files/26075866/2.bmp)|

## Docker

A Compose file example is available [here](docker-compose.yml).  The example includes the desktop
Discord client provided by [kasmweb](https://hub.docker.com/r/kasmweb/discord) which will allow you
to run a headless stack on a server without requiring a traditional desktop Discord client.

With this, you can play games on a Steam Deck or other handheld emulation device and your Discord
status will stay updated without requiring a Discord client running on that device.
