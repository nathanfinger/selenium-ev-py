# selenium-ev
This is a big mess, mostly a exploratory method to automatically upload covers on EV. 
Some os the stuff was done to learn more about python and its world.
It works through a xlsx from EV, reading every line for an 'ID' column, then using their search feature to look inside the description (any field actually) for that ID. 
Then it opens the edit page and uploads a cover from the local OS.

#### Config
- edit the file folders.txt listing the folders where the covers could be
- put the Estante virtual Acervo inside the project folder
- run selenium-ev, it will open a tkinter GUI

#### CLI
##### Usage
- You have to set a different log file and profile for each instance.
- Log files must be initialized containing the ID in the last row. 
- Please login in every profile before using in headless mode.
###### run
```shell
python3 selenium-ev.py [options]
python3 selenium-ev.py planilha1.xlsx planilha1.log profile1 browser ...
```
###### options
- example: python3 selenium-ev.py acervo_file.xlsx log_file.log profile3 browser gui
-- browser - opens browser without headless mode (to manually login)
-- gui - opens tkinter gui
-- profile___ - chrome profile (to save session). Default: profile_directory
-- acervo_file.xlsx  (.xlsx Acervo file, from EV) - Default: will search for any xlsx
-- log_file.log  (.log file, for logs) - Default: logfile.log

#### Tkinter GUI
- It shows some of the logs and the last added cover
- Actions:
-- Stop Robot
-- Start Robot from IF (DESC)
-- Start + Auto Restart every 2 hours
-- Open Browser for 2 min (to manually login)

### Cookies and Login
The driver will save the session in './chrome/profile_directory'
Once logged in in the browser, there should be no problems with authentication
So for cookie refreshing you should login manually using the same browser opened by robot

##### Advanced Cookies 
One can import the cookies using 'setCookies'
If importing EV cookies, it is advised to change the domains to 'www.estantevirtual.com.br'


## Processing logs
Running
```shell
python3 process_logs.py
```
this will process the .log files and save lists for 'capa_colocada', 'multiplos_resultados' and 'image not found'.
it also creates a new spreadsheet with the unprocessed rows/ids based on a HARD-CODED sheet taken as the original initial file 
## Known Bugs Errors
It should crash on errors. It won't restart automatically on errors. 