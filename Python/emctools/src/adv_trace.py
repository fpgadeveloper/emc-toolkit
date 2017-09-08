'''
Advanced trace usage example

This script will use the get_trace_adv() function of the dsa800 class
to perform an advanced trace measurement. The advanced trace allows you
to make a wide spectrum measurement with high resolution. You must provide
a start and stop frequency and the span to be used over that range.
The get_trace_adv function will break up the frequency range into 
segments of width specified by the span argument. The function then
makes a measurement for each of the segments and concatenates the traces
into one array. It returns a nx2 numpy array where the first column
represents the frequencies (Hz) and the second column the trace.
'''

from rigol import dsa800,storage
import time
import datetime
import sys
from afe import antenna
from emc import limit
import json



if __name__ == '__main__':
    
    """ 
    Measurement parameters
    The measurement parameters are stored in the file params.txt
    """
    param_file = 'params.txt'
    try:
        # Load the parameters from the params.txt file
        with open(param_file) as fp:
            params = json.load(fp)
    except:
        # Create default parameters and save the file
        params = {
            'title': 'Product X Radiated Emissions',
            'antenna': 'afe\\ab900a.csv',
            'limit_std': 'cispr22classb',
            'limit_units': 'dBuV/m(3m)',
            'span': 100e6,
            'sweeps': 10,
            'dsa_cfg': {
                'trace_mode': 'MAXHold',
                'preamp_en': True,
                'units': 'DBUV',
                'emi_filter_en': True,
                'rbw': 120000,
                }
            }
        with open(param_file,'w') as fp:
            json.dump(params,fp,indent=2)
    
    # Create the DSA object
    dsa = dsa800.dsa800()

    # Create the antenna object    
    ant = antenna.antenna(params['antenna'])
    
    # Start timing
    start_time = time.time()
    
    # Connect to the first detected DSA800
    try:
        dsa.connect()
    except Exception as e:
        print('Please make sure that your DSA is connected via UART, USB or TCP')
        print('Here is a list of the detected VISA resources:')
        for dev in dsa.list_devices():
            print('  ',dev)
        sys.exit()

    print("Connected to:", dsa.get_id())

    # DSA815 configuration
    config = dsa800.dsa800_config(params['dsa_cfg'])
    
    # Configure DSA815
    dsa.set_config(config)
    
    """
    Perform the advanced trace
    - Use antenna limits to determine start and stop frequencies
    - Use 'span' from measurement parameters dict
    - Use 'sweeps' from measurement parameters dict
    """
    trace_data = dsa.get_trace_adv(
        ant.start_freq,
        ant.stop_freq,
        params['span'],
        sweeps = params['sweeps'])
    
    # Close the connection with DSA815
    dsa.close()
    
    # Correct the trace data for the antenna factors
    corrected =  ant.corrected_measurement(trace_data)
    
    # Calculate the limit
    lim = limit.limit()
    limit_data = lim.limit_func(params['limit_std'],params['limit_units'],trace_data[:,:-1])
    
    #  Create a unique filename using the date and time
    d = datetime.datetime.now()
    filename = 'trace-%s' % d.strftime('%Y-%m-%d-%H%M%S')
    
    # Write trace to CSV and PNG file
    measurement = storage.Measurement(params['title'],config)
    measurement.add_data(trace_data[:,0],trace_data[:,1],corrected[:,1],limit_data[:,0])
    measurement.save_to_csv('%s.csv' % filename)
    measurement.save_to_png('%s.png' % filename)
    
    # End the timer
    end_time = time.time()
    print('Execution time:',end_time-start_time)
    
    print('Completed')    
    
    