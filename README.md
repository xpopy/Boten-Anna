# Boten-Anna
A discord bot written in python


# Installation (Windows)
1. Install python 3.8.1: Go to https://www.python.org/downloads/release/python-381/ and download "Windows x86-64 executable installer"

   1. Make sure you include PIP in the installation, and to tick the "Add Python to environment variables" option

2. Download the bot, either as a zip (unzip it where you want it) or clone it

3. Install Pipenv:
    
    1. Open up a command prompt or powershell in the new folder (shift rightclick the folder > open powershell window here)

    2. `pip install pipenv`: Installs pipenv, a python environment which keeps all the dependencies separate from the system python install

    3. `pipenv install`: Install all dependencies needed for the bot to run. 
    
    4. After it's done installing you can close the window

4. Install ffmpeg:

    1. Go to https://ffmpeg.zeranoe.com/builds/, select "Windows 64-bit" then click on Download Build

    2. Create a folder in `C:` like this `C:/ffmpeg` and extract the content of the zip file so it looks like this:
    ```
    C:/ffmpeg/presets
    C:/ffmpeg/doc
    C:/ffmpeg/bin
    C:/ffmpeg/README.txt
    C:/ffmpeg/LICENSE.txt
    ```

    3. Now add `C:/ffmpeg/bin` to the PATH:

        1. Open the Environment Variables window:
    
        2. press `Win + R` and paste in `rundll32.exe sysdm.cpl,EditEnvironmentVariables` and hit ok
  
        3. In `User variables for {username}` double click on `Path`.

        4. In the new window, click on `New` and type in `C:\ffmpeg\bin\` and hit enter, now hit `OK` on the open windows

5. Bot tokens:

    1. In /settings/config.json, edit the "INSERT DISCORD TOKEN" with your own discord token (https://discordapp.com/developers/applications/, create application and get the bot token on the "Bot" tab)

    2. In /settings/config.json, edit the "INSERT TENOR API KEY" with your tenor api key, which you can get from https://tenor.com/gifapi/documentation, create an account, create a new application in https://tenor.com/developer/keyregistration and copy the key


# Running
1. Open up a terminal in the installation folder and type `pipenv run python "Boten Anna.py"`
2. Alternatively you can create a file called "Run.bat" and inside of it you paste:
```
pipenv run python "Boten Anna.py"
pause
```

# Inviting
1. In order to invite your new bot to your own discord server, open up https://discordapp.com/developers/applications, select your bot, go to the OAuth2 tab, hit the "Bot" checkmarker and down below select the permissions:
  ```
  Send Messages
  Manage Messages
  Embed Links
  Read Message History
  Use External Emojis
  Add Reactions
  Connect
  Speak
  ```

2. Then right above the permissions there's a long link, click on the copy button and paste it in your browser, voila!
   You might want to save that link as that's the only way you can invite your bot to other servers (or you'll have to make a new link every time)

