# This project calls the ESPN API to display matches, score updates, and allows for the user to select favorite matchups. 

## Files Included:

* api.py - Main API file, calls on the ESPN API and handles scoreboards and team info
* db.py - client-sided database (hosted on user's machine). Handles the storage of user's favorite teams
* notify.py - Handles all alert popups
* sports.py - Dictionary that stores different sports leagues 
* worker.py - Background program that is called by main.py. Handles updating the application window and also is used to create instances of main.py
* main.py - Handles almost all functionality of the application window. Creates all buttons and widgets for the application and also handle formatting
* README.md - "readme" file. Contains all relevant information pertaining to the app.

## Functionality:
To run this program, run the "main.py" file. I would recommend using and IDE like vscode, however command line also works. To run via your CLI (Command-line interface), enter 
    "python main.py" into your terminal. 
Make sure you are in the proper directory where you downloaded the file.

### If using vscode (RECOMMENDED):
There are two easy ways to run this program. The first way is to open the main.py file with the editor. At the top right, there should be play button. Simply click this and it should compile and run.
Alternatively, you can right click the main.py file and select the option
    "Run Python File in Terminal"

Once open, you can click on the dropdown menu to change what league you want to see match ups for. Once you selected you will now be able to select your favorite match ups for the given day / week (depending on the sport). Favorite matchups are highlighted in yellow. In order to remove favorites, just click on the matchup again.

### Files Generated From Running
* logo_cache.pkl - cache of all team logos, allows for the logos to be generated significantly faster on subsequent runs.
* previous_scores.pkl - contains all previous scores, so that the user is not notified of scores/updates they have already received
* tracker.db - database storing all user favorites

### Necessary Packages
Note: This program uses PyQT5. If you do not already have this installed, make sure you do so! In order to download, you must open your terminal and run the command
    " pip install <packageName> "

All other packages should be preinstalled with python 3.13, however if you encounter any errors with packages not being detected, make sure you download them with the above method. 

## NOTE
* The logos will take some time to generate when you open the app, ESPECIALLY ON YOUR FIRST TIME RUNNING. Be patient, and eventually the logos will show up! The load time gets slightly more faster on subsequent runs of the app.
* **THIS PROGRAM USES A HIDDEN ESPN API. THIS MEANS THAT AT RANDOM THIS APP COULD STOP WORKING IF UPDATES OR CHANGES ARE MADE TO THE API!** ESPN will not disclose when these changes are being made.

## KNOWN BUGS
* Sometimes the app will not be able to display a team's logo. This happens when a logo has colors that are incompatible with the display. This error only really happens with college teams from my experience. As far as I am aware, there is no fix to this. This does not affect performance, there will just be a blank box where the logo would normally be displayed. 
