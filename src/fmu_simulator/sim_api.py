from bottle import request, route, run, response

import os.path
import json
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ''))


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def write_time_step(t_step, filename):
    with open(filename, 'w') as f:
        f.write(t_step)


# receive timestep value for new inputs. database queried using timestep to retrieve correct input
@route('/model_input', method='POST')
def get_input():
    temp = json.loads(request.json)
    req_data = json.dumps({"initialize": False, "input_data": temp['data']['input_data']})
    os.system("python sim_worker.py '{}'".format(req_data))


# receive FMU file from generator. Saving the FMU triggers the simulation_process
@route('/receive_fmu/<model_name>', method='POST')
def receive_fmu(model_name):
    upload = request.files
    save_path = '/home/deb/code/fmu_data/' + model_name

    try:
        os.mkdir(save_path)
    except (IOError, OSError) as error:
        if error == IOError:
            print("Error {0} encountered file already exists".format(error))
        else:
            print("Error {0} encountered problem saving file".format(error))
    else:
        print("Successfully created the directory %s " % save_path)

    for name, file in upload.iteritems():
        print("Saving: " + name)
        try:
            file.save(save_path)
        except IOError as error:  # need way to trigger sim process without creating new folder/file
            print("Error saving FMU:\n{}".format(error))

    json_data = request.forms.pop('json')

    os.system("python sim_worker.py '{}'".format(json_data))
    response.status = 200
    return 'File upload success in sim container for model_name = {0}'.format(model_name)


run(host='0.0.0.0', port=8000, debug=True, reloader=True)
