import re

# returns the time and text of a log line
def get_time_and_text(line):
    return line.strip().split('\t')[2], line.strip().split('\t')[-1]

# extract humidity and temperature
# lp = the log parser class
def _process_hum_and_temp(lp, line):
    time, text = get_time_and_text(line)
    if ':' in text:
        hum_or_temp_value = text.split(':')[2].strip()
        
        if 'exam' in text:
            if 'Humidity' in text:
                entry = (lp.date, time, hum_or_temp_value)
                lp.hum_exam_room_data.append(entry)
            elif 'Temperature' in text:
                entry = (lp.date, time, hum_or_temp_value)
                lp.temp_exam_room_data.append(entry)
        elif 'tech' in text:
            if 'Humidity' in text:
                entry = (lp.date, time, hum_or_temp_value)
                lp.hum_tech_room_data.append(entry)
            elif 'Temperature' in text:
                entry = (lp.date, time, hum_or_temp_value)
                lp.temp_tech_room_data.append(entry)
    else:
        print(f'split char not in {time}: {line}')

# extract dps fault in minutes
def _process_dps_fault(lp, line):
    time, text = get_time_and_text(line)
    if '=' in text:
        dps_fault = text.split('=')[1].strip()
        lp.dps_fault_data.append((lp.date, time, dps_fault))
    else:
        print(f'split char not in {time}: {line}')

# extract stt daily test results
# 0 = Passed and 1 = Failed
def _process_stt(lp, line):
    time, text = get_time_and_text(line)
    if 'result:' not in text or '\'' not in text:
        print(f'split char in {time}: {line}')
    else:
        test = text.split('\'')[1].strip()
        result = text.split('result:')[1].split(')')[0].strip()
        key = (lp.date, test)
        if key not in lp.stt_results_data:
            lp.stt_results_data[key] = {
                'Date': lp.date,
                'Time': time
            }
        lp.stt_results_data[key]['Test'] = test
        lp.stt_results_data[key]['Result'] = 0 if result == 'Passed' else 1

# get the name and serial number of deviced connected to the scanner each day
def _process_device_sn(lp, line):
    time, text = get_time_and_text(line)
    matches = re.findall(lp.regex_device, text)
    for device_name, sn in matches:
        key = (lp.date, device_name, sn, lp.scanner)
        if key not in lp.device_data:
            lp.device_data[key] = {
                'Date': lp.date,
                'Device': device_name,
                'SerNr': sn,
                'Scanner': lp.scanner
            }
        else:
            pass


def _process_latched_error(lopa, line):
    time, text = get_time_and_text(line)
    if ':' not in text:
        print(f'split char not in {time}: {line}')
    else:
        latched_errors = text.split(':')[1].strip()
        if len(latched_errors) >= 4:
            data = (lopa.date, time, latched_errors[0], latched_errors[1], latched_errors[2], latched_errors[3])
            #append latched errors to latched_error_data list
            lopa.latched_error_data.append(data)

def _process_psu_voltage(lopa, line):
    time, text = get_time_and_text(line)
    matches = re.findall(lopa.regex_psu_voltage, text)
    for match in matches:
        device = match[0] + " " + match[1]
        voltage_type = match[2]
        avg_voltage = match[3]
        key = (lopa.date, device)
        if key not in lopa.psu_voltage_data:
            lopa.psu_voltage_data[key] = {
                'Date': lopa.date,
                'Time': time,
                'Device': device,
            }
        lopa.psu_voltage_data[key][f'{voltage_type} Average [V]'] = avg_voltage

def _process_psu_temperature(lopa, line):
    time, text = get_time_and_text(line)
    matches = re.findall(lopa.regex_psu_temp, text)
    for match in matches:
        device = match[0] + " " + match[1]
        avg_temp = match[2]
        key = (lopa.date, device)
        if key not in lopa.psu_temp_data:
            lopa.psu_temp_data[key] = {
                'Date': lopa.date,
                'Time': time,
                'Device': device,
            }
        lopa.psu_temp_data[key]['Device Temperature Average [C]'] = avg_temp

def _process_link_error(lopa, line):
    time, text = get_time_and_text(line)
    matches = re.findall(lopa.regex_linkerr, text)
    for match in matches:
        device = match[0].strip() + " " + match[1].strip()
        key = (lopa.date, device)
        if key not in lopa.stt_linkerr_data:
            lopa.stt_linkerr_data[key] = {
                'Date': lopa.date,
                'Time': time,
                'Device': device,
            }
        link_error = match[2].strip()
        lopa.stt_linkerr_data[key]['Link Error'] = link_error

def _process_magnet_daily_monitor(lopa, line):
    time, text = get_time_and_text(line)
    matches = re.findall(lopa.regex_magnet, text)

    for parameter_name, value, description in matches:
        if parameter_name == 'pressure_avg':
            lopa.helium_avg_pressure_data.append((lopa.date, time, value))
        elif parameter_name == 'time_status':
            lopa.cryo_malfunction_data.append((lopa.date, time, value))
        else:
            parameter_key = (lopa.date, 'Magnet')
            if parameter_key not in lopa.magnet_daily_monitor_data:
                lopa.magnet_daily_monitor_data[parameter_key] = {
                    'Date': lopa.date,
                    'Time': time
                }
            lopa.magnet_daily_monitor_data[parameter_key][f'{description}'] = value

def _process_lcc(lopa, line):
    time, text = get_time_and_text(line)
    matches_new = re.findall(lopa.regex_lcc_new, text)
    matches_old = re.findall(lopa.regex_lcc_old, text)
    if 'Valve' in text and 'Position' in text:
        if lopa.scanner == 'Omega' or lopa.scanner == 'Ingenia':
            if 'GradCoil' in text:
                lopa.lcc_index += 1
        elif lopa.scanner == 'Alpha':
            lopa.lcc_index += 1
    if lopa.lcc_index > 0:
        key = (lopa.date, lopa.lcc_index)
        if key not in lopa.lcc_data:
            lopa.lcc_data[key] = {
                'Date': lopa.date,
                'Time': time
            }
        for match in matches_new:
            if 'LCC' in match[1] or 'Mode' in match[0]:
                continue
            else:
                if match[0] in lopa.lcc_maps:
                    mapped_name = lopa.lcc_maps[match[0]]
                else:
                    mapped_name = match[0]
                    print(f'{match[0]} not in lcc_maps for {lopa.scanner} at {time}, {lopa.date}')
                lopa.lcc_data[key][mapped_name] = match[1]
        for match in matches_old:
            if 'LCC' in match[1] or 'Mode' in match[0]:
                continue
            else:
                lopa.lcc_data[key][match[0]] = match[1]
    

def _process_cryo_switch(lopa, line):
    time, text = get_time_and_text(line)
    if 'switched on' in text:
        data = (lopa.date, time, 0)
        lopa.cryo_switch_data.append(data)
    elif 'switched off' in text:
        data = (lopa.date, time, 1)
        lopa.cryo_switch_data.append(data)

def _process_new_exam(lopa, line):
    time, text = get_time_and_text(line)
    if '[' not in text and ']' not in text:
        print(f'split char not in {time}: {line}')
    else:
        lopa.exam_id = text.split('[')[1].split(']')[0]

        lopa.exam_data_key = (lopa.date, time, lopa.exam_id)
        if lopa.exam_data_key and lopa.exam_data_key not in lopa.exam_data:
            lopa.exam_data[lopa.exam_data_key] = {
                'Date': lopa.date,
                'Exam ID': lopa.exam_id,
                'Exam start time': time,
                'Started Scans': 0,
                'Completed Scans': 0
            }
        else:
            print(f'exam {lopa.exam_data_key} already exists')
        # reset coil set when a new exam begins
        lopa.coil_set = set()
        lopa.start_detect_coils = True

def _process_new_scan(lopa, line):
    lopa.scan_index += 1
    lopa.scan_data_key = (lopa.date, lopa.exam_id, lopa.scan_index)
    if lopa.scan_data_key not in lopa.scan_data:
        lopa.scan_data[lopa.scan_data_key] = {
            'Date': lopa.date,
            'Exam ID': lopa.exam_id,
            'Scan Index': lopa.scan_index,
            'Start Time': None,
            'End Time': None,
            'Protocol': None
        }
        

def _process_scan_protocol(lopa, line):
    time, text = get_time_and_text(line)
    if lopa.scan_data_key and '=' in text:
        lopa.scan_data[lopa.scan_data_key]['Protocol'] = text.split('=')[1].strip()

def _process_scan_start(lopa, line):
    time, text = get_time_and_text(line)
    if lopa.exam_data_key:
        lopa.exam_data[lopa.exam_data_key]['Started Scans'] += 1
    if lopa.scan_data_key:
        lopa.scan_data[lopa.scan_data_key]['Start Time'] = time

def _process_scan_end(lopa, line):
    time, text = get_time_and_text(line)
    if lopa.exam_data_key:
        lopa.exam_data[lopa.exam_data_key]['Completed Scans'] += 1
    if lopa.scan_data_key:
        lopa.scan_data[lopa.scan_data_key]['End Time'] = time

def _process_coils(lopa, line):
    time, text = get_time_and_text(line)
    coil = text.split('Detected:')[1].split('/')[0].strip()
    if coil not in lopa.coil_set:
        lopa.coil_set.add(coil)
        if '"' in coil:
            print(time, text)
        lopa.exam_data[lopa.exam_data_key][f'Coil {coil}'] = 1
    else:
        lopa.start_detect_coils = False

def _process_f0(lopa, line):
    time, text = get_time_and_text(line)
    if ':' not in line:
        print(f'split char not in {time}: {line}')
    else:
        f0 = text.split(':')[2].strip()
        data = (lopa.date, time, lopa.exam_id, f0)
        lopa.f0_data.append(data)

def _process_rcu(lopa, line):#RF circulator check
    time, text = get_time_and_text(line)
    key = (lopa.date, lopa.exam_id, lopa.scan_index)
    if 'forw power phase' in line and 'deg' in text:
        if key not in lopa.rcu_data:
            lopa.rcu_data[key] = {
                'Date': lopa.date,
                'Time': time,
                'Exam ID': lopa.exam_id
            }
        channel = line.split('[')[1].split(']')[0].strip()
        phase = line.split('deg')[0].split('=')[1].strip()
        lopa.rcu_data[key][f'FWD phase TX{channel} (deg)'] = phase

    elif 'forw power' in line and 'mV^2' in line:
        if '[' in line and ']' in line:
            channel = line.split('[')[1].split(']')[0].strip()
            power = line.split('mV^2')[0].split('=')[1].strip()
            lopa.rcu_data[key][f'FWD power TX{channel} (mV^2)'] = power
            channel_1 = line.split('[')[1].split(']')[0].strip()
            channel_2 = line.split('[')[2].split(']')[0].strip()
            power = line.split('mV^2')[0].split('=')[1].strip()
            if channel_1 == channel_2:
                if 'at RF amplifier' in line:
                    lopa.rcu_data[key][f'FWD amp power TX{channel_1} (mV^2)'] = power
                elif 'at RF circulator' in line:
                    lopa.rcu_data[key][f'FWD circ power TX{channel_1} (mV^2)'] = power
    elif 'refl power' in line and 'mV^2' in line:
        if '[' in line and ']' in line:
            channel_1 = line.split('[')[1].split(']')[0].strip()
            channel_2 = line.split('[')[2].split(']')[0].strip()
            power = line.split('mV^2')[0].split('=')[1].strip()
            if channel_1 == channel_2:
                lopa.rcu_data[key][f'RFL power TX{channel_1} (mV^2)'] = power
        
    elif 'vswr' in line:
        if '[' in line and ']' in line:
            channel = line.split('[')[1].split(']')[0].strip()
            vswr = line.split('=')[1].strip()
            lopa.rcu_data[key][f'vswr TX{channel}'] = vswr

def _process_amp_power(lopa, line):
    time, text = get_time_and_text(line) 

    key = (lopa.date, lopa.exam_id, lopa.scan_index)
    if key not in lopa.amp_power_data:
        lopa.amp_power_data[key] = {
            'Date': lopa.date,
            'Time': time,
            'Exam ID': lopa.exam_id
        }
    if 'ch' in line and 'TRANSMIT' in line and 'measured FAP' in line and 'expected' in line:
        channel = text.split('ch')[1].split('TRANSMIT')[0].strip()
        avg_power = text.split('measured FAP')[1].split('W')[0].strip()
        expected_power = text.split('expected')[1].split('W')[0].strip()
        if key in lopa.amp_power_data:
            lopa.amp_power_data[key][f'Measured power TX{channel} (W)'] = avg_power
            lopa.amp_power_data[key][f'Expected power TX{channel} (W)'] = expected_power
    else:
        print(f'split char not in {time}: {line}')

def _process_pu(lopa, line):
    time, text = get_time_and_text(line)
    if 'PU' in line and 'uT' in line and ',' in line:
        b1_values = text.split('=')[1].split('uT')[0].split(',')
        for i in range(len(b1_values)):
            b1_values[i] = b1_values[i].strip()
        data = (lopa.date, time, lopa.exam_id, *b1_values)
        lopa.pu_data.append(data)
    else:
        print(f'split char not in {time}: {line}')

def _process_spikes(lopa, line):
    time, text = get_time_and_text(line)
    key = (lopa.date, lopa.exam_id, lopa.scan_index)
    if key not in lopa.spikes_data and lopa.scan_index > 0:
        lopa.spikes_data[key] = {
            'Date': lopa.date,
            'Time': time,
            'Exam ID': lopa.exam_id
        }
    matches = re.findall(lopa.regex_spikes, text)
    for match in matches:
        # map the spike names to the names in the dict
        mapped_name = lopa.spikes_maps[match[0]] if match[0] in lopa.spikes_maps else None
        if mapped_name:
            lopa.spikes_data[key][mapped_name] = match[1].split('percent')[0].strip() if 'percent' in match[1] else match[1].strip()

def _process_tm(lopa, line):
    time, text = get_time_and_text(line)
    key = (lopa.date, lopa.exam_id, lopa.scan_index)
    if key not in lopa.tune_coil_data and lopa.scan_index > 0:
        lopa.tune_coil_data[key] = {
            'Date': lopa.date,
            'Time': time,
            'Exam ID': lopa.exam_id
        }
    matches = re.findall(lopa.regex_tm, text)
    for match in matches:
        if 'TQ' in match[0]:
            lopa.tune_coil_data[key][f'Tune Coil {match[1]} Offset (kHz)'] = match[2].strip()
            lopa.tune_coil_data[key][f'Tune Coil {match[1]} Q'] = match[3].strip()
            lopa.tune_coil_data[key][f'Tune Coil {match[1]} Amplitude (mV)'] = match[4].strip()
        elif 'RQ' in match[0]:
            lopa.tune_coil_data[key][f'Receive Coil {match[1]} Offset (kHz)'] = match[2].strip()
            lopa.tune_coil_data[key][f'Receive Coil {match[1]} Q'] = match[3].strip()
            lopa.tune_coil_data[key][f'Receive Coil {match[1]} Amplitude (mV)'] = match[4].strip()

def _process_f0_mag(lopa, line):
    time, text = get_time_and_text(line)

    if lopa.scan_index > 0:
        matches = re.findall(lopa.regex_channel_f0_magnitude, text)
        for match in matches:
            channel = match[0]
            channel_magnitude = match[1]
            coil = match[2]
            key = (lopa.date, time, lopa.exam_id, lopa.scan_index, coil)
            if key not in lopa.channel_magnitude_data:
                lopa.channel_magnitude_data[key] = {
                    'Date': lopa.date,
                    'Time': time,
                    'Exam ID': lopa.exam_id
                }
            lopa.channel_magnitude_data[key]['Coil'] = coil
            lopa.channel_magnitude_data[key][f'Ch{channel} Magnitude (mV)'] = channel_magnitude


def _process_noise(lopa, line):
    time, text = get_time_and_text(line)
    noise_matches = re.findall(lopa.regex_noise, text)
    for match in noise_matches:
        coil = match[0]
        coil_channel = match[1]
        noise = match[2]
        key = (lopa.date, lopa.exam_id, lopa.scan_index, coil, coil_channel)
        if key not in lopa.noise_data:
            lopa.noise_data[key] = {
                'Date': lopa.date,
                'Time': time,
                'Exam ID': lopa.exam_id,
                'Coil': coil
            }
        lopa.noise_data[key]['Channel'] = coil_channel
        lopa.noise_data[key]['Noise (uV)'] = noise

def _process_cf_fcratio(lopa, line): # before feb 2020 there are only fc ratios not max diff
    time, text = get_time_and_text(line)
    matches = re.findall(lopa.regex_fc, text) 
    for match in matches:
        # coil = match[0] channel = match[1] cali_process = match[2] ratio = match[3]
        key = (lopa.date, lopa.exam_id, lopa.scan_index, match[0], match[1])
        if key not in lopa.cf_data:
            lopa.cf_data[key] = {
                'Date': lopa.date,
                'Time': time,
                'Exam ID': lopa.exam_id,
                'Coil': match[0],
                'Channel': match[1]
            }

        if 'ratio' in text:
            lopa.cf_data[key][f'{match[2].strip()} fc ratio'] = match[3]
        elif 'phase_coarse' in text:
            lopa.cf_data[key][f'{match[2].strip()} phase coarse'] = match[3]
        elif 'phase_fine' in text:
            lopa.cf_data[key][f'{match[2].strip()} phase fine'] = match[3]

def _process_cf_phase_diff(lopa, line):
    time, text = get_time_and_text(line)
    match_maxdiff = re.findall(lopa.regex_maxdiff, text)
    # coil = match[0] channel = match[1] coarse/fine = match[2] maxdiff = match[3] cali_process = match[4]
    for match in match_maxdiff:
        cali_process = lopa.f0_maps[match[4]] if match[4] in lopa.f0_maps else None
        key = (lopa.date, lopa.exam_id, lopa.scan_index, match[0], match[1])
        if key not in lopa.cf_phase_diff_data:
            lopa.cf_phase_diff_data[key] = {
                'Date': lopa.date,
                'Time': time,
                'Exam ID': lopa.exam_id,
                'Coil': match[0],
                'Channel': match[1],
                'Calibration Process': cali_process
            }
        lopa.cf_phase_diff_data[key][f'{cali_process} {match[2]} max diff'] = match[3]
    
def _process_time_align(lopa, line):
    time, text = get_time_and_text(line)
    match_time_align = re.findall(lopa.regex_time_align, text)
    # coil = match[0] receiver = match[1] delay = match[2]
    for match in match_time_align:
        coil = match[0]
        receiver = match[1]
        key = (lopa.date, lopa.exam_id, lopa.scan_index, coil, receiver)
        if key not in lopa.time_align_data:
            lopa.time_align_data[key] = {
                'Date': lopa.date,
                'Time': time,
                'Coil': coil,
                'Receiver': receiver
            }
        lopa.time_align_data[key]['Delay'] = match[2]

def _process_control_loop(lopa, line):
    time, text = get_time_and_text(line)
    matches = re.findall(lopa.regex_control_loop, text)
    # channel = match[0], gain = match[1], phase = match[2], delay = match[3]
    for match in matches:
        channel = match[0]
        key = (lopa.date, lopa.exam_id, lopa.scan_index, channel)
        if key not in lopa.control_loop_data:
            lopa.control_loop_data[key] = {
                'Date': lopa.date,
                'Time': time,
                'Channel': channel
            }
        lopa.control_loop_data[key]['Gain'] = match[1]
        lopa.control_loop_data[key]['Phase'] = match[2]
        lopa.control_loop_data[key]['Delay'] = match[3]