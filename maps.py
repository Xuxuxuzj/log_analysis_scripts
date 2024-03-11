
def generate_map(keyword):
    if keyword == 'FilePath':
        return get_file_path_maps()
    elif keyword == 'Header':
        return get_header_maps()
    elif keyword == 'LCC':
        return get_lcc_maps()
    elif keyword == 'Spike':
        return get_spike_maps()
    elif keyword == 'F0':
        return get_f0_maps()


def get_file_path_maps(): # matches the names of data instances within the LogParser class to names of the folders where the data are stored
    return {
        'hum_exam_room_data': 'Hum Exam Room', # humidity of the examination room
        'hum_tech_room_data': 'Hum Tech Room', # humdity of the tech room
        'temp_exam_room_data': 'Temp Exam Room', #temperature of the examination room 
        'temp_tech_room_data': 'Temp Tech Room', # temperature of the tech room
        'dps_fault_data': 'DPS Fault', # magnet pressure status fault in minutes
        'latched_error_data': 'Latched Error', # latched error 1, 2, 3, 4
        'helium_avg_pressure_data': 'Helium Avg Pressure', # helium pressure 3H average
        'cryo_malfunction_data': 'Cryo Malfunction', # cryo malfunction in minutes
        'cryo_switch_data': 'Cryo Switch Status', # cryo switch status (on/off)
        'f0_data': 'F0', # set water frequency
        'pu_data': 'Pick-Up', # pick-up b1 magnitudes
        'stt_results_data': 'STT Results', # STT results
        'device_data': 'Device', # connected device names and serial numbers of each day
        'psu_voltage_data': 'Power Supply Unit Voltage', # power supply unit voltage
        'psu_temp_data': 'Power Supply Unit Temperature', # power supply unit temperature
        'stt_linkerr_data': 'STT Link Error', # link errors
        'magnet_daily_monitor_data': 'Magnet Daily Monitor', # a number of magnet daily monitor parameter data
        'lcc_data': 'Liquid Cabinet Cooler', # liquid cabinet cooler data
        'exam_data': 'Exam', # general exam data
        'scan_data': 'Scan', # general scan data
        'rcu_data': 'Circulator Unit',# circulator unit data
        'amp_power_data': 'Amp Power', # amplifier power data
        'spikes_data': 'Spikes', # spike data
        'tune_coil_data': 'Tune Coil', # tune coil data
        'channel_magnitude_data': 'Channel Signal Magnitude',  # channel signal magnitude data
        'noise_data': 'Noise', # noise data
        'cf_data': 'Coarse Fine', # coarse fine tuning
        'cf_phase_diff_data': 'Coarse Fine Phase Difference', # also coarse fine tuning
        'time_align_data': 'Time Align', # time alignment data
        'control_loop_data': 'Control Loop' # control loop data
    }

def get_header_maps():
    return {
        'hum_exam_room_data': ['Date', 'Time', 'Exam Room Humidity (%)'],
        'hum_tech_room_data': ['Date', 'Time', 'Tech Room Humidity (%)'],
        'temp_exam_room_data': ['Date', 'Time', 'Exam Room Temperature (C)'],
        'temp_tech_room_data': ['Date', 'Time', 'Tech Room Temperature (C)'],
        'dps_fault_data': ['Date', 'Time', 'DPS Fault (minutes)'],
        'latched_error_data': ['Date', 'Time', 'Latched Error 1', 'Latched Error 2', 'Latched Error 3', 'Latched Error 4'],
        'helium_avg_pressure_data': ['Date', 'Time', 'Helium Pressure 3H Average (mbar)'],
        'cryo_malfunction_data': ['Date', 'Time', 'Cryo Malfunction (minutes)'],
        'cryo_switch_data': ['Date', 'Time', 'Cryo Switch (0=On, 1=Off)'],
        'f0_data': ['Date', 'Time', 'Exam ID', 'Set f0 (Hz)'],
        'pu_data': ['Date', 'Time', 'Exam ID', 'PU1 b1 (uT)', 'PU2 b1 (uT)'],
    }

def get_lcc_maps():
    return {
    'LCCSecondaryLoopValvePosition': 'LCCSecondaryLoop ValvePosition',
    'LCCSecondaryLoopTempSetpoint_C': 'LCCSecondaryLoop TempSetpoint [C]',
    'LCCSecondaryLoopControlOutput': 'LCCSecondaryLoop ControlOutput',
    'LCCSecondaryLoopProportionalGain': 'LCCSecondaryLoop ProportionalGain',
    'LCCSecondaryLoopIntegrationTime': 'LCCSecondaryLoop IntegrationTime',
    'LCCSecondaryLoopOperatingHours': 'LCCSecondaryLoop OperatingHours',
    'LCCSecondaryLoopErrorCode': 'LCCSecondaryLoop ErrorCode',
    'LCCSecondaryCoolingTemp_C': 'LCCSecondaryLoopTemperature of the Secondary cooling circuit[C]',
    'LCCT1CoolingTemp_C': 'LCC T1 Temperature of the LCC[C]',
    'LCCPrimaryFlow_lpm': 'LCC Flow of the (primary) incoming flow [liter/minute]',
    'LCCSecondaryLoopPressure_bar': 'LCCSecondaryLoop Filling pressure of the Secondary cooling circuit[bar]',
    'LCCHeCompressorTemp_C': 'LCC Helium Compressor Temperature of the LCC[C]',
    'LCCGradCoilValvePosition': 'LCCGradCoil ValvePosition',
    'LCCGradAmpValvePosition': 'LCCGradAmp ValvePosition',
    "LCCGradCoilTempSetpoint_C" : "LCCGradCoilTempSetpoint [C]" , 
    "LCCGradAmpTempSetpoint_C" : "LCCGradAmp TempSetpoint [C]" , 
    "LCCGradCoilControlOutput" : "LCCGradCoil ControlOutput" , 
    "LCCGradAmpControlOutput" : "LCCGradAmp ControlOutput" , 
    "LCCGradCoilProportionalGain" : "LCCGradCoil ProportionalGain" , 
    "LCCGradAmpProportionalGain" : "LCCGradAmp ProportionalGain" , 
    "LCCGradCoilIntegrationTime" : "LCCGradCoil IntegrationTime" , 
    "LCCGradAmpIntegrationTime" : "LCCGradAmp IntegrationTime" , 
    "LCCGradCoilOperatingHours" : "LCCGradCoil OperatingHours" , 
    "LCCGradAmpOperatingHours" : "LCCGradAmp OperatingHours" ,
    "LCCGradCoilErrorCode" : "LCCGradCoil ErrorCode" , 
    "LCCGradAmpErrorCode" : "LCCGradAmp ErrorCode" , 
    "LCCGradCoilCoolingTemp_C" : "LCCGradCoil CoolingTemp [C]" , 
    "LCCGradAmpCoolingTemp_C" : "LCCGradAmp CoolingTemp [C]" ,
    "LCCGradCoilPressure_bar" : "LCCGradCoil Filling pressure of the Gradient Coil cooling circuit[bar]" ,
    "LCCGradAmpPressure_bar" : "LCCGradAmp Filling pressure of the Gradient amplifier cooling circuit[bar]"
    }

def get_spike_maps():
    return {
        'factor responses detected': 'Factor Responses Detected (%)',
        'nr suppressed': 'Number Spikes Suppressed',
        'noise power time sample': 'Noise Power Time Sample',
        'nr above threshold 1': 'Number Spikes Above Threshold 1',
        'nr above threshold 2': 'Number Spikes Above Threshold 2',
        'nr above threshold 3': 'Number Spikes Above Threshold 3',
        'power above threshold 1': 'Power Above Threshold 1',
        'power above threshold 2': 'Power Above Threshold 2',
        'power above threshold 3': 'Power Above Threshold 3',
        'nr expected': 'Number Spikes Expected',
        'noise fraction': 'Noise Fraction',
        'QPI': 'QPI',
        'QPI after correction': 'QPI After Correction'
    }

def get_f0_maps():
    return {
        'f0': 'F0',
        'f0_min': 'F0-',
        'f0_plus': 'F0+'
    }

