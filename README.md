# log_analysis_scripts
Scripts to extract parameter data from Philips MRI log files

Change the parameters "Scanner", "year_month", "day", "input root" and "output" root in main.py and run the main.py script to extract parameters 

The script saves the data in .csv files. Note that the .csv files are indexed by the year-month of the log files. If a .csv file of a specific year-month already exists, the new data are appended to the file instead of overwriting it. If the year-month does not exist, a new .csv file is created.
