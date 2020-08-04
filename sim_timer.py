import csv
import time


class SimTimer:
    # TODO add "static" list to store each test time then write to csv
    _all_times = []

    def __init__(self):
        self._start_time = 0.0
        self._end_time = 0.

    def capture_start_time(self):
        self._start_time = time.perf_counter()

    def capture_end_time(self):
        self._end_time = time.perf_counter()

    def calc_runtime(self, stage_name):
        self._all_times.append({"stage_name": stage_name, "stage_time": f"{(self._end_time - self._start_time):0.4f}"})
        print(f"{stage_name} Time: {(self._end_time - self._start_time):0.4f}")

    def write_times(self):
        # TODO write times to csv
        try:
            csv_columns = ['stage_name', 'stage_time']
            with open('simulation_time.csv', 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for data in self._all_times:
                    writer.writerow(data)
        except IOError:
            print("I/O error")

