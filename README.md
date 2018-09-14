# WC3 Stats
Dashboard for warcraft 3 replays

Since Blizzard does not update the battle.net statistics for Warcraft 3 anymore I decided to create a little tool to analyse my replays.

# Features
- analyse 1on1 replays from Battle.Net ladder games (other replays will be ignored)
- statistics by race & map (win%, length, apm)
- graphs showing win% by hour, weekday and game length
- full game list

# How to use it
At the moment there are three ways to use the app:
- run it locally in a python environment
- run it locally using an .exe that I compiled
- open [wc3stats.herokuapp.com](https://wc3stats.herokuapp.com/) (this runs on a free server and I assume that it won't stay online long if too many people use it)

## Run it locally in a python environment
Follow these steps to run the app locally:
- create a python 3 environment on your system
    - i recommend a miniconda installation from [here](https://conda.io/miniconda.html)
    - after install create an environemnt with 
    ```shell
        conda create --name wc3 python pip
    ```
    - activate the enviroment (Windows)
    ```shell
        activate wc3
    ```
    - activate the enviroment (MacOS)
    ```shell
        source activate wc3
    ```
- navigate to this folder
- install all project dependencies from `requirements.txt`
    ```shell
        pip install -r requirements.txt
    ```
- run the app
    ```shell
        python run.py
    ```

## run it locally using an .exe that I compiled
Download the .zip file containing the app [here]() and unzip it. Find the `run.exe` and start it. Your browser should open with the app.