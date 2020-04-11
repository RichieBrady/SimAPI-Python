import time

from bottle import request, route, run, response

import os.path
import json
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def write_time_step(t_step, filename):
    with open(filename, 'w') as f:
        f.seek(0)
        f.write(t_step)


@route('/model_input', method='POST')
def get_input():
    print("RECEIVED INPUT: " + str(request.json))
    data = json.loads(request.json)
    t_step = data['time_step']
    write_time_step(t_step, '/home/deb/code/fmu_data/time_step.txt')


@route('/receive_fmu/<model_name>', method='POST')
def receive_fmu(model_name):
    upload = request.files
    save_path = '/home/deb/code/fmu_data/' + model_name

    try:
        os.mkdir(save_path)
    except OSError:
        print("Creation of the directory %s failed" % save_path)
    else:
        print("Successfully created the directory %s " % save_path)

    json_data = request.forms.pop('json')
    j_dict = {'model_params': []}

    j_dict['model_params'].append(json.loads(json_data))
    write_json(j_dict, save_path + '/model_params.json')
    print("JSON_DATA RECEIVE: " + str(json_data))

    time.sleep(1)

    for name, file in upload.iteritems():
        print("Saving: " + name)
        file.save(save_path)

    response.status = 200
    return 'File upload success in sim container for model_name = {0}'.format(model_name)


run(host='0.0.0.0', port=8000, debug=True, reloader=True)
