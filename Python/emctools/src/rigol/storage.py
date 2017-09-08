'''
For storage of DSA measurements in a CSV file

The goal is to be able to store all measurement parameters
so that a measurement can be replicated.
'''
import rigol.dsa800
import matplotlib.pyplot as plt
import numpy as np
import csv


class Measurement(object):
    def __init__(self,title=None,dsaconfig=None,filename=None):
        if filename:
            self.load_csv(filename)
        else:
            self.title = title
            self.config = dsaconfig
        
    def freq(self):
        return(self.data[:,0])
    
    def measured(self):
        return(self.data[:,1])
    
    def corrected(self):
        return(self.data[:,2])
    
    def limit(self):
        return(self.data[:,3])
    
    def add_data(self,freq,trace,corrected,limit):
        self.data = np.array([freq,trace,corrected,limit]).T
        
    def save_to_csv(self,filename):
        with open(filename, 'w', newline='') as csvfile:
            w = csv.writer(csvfile, delimiter=',')
            w.writerow([self.title])
            # Write the DSA configuration
            w.writerow(self.config.get_json_names())
            w.writerow(self.config.get_json_values())
            # Write the DSA and corrected readings
            w.writerow(['Frequency (Hz)','DSA','Corrected','Limit'])
            w.writerows(self.data)
        
    def load_csv(self,filename):
        with open(filename) as csvfile:
            r = csv.reader(csvfile)
            # Title
            self.title = next(r)[0]
            # DSA config
            config_keys = next(r)
            config_values = next(r)
            self.config = rigol.dsa800.dsa800_config(config_keys,config_values)
            next(r)
            self.data = np.array(list(r),dtype=np.float)
        
    def save_to_png(self,filename):
        # Plot the data to image file
        fig = plt.figure()
        plt.plot(self.freq(),self.corrected(),'-b',label='Measured')
        plt.plot(self.freq(),self.limit(),'-r',label='Limit')
        plt.legend(loc='lower right')
        fig.suptitle(self.title, fontsize=18)
        plt.xlabel('Frequency (Hz)', fontsize=12)
        plt.ylabel('Power (%s)' % self.config.param['units'], fontsize=12)
        fig.savefig('%s.png' % filename, dpi=900)
        plt.clf()
        plt.close(fig)
        
        

if __name__ == '__main__':
    pass