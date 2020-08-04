from simapi import SimApi
from sim_timer import SimTimer

model_name = "test"
model_count = 1
step_size = 900  # TODO change to steps per hour parse on backend
final_time = 24  # TODO convert to dict {'days': , 'months': , 'year': } parse on backend
idf_path = "data_files/new.idf"
epw_path = "data_files/new.epw"
csv = ["data_files/new1.csv"]
timer = SimTimer()

sim = SimApi(
    model_name=model_name,
    model_count=model_count,
    step_size=step_size,
    final_time=final_time,
    idf_path=idf_path,
    epw_path=epw_path,
    csv=csv
)


if not sim.login() == 200:
    sim.create_user()
    sim.login()

print("Generating FMU...")

timer.capture_start_time()

generate_resp = sim.send_and_generate()
print("Generate response: {}".format(generate_resp))

timer.capture_end_time()
timer.calc_runtime("gen_fmu")

if generate_resp == 201:
    print("Initializing...")
    timer.capture_start_time()
    init_resp = sim.send_and_init()
    timer.capture_end_time()
    timer.calc_runtime("init_fmu")
else:
    print("Something went wrong while generating the fmu!")
    print(generate_resp)
    exit(-1)

if init_resp == 200:
    print("Simulating...")
    timer.capture_start_time()
    simulate_resp = sim.simulate_models()
    timer.capture_end_time()
    timer.calc_runtime("sim_fmu")
else:
    print("Something went wrong while initializing the fmu!")
    print(init_resp)
    exit(-1)

timer.capture_start_time()
for name in sim.sim_names:
    print("Sim name: {}".format(name))
    sim.request_model_outputs(name)
    print()

timer.capture_end_time()
timer.calc_runtime("req_outs")
timer.write_times()
