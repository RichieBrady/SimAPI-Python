import celeryconfig

from celery import Celery
import os.path
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), '../simapi_simulation'))

from energy_plus_to_fmu import RunEnergyPlusToFMU

app = Celery('generator_tasks')
app.config_from_object(celeryconfig)


@app.task
def gen_fmu(idf, epw, directory):
    energy_plus = RunEnergyPlusToFMU(idf=idf, epw=epw, directory=directory)
    result = energy_plus.run()

    return result
