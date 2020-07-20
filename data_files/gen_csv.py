import csv
import random


def populate_test_csv():
    f = open('test.csv', 'w')

    with f:
        input_fields = ['time_step', 'PlantOnSched', 'HeatingSetpointSchedule']
        temp_change = [1, -1]
        plant_on_sched_last = 52
        heating_setpoint_schedule_last = 20

        writer = csv.DictWriter(f, fieldnames=input_fields)
        writer.writeheader()
        j = 0
        for i in range(35040):
            k = random.randint(0, 1)
            l = random.randint(0, 1)
            a = temp_change[k]
            b = temp_change[l]

            if (10 < (plant_on_sched_last + a) < 55) and (10 < (heating_setpoint_schedule_last + b) < 55):
                plant_on_sched_last += temp_change[k]
                heating_setpoint_schedule_last += temp_change[l]

            writer.writerow({'time_step': j,
                             'PlantOnSched': plant_on_sched_last,
                             'HeatingSetpointSchedule': heating_setpoint_schedule_last})

            j += 900

    f.close()


def populate_new_csv():
    f = open('TEST_MODEL_one_year.csv', 'w')

    with f:
        input_fields = ['time_step', 'Tset']
        temp_change = [1, -1]
        q = 23

        writer = csv.DictWriter(f, fieldnames=input_fields)
        writer.writeheader()
        j = 0
        for i in range(35040):
            k = random.randint(0, 1)
            a = temp_change[k]

            if -6 < (q + a) < 53:
                q += temp_change[k]

            writer.writerow({'time_step': j, 'Tset': q})

            j += 900
    f.close()


populate_new_csv()
