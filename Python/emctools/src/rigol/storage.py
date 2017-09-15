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
        self.components = []
        self.lim = None
        self.corrected_data = None
        self.limit_data = None
        
    def freq(self):
        return(self.data[:,0])
    
    def measured(self):
        return(self.data[:,1])
    
    def corrected(self):
        if self.corrected_data:
            return(self.corrected_data)
        # Correct the trace data for each of the components
        corrected = np.empty_like(self.data)
        corrected[:] = self.data
        for c in self.components:
            corrected = c.corrected_measurement(corrected)
        return(corrected[:,1])
    
    def limit(self):
        if self.limit_data:
            return(self.limit_data)
        return(self.lim.limit_func(self.freq()))
    
    def add_trace(self,trace):
        self.data = np.empty_like(trace)
        self.data[:] = trace
        
    def add_component(self,comp):
        self.components.append(comp)
    
    def add_limit(self,limit):
        self.lim = limit
    
    def save_to_csv(self,filename):
        with open(filename, 'w', newline='') as csvfile:
            w = csv.writer(csvfile, delimiter=',')
            w.writerow([self.title])
            # Write the DSA configuration
            w.writerow(self.config.get_json_names())
            w.writerow(self.config.get_json_values())
            # Write the DSA and corrected readings
            headings = ['Frequency (Hz)','DSA']
            columns = [self.freq(),self.measured()]
            # Add all component data
            for c in self.components:
                headings.append(c.name)
                columns.append(c.get_factors(self.freq()))
            # Add the corrected measurement
            if len(self.components) > 0:
                headings.append('Corrected')
                columns.append(self.corrected())
            # Add the limit
            if self.lim:
                headings.append('Limit')
                columns.append(self.limit())
            # Write the data
            w.writerow(headings)
            w.writerows(np.array(columns).T)
        
    def load_csv(self,filename):
        with open(filename) as csvfile:
            r = csv.reader(csvfile)
            # Title
            self.title = next(r)[0]
            # DSA config
            config_keys = next(r)
            config_values = next(r)
            self.config = rigol.dsa800.dsa800_config(config_keys,config_values)
            # Data
            headings = next(r)
            self.data = np.array(list(r),dtype=np.float)
            # Get the corrected data and limit
            heading_index = dict((v,i) for i,v in enumerate(headings))
            self.corrected_data = self.data[:,heading_index['Corrected']]
            self.limit_data = self.data[:,heading_index['Limit']]
        
    def save_to_png(self,filename):
        # Add .png extension to filename if needed
        if filename.endswith('.png') == False:
            filename = '%s.png' % filename
        # Plot the data to image file
        fig = plt.figure()
        if len(self.components) > 0:
            plt.plot(self.freq(),self.corrected(),'-b',label='Measured')
        else:
            plt.plot(self.freq(),self.measured(),'-b',label='Trace')
        if self.lim:
            plt.plot(self.freq(),self.limit(),'-r',label='Limit')
        plt.legend(loc='lower right')
        fig.suptitle(self.title, fontsize=18)
        plt.xlabel('Frequency (Hz)', fontsize=12)
        plt.ylabel('Power (%s)' % self.config.param['units'], fontsize=12)
        ax = fig.gca()
        ymin, ymax = ax.yaxis.get_data_interval()
        ax.set_ylim([np.floor(ymin/5)*5,np.ceil(ymax/5)*5])
        plt.grid()
        fig.savefig(filename, dpi=900)
        plt.clf()
        plt.close(fig)
        
        

if __name__ == '__main__':
    pass