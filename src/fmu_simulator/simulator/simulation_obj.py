import os
import sys
import json
import pyfmi

from pyfmi import load_fmu
from pyfmi.fmi import FMUModelCS2
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


""" SimulationObject class represents an FMU model and class methods to access and run the model """


class SimulationObject:

    model: pyfmi.fmi.FMUModelCS1

    def __init__(self,  model_name, step_size=600, final_time=72., path_to_fmu='_fmu_export_variable.fmu'):

        """
            fmu model initialize method. Parameters originate from API.
            step_size: size of each step in seconds 600 = 10 minutes
            final_time: must be multiple of 86400 (a day in seconds) min value is 24.0,
                        converted to seconds by 60*60*final_time
            path_to_fmu: self explanatory
        """
        self.model_name = model_name
        self.step_size = step_size
        self.final_time = 60*60*final_time
        self.model = load_fmu(path_to_fmu, kind='CS')

        # store dict of current model variables. Key is variable name, used in do_time_step()
        self.model_output_vars = list(self.model.get_model_variables(causality=1))
        self.model_real_vars = list(self.model.get_model_variables(type=0))
        self.model_int_vars = list(self.model.get_model_variables(type=1))

    def model_init(self):
        """ Initialize model with start and finish time """
        self.model.initialize(0, self.final_time)

    def do_time_step(self, json_input):
        """
            process current time_step.
            json_input: input values for current time step. Originates from API.
            json_input is converted to dict, values from dict are used to set relevant model inputs.
            calls model.do_step,
            creates new dict with output then returns output dict as json to pass back to API
        """

        time_step = json_input['time_step']
        print("do_time_step json -> " + str(json_input))
        for key in json_input:
            if key in self.model_real_vars:
                self.model.set(key, float(json_input[key]))
            elif key in self.model_int_vars:
                self.model.set(key, int(json_input[key]))

        self.model.do_step(current_t=time_step, step_size=self.step_size, new_step=True)

        do_step_outputs = {'fmu_model': self.model_name, 'time_step': time_step}

        output = {}

        for key in self.model_output_vars:
            output[key] = self.model.get(key)[0]

        do_step_outputs['output_json'] = output

        return do_step_outputs

