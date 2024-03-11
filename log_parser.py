import re
import log_reader as lr
import line_processor_allscanners as lp
import os
import csv
import pandas as pd
import maps as mps

class LogParser:
    # initiate all instances needed
    def __init__(self):
        # Gneral settings
        self.date = None
        self.scanner = None
        self.scan_index = 0
        self.lcc_index = 0
        self.exam_data_key = None
        self.scan_data_key = None
        self.exam_id = None

        
        # Flags
        self.start_detect_coils = False

        # Lists
        self.hum_exam_room_data = []  # humidity of the exam room
        self.hum_tech_room_data = []  # humidity of the technician room
        self.temp_exam_room_data = []  # temperature of the exam room
        self.temp_tech_room_data = []  # temperature of the technician room
        self.dps_fault_data = []  # DPS fault in minutes
        self.latched_error_data = [] # latched error status
        self.helium_avg_pressure_data = []  # helium pressure moving average
        self.cryo_malfunction_data = []  # cryo malfunction  
        self.cryo_switch_data = [] # cryo switch
        self.f0_data = []  # f0
        self.pu_data = []

        # Dictionaries
        self.stt_results_data = {}
        self.device_data = {}
        self.psu_voltage_data = {}
        self.psu_temp_data = {}
        self.stt_linkerr_data = {}
        self.magnet_daily_monitor_data = {}
        self.lcc_data = {}
        self.exam_data = {}
        self.scan_data = {}
        self.rcu_data = {}
        self.amp_power_data = {}
        self.spikes_data = {}
        self.tune_coil_data = {}
        self.channel_magnitude_data = {}
        self.noise_data = {}
        self.cf_data = {}
        self.cf_phase_diff_data = {}
        self.time_align_data = {}
        self.control_loop_data = {}

        #Sets
        self.coil_set = set()

        # Regex
        self.regex_device = re.compile('Device\s(\w+)\sadded.+SerNr:(\w+),.+:\w+,.+:\w+')
        self.regex_psu_voltage = re.compile("Device\s(.*?)\s\[.*?\]\s(\w+)?\s(\w+)\s\[V\]:\smin=\s+[-.\d]+\s*,max=\s+[-.\d]+\s*,avg=\s+([-.\d]+)")
        self.regex_psu_temp = re.compile('Device\s(.*?)\s\[.*?\]\s(\w+)_temperature.+min=\s+\d.+\s.max=\s+\d.+\s.avg=\s+(\d.+)\s,std.+')
        self.regex_linkerr = re.compile(".+Device\s+(\w+)\s+\[.+\]\s+a?t?(.+?)=\s+(\d+)\s+.+")
        self.regex_magnet = re.compile('FRUPROP.+:\s(\w+)\s=\s(.+?)\s\((.+)\)')
        self.regex_lcc_old = re.compile('LCC.+Monitor.:\s(.+):\s(\d*.?\d+?)')
        self.regex_lcc_new = re.compile('"([^"]+)"\s*:\s*"([^"]+)"')
        self.regex_spikes = re.compile('.*?REC_JDB.*?-(.*?):?\s{2,}(.+)')
        self.regex_tm = re.compile('TM:\s([T|R]Q(11|22)).+:\s+(-?\d*.?\d+)\s+kHz.+Q:\s+(-?\d*.?\d+),.+:\s+(-?\d*.?\d+).+mV')
        self.regex_channel_f0_magnitude = re.compile('F0:.mag.+channel\[\s*(\d+?)\s*\]\s*=\s+(\d*.\d+)\s*mV\s*\((\w+)\)')
        self.regex_noise = re.compile('NS:\s(\w+)\s+.+\[(.+)\]\s=\s(\d+.\d+)\suV')
        self.regex_fc = re.compile("Fine:\s(.+)_E?0*(\w*\d)_\w+?\s(.+):.+val=(-?\d+\.\d+),")
        self.regex_maxdiff = re.compile("channel\s(\w.+)_E?0*(\w+)\/(\w+)\smax\sphase\sdifference\s(\d+\.\d+)\sduring\sfull_callibration:(\w+)")
        self.regex_time_align = re.compile("TimeAlign:\s(\w+)\s+receiver\((.+)\)\s+Delay=\(measured=(-?\d*.\d+),\s?err.+")
        self.regex_control_loop = re.compile("CL:.+channel\s*(\d):\s*gain\s*=\s+(\d*.\d+),\s+phase\s*=\s*(\d*.\d+),\s*delay\s*=\s*(\d*.\d+)")

        # maps
        self.data_paths_maps = mps.generate_map('FilePath')
        self.header_maps  = mps.generate_map('Header')
        self.lcc_maps = mps.generate_map('LCC')
        self.spikes_maps = mps.generate_map('Spike')
        self.f0_maps = mps.generate_map('F0')

    # get which scanner the log file belongs to from the file pathes
    def get_scanner(self, file_path):
        if 'Alpha' in file_path or "B1-MR-02" in file_path:
            self.scanner = 'Alpha'
        elif 'Ingenia' in file_path or "Z0-MR-01" in file_path:
            self.scanner = 'Ingenia'
        elif 'Omega' in file_path or "B1-MR-01" in file_path:
            self.scanner = 'Omega'
        else:
            print('Scanner information unavailbe in the file path')
        return self.scanner

    # process file
    def process_new_file(self, file_path):
        print(f'Processing: {file_path}') # print the file path to be processed
        lines = lr.read_lines(file_path) # read the log lines of the file
        self.date = lines[1].split('\t')[1] # get the date of the log file
        self.year_month = self.date.split('-')[0] + '-' + self.date.split('-')[1] # get the year and month of the log file
        self.scanner = self.get_scanner(file_path) # get the scanner of the log file
        # skip the repeated Disk Full lines and process the rest
        for line in lines:
            if 'Disk Full' in line and 'less than' in line:
                time, text = lp.get_time_and_text(line)
                print(f'Disk Full Error at {time} of {self.date}, text: {text}')
                break
            else:
                self.parse_log_lines(line)


    def save_data_to_csv(self, output_root):
        print('Saving data to csv files')
        for data_attr, folder_name in self.data_paths_maps.items():
            if data_attr.endswith('_data'):
                data_dict = getattr(self, data_attr)
                data_dict = getattr(self, data_attr)
                folder = f'{output_root}/{self.scanner}/{folder_name}'
                if not os.path.exists(folder):
                    os.makedirs(folder)
                # create the csv files indexed by the year
                csv_file_path = f'{folder}/data_{self.year_month}.csv' # data of the same month are saved in the same csv file


                if isinstance(data_dict, dict):
                    # check if the csv path exists
                    data_list = list(data_dict.values())
                    data_df = pd.DataFrame(data_list, dtype=str)
                    # if the csv file exists, append the data to the file
                    if os.path.exists(csv_file_path):
                        data_df.to_csv(csv_file_path, mode='a', header=False, index=False, decimal='.', float_format='%.15f')
                    else:
                        data_df.to_csv(csv_file_path, index=False, decimal='.', float_format='%.15f')


                elif isinstance(data_dict, list):
                    # check if the csv path exists
                    if os.path.exists(csv_file_path):
                        with open(csv_file_path, 'a', newline='') as csv_file:
                            writer = csv.writer(csv_file)
                            writer.writerows(data_dict)
                    else:
                        with open(csv_file_path, 'w', newline='') as csv_file:
                            writer = csv.writer(csv_file)
                            writer.writerow(self.header_maps[data_attr])
                            writer.writerows(data_dict)


    def parse_log_lines(self, line):
        # some general parameters
        if 'AXOBJFE' in line and 'room' in line:  # extract exam/tech room humidity and temperature # completed
            lp._process_hum_and_temp(self, line)
        elif '(STT)' in line and 'result' in line:  # extract STT daily test results
            lp._process_stt(self, line)
        elif 'Device' in line and 'SerNr' in line:  # extract device serial number
            lp._process_device_sn(self, line)
        elif 'Latched error status' in line:
            lp._process_latched_error(self, line)
        elif 'PSUANA' in line and '[V]' in line:
            lp._process_psu_voltage(self, line)
        elif 'PSUANA' in line and '_temperature' in line:
            lp._process_psu_temperature(self, line)
        elif 'LNKERR' in line:
            lp._process_link_error(self, line)
        elif 'STT' in line and 'FRUPROP' in line:
            lp._process_magnet_daily_monitor(self, line)
        elif 'LCC' in line and 'Monitor' in line:
            lp._process_lcc(self, line)
        elif 'Cryocooler switched' in line:
            lp._process_cryo_switch(self, line)
        elif 'examOID' in line and '=' in line:
            lp._process_new_exam(self, line)
        elif 'SingleScan members' in line:
            lp._process_new_scan(self, line)
        elif 'm_Name' in line and '=' in line:
            lp._process_scan_protocol(self, line)
        elif '0 event Scan starts' in line:
            lp._process_scan_start(self, line)
        elif '0 event Scan completed' in line:
            lp._process_scan_end(self, line)
        elif 'CI: Detected' in line and '/' in line and 'args' not in line and self.start_detect_coils == True:
            lp._process_coils(self, line)
            # extract exam related data but not coil specific
        elif 'pf0_set_freq' in line:
            lp._process_f0(self, line)
        elif 'RCU:' in line:
            lp._process_rcu(self, line)
        elif 'measured FAP' in line:
            lp._process_amp_power(self, line)
        elif 'b1 values per channel'in line:
            lp._process_pu(self, line)
        elif 'REC_JDB' in line:
            lp._process_spikes(self, line)
        elif 'TM: ' in line and 'ampl:' in line:
            lp._process_tm(self, line)
        elif 'F0: magnitude' in line and 'RESP' not in line:
            lp._process_f0_mag(self, line)
        elif 'noise level' in line:
            lp._process_noise(self, line)
        elif 'CoarseFine:' in line and 'F0' in line:
            lp._process_cf_fcratio(self, line)
        elif 'CoarseFine:' in line and 'f0' in line:
            lp._process_cf_phase_diff(self, line)
        # time alignment in receive channel calibration
        elif 'TimeAlign:' in line and 'Delay=' in line:
            lp._process_time_align(self, line)
        # control loop calibration
        elif 'CL:' in line:
            lp._process_control_loop(self, line)
        else:
            pass

def get_scanner(file_path):
    if 'Alpha' in file_path:
        scanner = 'Alpha'
    elif 'Ingenia' in file_path:
        scanner = 'Ingenia'
    elif 'Omega' in file_path:
        scanner = 'Omega'
    else:
        print('Scanner not found')
    return scanner


# this function is used to get the log files to be processed based on the parameters of the scanner, year-month and day
def process_files(scanner_to_process, year_month, day, root):
    # match the name of the scanner to the name of the scanner in the log file path
    if scanner_to_process == 'Alpha':
        scanner = 'AMC-B1-MR-02'
    elif scanner_to_process == 'Ingenia':
        scanner = 'AMC-Z0-MR-01'
    elif scanner_to_process == 'Omega':
        scanner = 'AMC-B1-MR-01'
    
    # get the log files to be processed based on the parameters of the scanner, year-month and day
    log_files = []
    # get all possible years and months between the passed argument of (YYYY-MM-DD, YYYY-MM-DD) which are the start and end of the period
    directory = f'{root}/{scanner}/{year_month}/log/'

    
    if day is not None: # if the day is specified, get the log file(s) of the specified day
        # reformat the date to match the date in the log file path as "YYYYMMDD"
        date = year_month.replace('-', '') + day
        print(f'date is {date}')
        for file in os.listdir(directory):
            if file.endswith('.log') and date in file:
                log_files.append(os.path.join(directory, file))
    else: # if the day is not specified, get all the log files in the whole month
        for file in os.listdir(directory):
            if file.endswith('.log'):
                log_files.append(os.path.join(directory, file))


    return log_files

