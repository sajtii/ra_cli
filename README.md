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
- From Discord, an app ID.

You will need to create an app on the Discord Developer Portal (https://discord.com/developers/applications/). Give it a nice, unique name, which will appear below your name as your 'Playing' status. Don't worry if you make a mistake; you can modify the app's name at any time. From there, you will need your app's ID.

## Features
- Detailed Rich Presence on your Discord profile (name of the game, details about what you're currently doing in the game, icons, etc.)
- Two clickable buttons (only others can see them): One leads to the RA page of the game you're currently playing; the other leads to your RA profile. You can enable or disable them using `python racli.py -b`.
- A CLI that provides some information, fetches the icon of your current game and attempts to recreate it in the terminal or command line you're using.
- Character presets for recreating the game icon, or you can create your own by editing `charset.txt`.
- A little automation feature called `timeout`. It tries to detect when you are actually playing and activates or deactivates the rich presence accordingly. It is disabled by default.

## Usage
After installing the requirements and ensuring you have all the necessary data, start by launching the setup script with `python racli.py -s` from terminal. Provide the requested details, and you're good to go. Or, if you prefer you can manually modify config.ini, but be careful, as incorrect changes could break the code. Also, never ever modify `data.ini`.

When you have provided all your details, you can launch the script without flags by running `python racli.py`.

> [!IMPORTANT]
> The [Docker](#docker) container requires manual editing of `config.ini` because it runs non-interactively.  Alternatively you may run `python racli.py -s` manually as shown above and copy the generated `config.ini` into the Docker bind mount path in the [docker-compose.yml](docker-compose.yml) file.


Flag descriptions:
-	`-h`, `--help`      show this help message and exit
-	`-s`, `--setup`     run setup script
-	`-c`, `--charset`   select charset presets or set it to custom
-	`-i`, `--interval`  set the update interval
-	`-t`, `--timeout`   set the timeout value
-	`-b`, `--buttons`   enable or disable buttons on your discord profile


## Screenshots
|![1](https://github.com/user-attachments/assets/c3901bf9-d3b9-4a13-bbac-b685276c308f)|![2](https://github.com/user-attachments/assets/070c4e64-f51e-481a-b7e5-c0a374b16c4e)|![3](https://github.com/user-attachments/assets/a5796b21-14df-4b30-974e-9a81d109ba94)|
|---|---|---|
|![6](https://github.com/user-attachments/assets/66979836-6189-4ddc-9fe7-26f1b235ed93)|![4](https://github.com/user-attachments/assets/c128ca7c-c9f8-4bbf-bf03-1ae02e296b07)|![5](https://github.com/user-attachments/assets/a6dc4142-f0de-49ac-89ab-63298cd17853)|
|![7](https://github.com/user-attachments/assets/8e004e63-2563-48e5-9bfd-04358351e60f)|     |     |

## Docker

A Compose file example is available [here](docker-compose.yml).  The example includes the desktop
Discord client provided by [kasmweb](https://hub.docker.com/r/kasmweb/discord) which will allow you
to run a headless stack on a server without requiring a traditional desktop Discord client.

With this, you can play games on a Steam Deck or other handheld emulation device and your Discord
status will stay updated without requiring a Discord client running on that device.