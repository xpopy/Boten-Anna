# Boten-Anna
A discord bot written in python


# Installation
* install python 3.8.1: https://www.python.org/downloads/release/python-381/

* Make sure you include PIP in the installation, and to tick the "Add Python to environment variables" option

* Download the bot, either as a zip (unzip it where you want it) or clone it

* Open up a command prompt or powershell in the new folder (shift rightclick the folder > open powershell window here)

* `pip install pipenv`: Installs pipenv, a python environment which keeps all the dependencies which is good if you have multiple python projects

* `pipenv shell`: Opens a new python environment

* `pipenv install`: Install all dependencies

* In /settings/config.json, edit the "INSERT DISCORD TOKEN" with your own discord token (https://discordapp.com/developers/applications/, create application and get the bot token on the "Bot" tab)

* In /settings/config.json, edit the "INSERT TENOR API KEY" with your tenor api key, which you can get from https://tenor.com/gifapi/documentation, create an account, create a new application in https://tenor.com/developer/keyregistration and copy the key
* to get the tenor api key, create a new account on tenor developer page, log in and create a new application



# Running

* Open up a terminal in the installation folder and type `pipenv run python "Boten Anna.py"`
* Alternatively you can create a file called "Run.bat" and inside of it you paste:
```
pipenv run python index.py
pause
```
