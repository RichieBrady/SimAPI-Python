from simapi import SimApi

model_name = ""
model_count = 1
step_size = 900
final_time = 24
idf_path = ""
epw_path = ""
csv = [""]

sim = SimApi(
    model_name=model_name,
    model_count=model_count,
    step_size=step_size,
    final_time=final_time,
    idf_path=idf_path,
    epw_path=epw_path,
    csv=csv
)

# TODO add check for existing user
# TODO add endpoint to clear and reset system
sim.create_user()
sim.login()

print("Generating FMU...")
generate_resp = sim.send_and_generate()
print("Generate response: {}".format(generate_resp))

if generate_resp == 201:
    print("Initializing...")
    init_resp = sim.send_and_init()
else:
    print("Something went wrong while generating the fmu! Below is the response.")
    print(generate_resp)
    exit(-1)

print("After init")
if init_resp == 200:
    simulate_resp = sim.simulate_models()
else:
    print("Something went wrong while initializing the fmu! Below is the response.")
    print(init_resp)
    exit(-1)
