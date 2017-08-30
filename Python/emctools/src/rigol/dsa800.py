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

"""
DSA800 class to represent the spectrum analyzer
"""
class dsa800(object):
    """ """
    def __init__(self):
        # Create the resource manager
        self.rm = visa.ResourceManager()
        self.resource = None

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

    """ Get resolution bandwidth (RBW) """
    def set_rbw(self,freq):
        self.resource.write(":SENSe:BAND %d" % freq)
    
    """ Get resolution bandwidth (RBW) """
    def get_rbw(self):
        return self.resource.query(":SENSe:BAND?")
    
    """ Get trace data """
    def get_trace(self):
        result = self.resource.query(":TRACe:DATA? TRACE1")
        return(self.parse_ascii(result))
        
    """ Set data format (ASCii,REAL) """
    def set_data_format(self,value):
        self.resource.write(":FORMat:TRACe:DATA ASCii")
        
    """ Get data format (ASCii,REAL) """
    def get_data_format(self):
        return self.resource.query(":FORMat:TRACe:DATA?")
        
    """ Set trace mode (WRITe, MAXHold, MINHold, VIEW, BLANk, VIDeoavg, POWeravg) """
    def set_trace_mode(self,mode):
        self.resource.write(":TRACe1:MODE %s" % mode)
        
    """ Get trace mode (WRITe, MAXHold, MINHold, VIEW, BLANk, VIDeoavg, POWeravg) """
    def get_trace_mode(self):
        return self.resource.query(":TRACe1:MODE?")
        
    """ Set units (DBM, DBMV, DBUV, V, W) """
    def set_unit(self,unit):
        self.resource.write(":UNIT:POWer %s" % unit)
        
    """ Get units (DBM, DBMV, DBUV, V, W)"""
    def get_unit(self):
        return self.resource.query(":UNIT:POWer?")
        
    """ Send (install) a purchased license key """
    def send_license_key(self,key):
        self.resource.write(":SYSTem:LKEY %s" % key)
        
    """ Set DSA configuration """
    def set_config(self,config):
        # Set the data format
        self.set_data_format(config.data_format)
        # Set the trace mode
        self.set_trace_mode(config.trace_mode)
        # Enable/disable preamp
        self.set_preamp_en(config.preamp_en)
        # Set the units
        self.set_unit(config.units)
        # Set the EMI filter enable
        self.set_emi_filter_en(config.emi_filter_en)
        # Set the resolution bandwidth
        self.set_rbw(config.rbw)
        # Set the TG output enable
        self.set_tg_output_en(config.tg_en)
        # Set the TG amplitude
        self.set_tg_amplitude(config.tg_amplitude)
        
    """ Get trace (advanced) - returns 2-dim numpy array of floats """
    def get_trace_adv(self,start_freq,stop_freq,span,delay=0):
        # Initialize start frequency and trace list
        start_f = start_freq
        trace = np.array([],np.float)
        while(start_f < stop_freq):
            # Set the start freq
            print("Setting start freq to:",start_f)
            self.set_start_freq(start_f)
            # Set the stop freq
            self.set_stop_freq(start_f + span)
            print("Start:",self.get_start_freq(),"Stop:",self.get_stop_freq(),"Span:",self.get_span())
            # Allow time to average the trace
            time.sleep(delay)
            # Read the trace data
            trace_data = self.get_trace()
            # Append all data except the last point
            trace = np.append(trace,trace_data[:-1])
            # Increment the start freq
            start_f = start_f + span
        
        # Append the endpoint
        trace = np.append(trace,trace_data[-1])
        
        # Generate the frequency points
        freq = np.linspace(start_freq,self.get_stop_freq(),len(trace))
        
        return(np.array([freq,trace]).T)
    
    """ Close the connection to the resource """
    def close(self):
        self.resource.close()

"""
DSA800 configuration class for storing a particular configuration
"""
class dsa800_config():
    def __init__(self):
        self.data_format = 'ASCii'
        self.trace_mode = 'WRITe'
        self.preamp_en = False
        self.units = 'DBM'
        self.emi_filter_en = False
        self.rbw = 100000
        self.tg_en = False
        self.tg_amplitude = -40


        
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
    config.trace_mode = 'POWeravg'
    config.preamp_en = True
    config.units = 'DBUV'
    config.emi_filter_en = True
    config.rbw = 120000
    
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
    
    
    
    