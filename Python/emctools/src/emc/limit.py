'''

The limit class stores emissions limits for a particular standard
and provides functions that can calculate interpolated limits
for a given array of frequencies. 

'''

import numpy as np
import matplotlib.pyplot as plt

"""
Limit class to represent emissions limits
"""
class limit(object):
    """ """
    def __init__(self):
        # Create the limits
        self.limit_table = {
            'fccclassa':[(30e6,88e6,300,49.6,90,39.1),
                       (88e6,216e6,500,54,150,43.5),
                       (216e6,960e6,700,56.9,210,46.4),
                       (960e6,10e9,1000,60,300,49.5)],
            'fccclassb':[(30e6,88e6,100,40,30,29.5),
                       (88e6,216e6,150,43.5,45,33.1),
                       (216e6,960e6,200,46,60,35.6),
                       (960e6,10e9,500,54,150,43.5)],
            'cispr22classa':[(30e6,230e6,333.3,50.5,100,40),
                       (230e6,1000e6,746.2,57.5,223.9,47)],
            'cispr22classb':[(30e6,230e6,105.4,40.5,31.6,30),
                       (230e6,1000e6,236,47.5,70.8,37)],
            }
        # Limit unit indexes
        self.unit_index = {'uV/m(3m)':2,'dBuV/m(3m)':3,'uV/m(10m)':4,'dBuV/m(10m)':5}
        
    """ The limits for a given array of frequencies """
    def limit_func(self,standard,units,freq):
        # Create a limit vector the same length as the freq vector
        limit_vec = np.zeros_like(freq)
        # Iterate through the table and apply the appropriate limit
        for l in self.limit_table[standard]:
            limit_vec[np.logical_and(freq > l[0],freq <= l[1])] = l[self.unit_index[units]]
        # Handle the lower limit condition
        limit_vec[freq == self.limit_table[standard][0][0]] = self.limit_table[standard][0][self.unit_index[units]]
        return(limit_vec)
    


if __name__ == '__main__':
    """
    Displays the emissions limit
    """
    # Create the limit object
    l = limit()
    
    # Calculate the interpolated afe factors
    f = np.linspace(30e6, 1000e6, 1000)
    l_func = l.limit_func('cispr22classb','dBuV/m(3m)',f)
    
    plt.figure()
    plt.plot(f, l_func)
    plt.title('Emissions limit')
    plt.show()

