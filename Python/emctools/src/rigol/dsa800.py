"""

DSA800 module for controlling DSA800 series spectrum analyzers via NI-VISA

Requirements:
-------------

* Python 3.6

* Numpy is needed for the trace data

* PyVISA must be installed (pip install -U pyvisa)
  See docs: https://pyvisa.readthedocs.io/en/stable/

* NI-VISA must be installed
  See here: https://pyvisa.readthedocs.io/en/stable/getting_nivisa.html

References:
-----------

* RIGOL Programming Guide for DSA800E Series Spectrum Analyzer
  http://int.rigol.com/File/TechDoc/20160603/DSA800E_ProgrammingGuide_EN.pdf

* PyVISA docs
  https://pyvisa.readthedocs.io/en/stable/
  
"""

import visa
import time
import numpy as np
import sys
from enum import Enum
import json

"""
Setting dicts

When querying a setting, the DSA800 sometimes returns a different code than 
the one used to write the setting. For example, when setting the data format
to ASCII, we use the setting name 'ASCii' or 'ASC', however, when querying 
the data format, the DSA800 returns 'ASCII' (all caps). For this reason, we
use dicts to convert the query results to the names used when we write. This 
allows for uniformity when storing settings.
"""

DATA_FORMAT = {'ASCII':'ASCii', 'REAL': 'REAL'}
    
UNITS = {'DBM': 'DBM', 'DBMV': 'DBMV', 'DBUV': 'DBUV', 'V': 'V', 'W': 'W'}

TRACE_MODE = {'WRIT': 'WRITe', 'MAXH': 'MAXHold', 
              'MINH': 'MINHold', 'VIEW': 'VIEW', 
              'BLAN': 'BLANk', 'VID': 'VIDeoavg', 
              'POW': 'POWeravg'}

DET_FUNC = {'NEG': 'NEGative', 'NORM': 'NORMal', 
            'POS':'POSitive', 'RMS':'RMS', 
            'SAMP':'SAMPle', 'VAV':'VAVerage', 
            'QPEAK':'QPEak'}


"""
DSA800 class to represent the spectrum analyzer
"""
class dsa800(object):
    """ """
    def __init__(self):
        # Create the resource manager
        self.rm = visa.ResourceManager()
        self.resource = None
        self.config_func = {
            'data_format' : {'set':self.set_data_format,'get':self.get_data_format},
            'sweep_points' : {'set':self.set_sweep_points,'get':self.get_sweep_points},
            'trace_mode' : {'set':self.set_trace_mode,'get':self.get_trace_mode},
            'preamp_en' : {'set':self.set_preamp_en,'get':self.get_preamp_en},
            'units' : {'set':self.set_unit,'get':self.get_unit},
            'emi_filter_en' : {'set':self.set_emi_filter_en,'get':self.get_emi_filter_en},
            'rbw' : {'set':self.set_rbw,'get':self.get_rbw},
            'tg_en' : {'set':self.set_tg_output_en,'get':self.get_tg_output_en},
            'tg_amplitude' : {'set':self.set_tg_amplitude,'get':self.get_tg_amplitude},
            'det_func' : {'set':self.set_detector_function,'get':self.get_detector_function},
            }

    """ Returns a list of detected VISA resource names """
    def list_devices(self):
        return self.rm.list_resources()
        
    """ Connect to the DSA using the id string """
    def connect(self, idn):
        self.resource = self.rm.open_resource(idn,send_end=True,query_delay=1)
        self.resource.read_termination = '\n'
        self.resource.write_termination = '\n'
        self.resource.timeout = 5000

    """ Get the DSA identification string """
    def get_id(self):
        return self.resource.query("*IDN?")

    """ Get operation finished """
    def get_opc(self):
        if self.resource.query("*OPC?") == '1':
            return(True)
        else:
            return(False)

    """ Trigger a sweep or measurement immediately """
    def trigger(self):
        self.resource.write("*TRG")

    """ Parse ASCII trace data into a list of numpy floats """
    def parse_ascii(self,data):
        # The first character should be '#'
        if data[0] != '#':
            return None
        # The second character should be '9'
        if data[1] != '9':
            return None
        # Remove the commas
        data = data.replace(',','')
        # Split the data by spaces
        str_list = data.split()
        return np.array(str_list[1:],np.float)

    """ Set continuous enable (True,False) """
    def set_continuous_en(self, en):
        if en:
            self.resource.write(":INITiate:CONTinuous ON")
        else:
            self.resource.write(":INITiate:CONTinuous OFF")

    """ Get continuous enabled (True,False) """
    def get_continuous_en(self):
        en = self.resource.query(":INITiate:CONTinuous?")
        if((en == "ON") or (en == "1")):
            return True
        else:
            return False

    """ In single measurement mode, trigger a sweep or measurement immediately """
    def trigger_single_sweep(self):
        self.resource.write(":INITiate:IMMediate")

    """ Set span in Hz (integer) """
    def set_span(self, span):
        self.resource.write(":SENSe:FREQ:SPAN %d" % span)

    """ Get span in Hz (integer) """
    def get_span(self):
        return int(self.resource.query(":SENSe:FREQ:SPAN?"))

    """ Set center frequency in Hz (integer) """
    def set_centerfreq(self, freq):        
        self.resource.write(":SENSe:FREQ:CENT %d" % freq)
        
    """ Get center frequency in Hz (integer) """
    def get_centerfreq(self):        
        return int(self.resource.query(":SENSe:FREQ:CENT?"))
        
    """ Set start frequency in Hz (integer) """
    def set_start_freq(self,freq):
        return self.resource.write(":SENSe:FREQ:STARt %d" % freq)

    """ Get start frequency in Hz (integer) """
    def get_start_freq(self):
        return int(self.resource.query(":SENSe:FREQ:STARt?"))

    """ Set stop frequency in Hz (integer) """
    def set_stop_freq(self,freq):
        return self.resource.write(":SENSe:FREQ:STOP %d" % freq)

    """ Get stop frequency in Hz (integer) """
    def get_stop_freq(self):
        return int(self.resource.query(":SENSe:FREQ:STOP?"))

    """ Set preamp enabled (True,False) """
    def set_preamp_en(self,en):
        if en:
            self.resource.write(":SENSe:POW:GAIN ON")
        else:
            self.resource.write(":SENSe:POW:GAIN OFF")
            
    """ Get preamp enabled (True,False) """
    def get_preamp_en(self):
        en = self.resource.query(":SENSe:POW:GAIN?")
        if((en == "ON") or (en == "1")):
            return True
        else:
            return False
        
    """ Set TG output enabled (True,False) """
    def set_tg_output_en(self, en):
        if en:
            self.resource.write(":OUTput:STATe ON")
        else:
            self.resource.write(":OUTput:STATe OFF")

    """ Get TG output enabled (True,False) """
    def get_tg_output_en(self):
        en = self.resource.query(":OUTput:STATe?")
        if((en == "ON") or (en == "1")):
            return True
        else:
            return False

    """ Set TG output amplitude (dBm: -40 to 0, integer) """
    def set_tg_amplitude(self, dbm):
        self.resource.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude %d" % dbm)

    """ Get TG output amplitude (dBm: -40 to 0, integer) """
    def get_tg_amplitude(self):
        return int(self.resource.query(":SOURce:POWer:LEVel:IMMediate:AMPLitude?"))

    """ Set EMI filter enabled (True,False) """
    def set_emi_filter_en(self, en):
        if en:
            self.resource.write(":SENSe:BANDwidth:EMIFilter:STATe ON")
        else:
            self.resource.write(":SENSe:BANDwidth:EMIFilter:STATe OFF")

    """ Get EMI filter enabled (True,False) """
    def get_emi_filter_en(self):
        en = self.resource.query(":SENSe:BANDwidth:EMIFilter:STATe?")
        if((en == "ON") or (en == "1")):
            return True
        else:
            return False

    """ Set resolution bandwidth (RBW) """
    def set_rbw(self,freq):
        self.resource.write(":SENSe:BAND %d" % freq)
    
    """ Get resolution bandwidth (RBW) """
    def get_rbw(self):
        return self.resource.query(":SENSe:BAND?")
    
    """ Get sweep count current (number of sweeps that have been finished in single sweep) """
    def get_sweep_count_current(self):
        return int(self.resource.query(":SENSe:SWEep:COUNt:CURRent?"))
    
    """ Set sweep count (number of sweeps to be executed in single sweep, 1 to 9999) """
    def set_sweep_count(self,count):
        if 1 <= count <= 9999:
            self.resource.write(":SENSe:SWEep:COUNt %d" % count)
        else:
            print('Sweep count must be integer between 1 and 9999')
    
    """ Get sweep count (number of sweeps to be executed in single sweep, 1 to 9999) """
    def get_sweep_count(self):
        return int(self.resource.query(":SENSe:SWEep:COUNt?"))
    
    """ Set sweep points (101 to 3001) """
    def set_sweep_points(self,points):
        self.resource.write(":SENSe:SWEep:POINts %d" % points)
    
    """ Get sweep points (101 to 3001) """
    def get_sweep_points(self):
        return int(self.resource.query(":SENSe:SWEep:POINts?"))
    
    """ Set sweep time (20e-06 to 3200 seconds) """
    def set_sweep_time(self,time):
        self.resource.write(":SENSe:SWEep:TIME %f" % time)
    
    """ Get sweep time (20e-06 to 3200 seconds) """
    def get_sweep_time(self):
        return float(self.resource.query(":SENSe:SWEep:TIME?"))
    
    """ Get trace data """
    def get_trace(self):
        result = self.resource.query(":TRACe:DATA? TRACE1")
        return(self.parse_ascii(result))
        
    """ Set data format (ASCii,REAL) """
    def set_data_format(self,value):
        if value in DATA_FORMAT.values():
            self.resource.write(":FORMat:TRACe:DATA %s" % value)
        else:
            print('Data format must be:',', '.join(DATA_FORMAT.values()))
        
    """ Get data format (ASCii,REAL) """
    def get_data_format(self):
        value = self.resource.query(":FORMat:TRACe:DATA?")
        return(DATA_FORMAT[value])
        
    """ Set detector function (NEGative,NORMal,POSitive,RMS,SAMPle,VAVerage,QPEak) """
    def set_detector_function(self,func):
        if func in DET_FUNC.values():
            self.resource.write(":DETector:FUNCtion %s" % func)
        else:
            print('Data format must be:',', '.join(DET_FUNC.values()))
        
    """ Get detector function (NEGative,NORMal,POSitive,RMS,SAMPle,VAVerage,QPEak) """
    def get_detector_function(self):
        func = self.resource.query(":DETector:FUNCtion?")
        return(DET_FUNC[func])
        
    """ Set trace mode (WRITe, MAXHold, MINHold, VIEW, BLANk, VIDeoavg, POWeravg) """
    def set_trace_mode(self,mode):
        if mode in TRACE_MODE.values():
            self.resource.write(":TRACe1:MODE %s" % mode)
        else:
            print('Trace mode must be:',', '.join(TRACE_MODE.values()))
        
    """ Get trace mode (WRITe, MAXHold, MINHold, VIEW, BLANk, VIDeoavg, POWeravg) """
    def get_trace_mode(self):
        mode = self.resource.query(":TRACe1:MODE?")
        return(TRACE_MODE[mode])
        
    """ Set units (DBM, DBMV, DBUV, V, W) """
    def set_unit(self,unit):
        if unit in UNITS.values():
            self.resource.write(":UNIT:POWer %s" % unit)
        else:
            print('Units must be:',', '.join(UNITS.values()))
        
    """ Get units (DBM, DBMV, DBUV, V, W)"""
    def get_unit(self):
        unit = self.resource.query(":UNIT:POWer?")
        return(UNITS[unit])
        
    """ Send (install) a purchased license key """
    def send_license_key(self,key):
        self.resource.write(":SYSTem:LKEY %s" % key)
        
    """ Set DSA configuration """
    def set_config(self,config):
        # Iterate through the parameters and set them
        for setting,value in config.param.items():
            self.config_func[setting]['set'](value)
        # Wait for config to be applied
        time.sleep(1)
        
    """ Get trace (advanced) - returns 2-dim numpy array of floats """
    def get_trace_adv(self,start_freq,stop_freq,span,sweeps=1):
        # Record current settings
        continuous_sweep = self.get_continuous_en()
        sweep_count = self.get_sweep_count()
        # Use single sweep mode and requested sweep count
        self.set_continuous_en(False)
        self.set_sweep_count(sweeps)
        # Remember the trace mode, because we need to reset this for each step
        trace_mode = self.get_trace_mode()
        # Initialize start frequency and trace list
        start_f = start_freq
        trace = np.array([],np.float)
        while(start_f < stop_freq):
            # Set the trace mode to reset the trace
            self.set_trace_mode(trace_mode)
            # Set the start freq
            print("Setting start freq to:",start_f)
            self.set_start_freq(start_f)
            # Set the stop freq
            self.set_stop_freq(start_f + span)
            print("Start:",self.get_start_freq(),"Stop:",self.get_stop_freq(),"Span:",self.get_span())
            # Calculate time expected to complete all sweeps and wait
            wait_time = self.get_sweep_time() * sweeps * 0.9
            # Trigger the single sweep
            self.trigger_single_sweep()
            # Sleep for the expected completion time
            time.sleep(wait_time)
            # Wait until sweep count reaches the total count
            sweep_current = self.get_sweep_count_current()
            while sweep_current < sweeps:
                time.sleep(1)
                sweep_current = self.get_sweep_count_current()
            # Read the trace data
            trace_data = self.get_trace()
            # Append all data except the last point
            trace = np.append(trace,trace_data[:-1])
            # Increment the start freq
            start_f = start_f + span
        
        # Return to original sweep settings
        self.set_continuous_en(continuous_sweep)
        self.set_sweep_count(sweep_count)
        
        # Append the endpoint
        trace = np.append(trace,trace_data[-1])
        
        # Generate the frequency points
        freq = np.linspace(start_freq,self.get_stop_freq(),len(trace))
        
        return(np.array([freq[freq < stop_freq],trace[freq < stop_freq]]).T)
    
    """ Close the connection to the resource """
    def close(self):
        self.resource.close()

"""
DSA800 configuration class for storing a particular configuration
"""
class dsa800_config():
    def __init__(self,param=None,json_keys=None,json_values=None):
        # If given a list of keys and values as JSON strings
        if json_keys and json_values:
            key_list = [json.loads(k) for k in json_keys]
            value_list = [json.loads(v) for v in json_values]
            self.param = dict(zip(key_list,value_list))
        else:
            # Default parameters
            self.param = {
                'data_format' : 'ASCii',
                'trace_mode' : 'WRITe',
                'sweep_points' : 601,
                'preamp_en' : False,
                'units' : 'DBM',
                'emi_filter_en' : False,
                'rbw' : 100000,
                'tg_en' : False,
                'tg_amplitude' : -40,
                'det_func' : 'POSitive'
                }
            # Update parameters if provided
            if param:
                self.param.update(param)
            
    def get_json_names(self):
        return([json.dumps(k) for k in self.param.keys()])

    def get_json_values(self):
        return([json.dumps(v) for v in self.param.values()])
    
        
        
if __name__ == '__main__':
    """
    Example usage code
    """
    
    # The VISA resource name below must be replaced by that of your DSA.
    visa_id = "USB0::0x1AB1::0x0960::<dsa-serial-num>::INSTR"
    
    # Create the DSA object
    dsa = dsa800()
    
    # Create the DSA configuration
    config = dsa800_config()
    config.param['preamp_en'] = True
    config.param['units'] = 'DBUV'
    config.param['emi_filter_en'] = True
    config.param['rbw'] = 120000
    
    # Connect to the DSA using the identity string
    try:
        dsa.connect(visa_id)
    except:
        print("Failed to connect to VISA resource:",visa_id)
        print('Please make sure that your DSA is connected via UART, USB or TCP')
        print('Here is a list of the detected VISA resources:')
        for dev in dsa.list_devices():
            print('  ',dev)
        sys.exit()

    # Display information about connected DSA
    print("Connected to:", dsa.get_id())

    # Configure DSA
    dsa.set_config(config)
    
    # Get the trace data
    trace_data = dsa.get_trace()
    
    print("Trace data:",trace_data)
    
    # Close the connection with DSA815
    dsa.close()
    
    print("Connection closed")
    
    
    
    