import os.path
import sys

from pyfmi.fmi import load_fmu

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

""" Simple test script to. Tests functionality of the simulation_obj class"""


#  instantiate simulation obj with default values
# sim_obj = SimulationObject(model_name='asd.fmu', final_time=24.0, path_to_fmu='asd.fmu')

model = load_fmu('test.fmu', log_level=4)

final_time = 60*60*24

model.initialize(0, final_time)

# sim_obj.model_init()  # initialize fmu model. Calls pyFMI model.init() and sets start and finish time
# new dictionary with inputs for fmu time step


"""
i = 0
shade = 1.0

while i < 86400:
    input_dict = {'time_step': i, 'yShadeFMU': shade}
    output = sim_obj.do_time_step(input_dict)
    print(output)
    i += 600

print("FINISHED")
"""