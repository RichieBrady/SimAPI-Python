import celeryconfig

from celery import Celery

from run_eptf import RunEnergyPlusToFMU

app = Celery('generator_tasks')
app.config_from_object(celeryconfig)

# runs EnergyPlusToFMU command and generates FMU
@app.task
def gen_fmu(idf, epw, directory):
    energy_plus = RunEnergyPlusToFMU(idf=idf, epw=epw, directory=directory)
    result = energy_plus.run()

    return result
