import json
import subprocess
import sys
import requests

from simulator.simulation_obj import SimulationObject


class SimProc:

    def __init__(self, sim_data):
        self.sim_obj = None
        self.model_name = sim_data['model_name']
        self.final_time = sim_data['final_time']
        self.step_size = sim_data['step_size']
        self.is_sim_one = sim_data['isSimOne']
        self.header = {'Authorization': 'Token ' + sim_data['Authorization']}
        self.prev_time_step = 0
        self.kill_proc = False

    # TODO add method that validates parameters

    def initialize(self):
        fmu_path = '/home/deb/code/fmu_data/{0}/{0}.fmu'.format(self.model_name)

        # if the simulation container is not designated as the first container in a swarm
        if not self.is_sim_one:
            # create a new model instance in the django database for this container
            init_url = 'http://web:8000/init_model/'

            hostname = subprocess.getoutput("cat /etc/hostname")
            self.model_name = self.model_name + '_' + hostname

            initial_data = {
                'model_name': self.model_name,  # change name each time script is run!
                'step_size': self.step_size,  # step size in seconds. 600 secs = 10 mins
                'final_time': self.final_time,  # 24 hours = 86400 secs
                'container_id': hostname
            }

            requests.post(init_url, headers=self.header, data=initial_data)

        self.sim_obj = SimulationObject(model_name=self.model_name, step_size=int(self.step_size),
                                        final_time=float(self.final_time),
                                        path_to_fmu=fmu_path)

        self.sim_obj.model_init()

    def process_step(self, step_input):

        print("\ninput: " + str(step_input))

        # run do_step for current time step with current inputs
        output_json = self.sim_obj.do_time_step(step_input)

        output_url = 'http://router:8000/route_output/'

        output_json['Authorization'] = self.header['Authorization']
        r = requests.post(output_url, headers=self.header, json=json.dumps(output_json))

        step_input = json.loads(step_input)
        # when last time step has completed free and terminate instance
        if int(step_input['time_step']) == self.sim_obj.final_time - int(self.step_size):
            self.kill_proc = True


if __name__ == '__main__':
    sim_proc = None
    try:
        while True:
            data = None
            for line in open('proc_pipe'):
                str_json = line.rstrip('\n')
                data = json.loads(str_json)

            if data:
                if not data['initialize']:
                    if sim_proc.kill_proc:
                        break
                    else:
                        sim_proc.process_step(data['input_data'])
                elif data['initialize']:
                    sim_proc = SimProc(data['data'])
                    sim_proc.initialize()
    except KeyboardInterrupt:
        print("ending process!")
        sys.exit(0)

    print("ending process!")
    sys.exit(1)
