# selenium-ev

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
--  python3 selenium-ev.py [options]
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


## Known Bugs Errors
It shouldn't crash on errors. It won't restart automatically on errors. 