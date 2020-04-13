import time
from pathlib import Path

import requests
from bottle import request, route, run, response

import json
import os.path
import generator_tasks


@route('/file_upload/<model_name>', method='POST')
def test(model_name):
    upload = request.files
    save_path = '/home/fmu/code/energy/test/' + model_name

    try:
        os.mkdir(save_path)
    except OSError:
        print("Creation of the directory %s failed" % save_path)
    else:
        print("Successfully created the directory %s " % save_path)

    if len(upload) == 2:
        for name, file in upload.iteritems():
            print("Saving: " + name)
            file.save(save_path)
    else:
        response.status = 400
        return "Found {0} files. Expected 2".format(len(upload))

    directory = os.listdir(save_path)
    print(directory)

    if model_name + '.idf' in directory and model_name + '.epw' in directory:
        epw = '/home/fmu/code/energy/test/' + model_name + '/' + model_name + '.epw'
        idf = '/home/fmu/code/energy/test/' + model_name + '/' + model_name + '.idf'
    else:
        response.status = 400
        return 'Error files not saved!'

    fmu_store_dir = '/home/fmu/code/fmu_test/' + model_name

    try:
        os.mkdir(fmu_store_dir)
    except OSError:
        print("Creation of the directory %s failed" % fmu_store_dir)
    else:
        print("Successfully created the directory %s " % fmu_store_dir)

    result = generator_tasks.gen_fmu.apply_async((idf, epw, fmu_store_dir))
    result.get()

    fmu_check = Path('/home/fmu/code/fmu_test/{0}/{0}.fmu'.format(model_name))
    fmu_zip_check = Path('/home/fmu/code/fmu_test/{0}/{0}.zip'.format(model_name))

    if fmu_check.exists():
        message = "FMU FILE EXISTS"
    elif fmu_zip_check.exists():
        message = "FMU ZIP EXISTS"
    else:
        message = "NO FMU OR ZIP"
        return message

    return message


@route('/fmu_to_simulator/<model_name>', method='POST')
def send_fmu(model_name):

    json_data = request.json

    model_count = json_data['model_count']

    i = 1
    while i <= int(model_count):
        if i == 1:
            json_data['isSimOne'] = True
        else:
            json_data['isSimOne'] = False

        fmu_file = open('/home/fmu/code/fmu_test/' + model_name + '/' + model_name + '.fmu', 'rb')
        file = {'fmu': (model_name + '.fmu', fmu_file, 'application/zip'),
                'json': (None, json.dumps(json_data), 'application/json')}

        url = 'http://src_simulator_{0}:8000/receive_fmu/{1}'.format(i, model_name)
        print(url)
        print(json_data)
        # TODO add logic to find out if model init is success, Keep count and pass back to user as response.
        r = requests.post(url, files=file)

        print(r.status_code)
        print(r.text)
        fmu_file.close()
        time.sleep(3)
        i += 1

    response.status = 200
    return 'File upload success in sim container for model_name = {0}'.format(model_name)


run(host='0.0.0.0', port=8000, debug=True, reloader=True)
