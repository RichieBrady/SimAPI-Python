import os


class RunEnergyPlusToFMU:

    def __init__(self, idf='_fmu-export-variable.idf', epw='USA.epw', directory='/home/fmu/code/energy/test'):
        self.idf = idf
        self.epw = epw
        self.directory = directory

    def run(self):

        eplus_command = "cd " + self.directory + " && \
                      python /home/fmu/code/energy/Scripts/EnergyPlusToFMU.py -d -i  /home/fmu/code/Energy+.idd \
                      -w " + self.epw + " " + self.idf + " && ./idf-to-fmu-export-prep-linux \
                      /home/fmu/code/Energy+.idd " + self.idf

        os.system(eplus_command)
        return 'success'

