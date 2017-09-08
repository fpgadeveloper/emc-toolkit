'''

The antenna class stores antenna factors for a particular antenna
and provides functions that can calculate interpolated antenna
factors for a given array of frequencies, and also correct a
measurement.

The constructor is called with a 'filename' string argument which
is the name of a CSV file containing the antenna factors. Refer
to the example antenna factor CSV files in this project.

'''

import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
import csv

"""
Antenna class
"""
class antenna(object):
    """ """
    def __init__(self,filename):
        # Read the antenna factor CSV file
        with open(filename) as csvfile:
            r = csv.reader(csvfile)
            # Skip comments
            line = next(r)
            while line != ['Frequency','AF']:
                line = next(r)
            # Read antenna factors into numpy array
            self.afe = np.array(list(r),dtype=np.float)
        # f = frequency, af = afe factor 
        f = self.afe.T[0]
        af = self.afe.T[1]
        # Calculate the interpolation representation
        self.tck = interpolate.splrep(f, af, s=0)
        # Start and end frequencies
        self.start_freq = f[0]
        self.stop_freq = f[-1]
        
    """ Interpolated afe factors for an array of frequencies """
    def antenna_factors(self,freq):
        return(interpolate.splev(freq, self.tck, der=0))
    
    """ Corrected measurement """
    def corrected_measurement(self,trace):
        # tr[0] = frequency, tr[1] = measurement 
        tr = trace.T
        # Get interpolated afe factors
        af = self.antenna_factors(tr[0])
        # Return corrected measurement data
        corrected = tr[1] + af
        return(np.array([tr[0],corrected]).T)


if __name__ == '__main__':
    """
    Displays the afe factors and the interpolation
    """
    
    # Create the afe
    ant = antenna('pcb_400_1000_lp.csv')
    
    # f = frequency, af = afe factor 
    f = ant.afe.T[0]
    af = ant.afe.T[1]
    # Calculate the interpolated afe factors
    f_new = np.linspace(f[0], f[-1], 1000)
    af_new = ant.antenna_factors(f_new)
    
    plt.figure()
    plt.plot(f, af, 'x', f_new, af_new)
    plt.title('Antenna factor cubic-spline interpolation')
    plt.show()

