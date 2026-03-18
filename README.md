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
	- On the website go to your profile settings, scroll down to the `Authentication` section and there you will find your Web API Key.

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
|<img width="1235" height="708" alt="3" src="https://github.com/user-attachments/assets/1c1014c1-6a88-475c-89c8-f82119519980" />|<img width="1236" height="709" alt="4" src="https://github.com/user-attachments/assets/9ffa4b36-99b1-401d-b857-b288bfdd1a98" />|![2](https://github.com/user-attachments/assets/070c4e64-f51e-481a-b7e5-c0a374b16c4e)|
|---|---|---|
|<img width="255" height="134" alt="1" src="https://github.com/user-attachments/assets/b35e2a92-dbda-4464-b99d-312997e48d95" />|<img width="309" height="477" alt="5" src="https://github.com/user-attachments/assets/cd1b6d8f-1bdd-4f3f-b0d1-0ac6393c7da0" />|<img width="276" height="411" alt="2" src="https://github.com/user-attachments/assets/fc40a07d-c160-4137-9fa7-5b92c50383c2" />|

## Docker

A Compose file example is available [here](docker-compose.yml).  The example includes the desktop
Discord client provided by [kasmweb](https://hub.docker.com/r/kasmweb/discord) which will allow you
to run a headless stack on a server without requiring a traditional desktop Discord client.

With this, you can play games on a Steam Deck or other handheld emulation device and your Discord
status will stay updated without requiring a Discord client running on that device.
