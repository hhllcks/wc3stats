# WC3 Stats
Dashboard for Warcraft 3 replays

Since Blizzard does not update the battle.net statistics for Warcraft 3 anymore I decided to create a little tool to analyse my replays. Please acknowledge that this is a little side project and not a fully supported tool. Blizzard also has nothing to do with it so don't blame them if something goes wrong.

# Usage
Type in your player name and select the replays. The stats will appear automatically. Please be patient if you are parsing a lot of replays (> 100).

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

If you are getting errors or some stats seem to be wrong please provide the smallest possible sample of replays where the error occurs. This will help fixing it.

## Known Issues
- the loading indicator appears after the file upload is done and just indicates that the statistics are getting calculated. So for some time you will think that nothing is happening. That is due to the dash framework I am using. I am already thinking about using pure Flask.
- it takes a long time to compute the stats (for my ~250 replays it is usually around 2 minutes). Please have in mind that the app has to parse every single replay!
- the size and position of the graphs is not ideal
- position of the loading indicator is off

# Thanks
Thanks to [scopatz](https://github.com/scopatz) for creating [a python module to read Warcraft 3 replays](https://github.com/scopatz/w3g).

Thanks to Blizzard for creating the greatest game of all time.

# How to use it
At the moment there are three ways to use the app:
- run it locally using a compiled executable
- open [wc3stats.herokuapp.com](https://wc3stats.herokuapp.com/) (this runs on a free server and I assume that it won't stay online long if too many people use it)
- run it locally in a python environment (if you are experienced with Python, Flask & co.)

## Run it locally using a compiled executable
Windows:
Download the .zip file containing the app and unzip it. Find the `run.exe` and start it. Your browser should open with the app.
[Download](run-windows.zip?raw=true) (Tested on Windows 7 64-bit)

Mac: 
Download the .zip file containing the app and unzip it. Open the terminal and navigate into the folder 'run'. Type:
```shell
    ./run
```
[Download](run-mac.zip?raw=true) (Tested on macOS High Sierra 10.13.6)

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