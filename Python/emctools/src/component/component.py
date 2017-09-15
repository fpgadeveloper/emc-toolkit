'''

The component class stores gain/loss factors for a particular
component and provides functions that can calculate interpolated 
gain/loss factors for a given array of frequencies, and also correct
a measurement.

The component class is intended to represent gains from a preamp
or losses from an antenna or cable.

The constructor is called with a 'filename' string argument which
is the name of a CSV file containing the gain/loss factors. Refer
to the example antenna factor CSV files in this project. Note that
the gains/losses must always be represented in dB.

The CSV file must always contain losses for antennas and cables, and
gains for preamps. For example, if the cable has a loss of 5dB, the
value in the CSV file should be 5 and not -5. The 'loss' boolean
argument of the constructor specifies if the gain/loss factors are 
gains or losses. 

'''

import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
import csv

"""
Component class
"""
class component(object):
    """ """
    def __init__(self,name,filename,loss=True):
        # Read the gain/loss factor CSV file
        with open(filename) as csvfile:
            r = csv.reader(csvfile)
            # Skip comments
            line = next(r)
            while line != ['Frequency','Factor']:
                line = next(r)
            # Read gain/loss factors into numpy array
            self.factors = np.array(list(r),dtype=np.float)
        # Name of this component
        self.name = name
        # Gain or loss
        self.loss = loss
        # f = frequency, gl = gain/loss factor 
        f = self.factors.T[0]
        gl = self.factors.T[1]
        # Calculate the interpolation representation
        self.tck = interpolate.splrep(f, gl, s=0)
        # Start and end frequencies
        self.start_freq = f[0]
        self.stop_freq = f[-1]
        
    """ Interpolated gain/loss factors for an array of frequencies """
    def get_factors(self,freq):
        return(interpolate.splev(freq, self.tck, der=0))
    
    """ Corrected measurement """
    def corrected_measurement(self,trace):
        # tr[0] = frequency, tr[1] = measurement 
        tr = trace.T
        # Get interpolated gain/loss factors
        gl = self.get_factors(tr[0])
        # Return corrected measurement data
        if self.loss:
            corrected = tr[1] + gl
        else:
            corrected = tr[1] - gl
        return(np.array([tr[0],corrected]).T)


if __name__ == '__main__':
    """
    Displays the gain/loss factors and the interpolation
    """
    
    # Create the compoment
    antenna = component('Antenna factor','ab900a.csv',loss = True)
    
    # f = frequency, gl = gain/loss factor 
    f = antenna.factors.T[0]
    gl = antenna.factors.T[1]
    # Calculate the interpolated gain/loss factors
    f_new = np.linspace(f[0], f[-1], 1000)
    af_new = antenna.get_factors(f_new)
    
    plt.figure()
    plt.plot(f, gl, 'x', f_new, af_new)
    plt.title('Gain/loss factors cubic-spline interpolation')
    plt.show()

