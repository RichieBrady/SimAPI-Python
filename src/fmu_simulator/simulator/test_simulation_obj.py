import os.path
import sys
from simulator.simulation_obj import SimulationObject
from pyfmi.fmi import load_fmu

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

""" Simple test script to. Tests functionality of the simulation_obj class"""

model = load_fmu('brandon.fmu', log_level=4)

final_time = 60*60*24
print("INIT")
model.initialize(0, final_time)
print("After INIT")
print(list(model.get_model_variables(causality=1)))
print(list(model.get_model_variables(type=0)))
print(list(model.get_model_variables(type=1)))


# # instantiate simulation obj with default values
# sim_obj = SimulationObject(model_name='TEST_MODEL1.fmu', step_size=900, final_time=24.0, path_to_fmu='TEST_MODEL1.fmu')
# sim_obj.model_init()  # initialize fmu model. Calls pyFMI model.init() and sets start and finish time
# # new dictionary with inputs for fmu time step
#
# i = 0
# Tset = 23.0
#
# while i < 86400:
#     input_dict = {'time_step': i, 'TSet': Tset}
#     output = sim_obj.do_time_step(input_dict)
#     print("output -> " + str(output['output_json']) + "\n")
#     i += 900
#
# print("FINISHED")
