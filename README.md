# WC3 Stats
Dashboard for warcraft 3 replays

Since Blizzard does not update the battle.net statistics for Warcraft 3 anymore I decided to create a little tool to analyse my replays.

# Features
- analyse 1on1 replays from Battle.Net ladder games (other replays will be ignored)
![Overall stats by race](/screenshots/20180914_Total.png?raw=true)
- statistics by race & map (win%, length, apm)
![Stats by enemy race](/screenshots/20180914_EnemyRace.png?raw=true)
![Stats by map](/screenshots/20180914_Map.png?raw=true)
- graphs showing win% by hour, weekday and game length
- full game list
![Full Game List](/screenshots/20180914_List.png?raw=true)

# Issues and feature request
Please use the issues of this github repo to send any feedback and suggestions my way. Also if you want to help improving the app please reach out. I am working full time and therefor I don't have much time to update the app.

# How to use it
At the moment there are three ways to use the app:
- run it locally using an .exe that I compiled
- open [wc3stats.herokuapp.com](https://wc3stats.herokuapp.com/) (this runs on a free server and I assume that it won't stay online long if too many people use it)
- run it locally in a python environment (if you are experienced with Python, Flask & co.)

## run it locally using an .exe that I compiled
Download the .zip file containing the app [here]() and unzip it. Find the `run.exe` and start it. Your browser should open with the app.

## Online version at [wc3stats.herokuapp.com](https://wc3stats.herokuapp.com/)
I am running it as a free app there. If there is demand to put it on a stronger server please reach out to me. Maybe there are some dev ops guys who can help me. You can also donate to https://www.paypal.me/hendrikhilleckes. 

## Run it locally in a python environment
Follow these steps to run the app locally:
- create a python 3 environment on your system
    - i recommend a miniconda installation from [here](https://conda.io/miniconda.html)
    - after install create an environment with 
    ```shell
        conda create --name wc3 python pip
    ```
    - activate the environment (Windows CMD)
    ```shell
        activate wc3
    ```
    - activate the environment (Unix Shells, MacOS,...)
    ```shell
        source activate wc3
    ```
- navigate to this folder
- install all project dependencies from `requirements.txt`
    ```shell
        pip install -r requirements.txt
    ```
- create the file `.env` just as described in `.env.example`
    - you need to register on [plot.ly](https://plot.ly) to get a username and api key
- run the app
    ```shell
        python run.py
    ```