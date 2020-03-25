from bottle import request, route, run, response

import os.path
import json
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def write_json(data, filename):
    # TODO already json at this point no need to dump
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def write_time_step(t_step, filename):
    # TODO already json at this point no need to dump
    with open(filename, 'w') as f:
        f.seek(0)
        f.write(t_step)


@route('/model_input', method='POST')
def get_input():
    data = json.loads(request.json)
    t_step = data['time_step']
    write_time_step(t_step, '/home/deb/code/store_incoming_json/time_step.txt')
    # TODO return code


@route('/upload/<model_name>', method='POST')
def do_upload(model_name):
    upload = request.files
    save_path = '/home/deb/code/volume/' + model_name

    json_data = request.forms.pop('json')
    print("IN SIM UPLOAD TEST JSON " + json_data)
    try:
        os.mkdir(save_path)
    except OSError:
        print("Creation of the directory %s failed" % save_path)
    else:
        print("Successfully created the directory %s " % save_path)

    for name, file in upload.iteritems():
        file.save(save_path)

    if len(upload) == 2:
        j_dict = {'model_params': []}

        j_dict['model_params'].append(json.loads(json_data))
        write_json(j_dict, save_path + '/model_params.json')
        response.status = 200
        return 'File upload success in sim container for model_name = {0}'.format(model_name)
    else:
        response.status = 400
        return 'Number of Files required = 2. Uploaded Files = {0}'.format(len(upload))


run(host='0.0.0.0', port=8000, debug=True, reloader=True)
