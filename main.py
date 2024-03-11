import log_parser as logpar
from log_parser import LogParser
import time

# manually specify the scanner and which month you want to extract the log data from
scanner = "Ingenia" #"Ingenia" or "Alpha" or "Omega"
year_month = '2021-10' # use format of "YYYY-MM" for the whole month; 
day = None # use "None" if you want to extract the whole month; replace with "DD" for specific date for example "15" as the 15th of the month
input_root = '/home/zhangj/lood_storage/divi/Ima/parrec/!logfiles' # !!!CHANGE THIS ROOT OF INPUT FILES AS IN YOUR COMPUTER!!! with the last folder as the !logfiles folder of the scanner
output_root = '/home/zhangj/lood_storage/Personal Archive/Z/zhangj/log_scripts_jiaxu/' # !!! change the root folder of the outout data files as in your computer, the data will be saved as "output_root/scanner/parameter_category/data_year.csv"

if __name__ == '__main__':
    # get time elapsed
    start_time = time.time()

    # get the list of all files to be processed based on specified parameters
    log_files_to_process = logpar.process_files(scanner_to_process = scanner, year_month = year_month, day = day, root = input_root)

    # initiate the log parser class
    LOPA = LogParser()

    # use the following codes to save the data of multiple processed files in a single csv file
    for file in log_files_to_process:
        LOPA.process_new_file(file)

    # save the data of multiple processed files in a single csv file
    LOPA.save_data_to_csv(output_root)

    end_time = time.time()
    print(f'Elapsed time: {end_time - start_time}')
