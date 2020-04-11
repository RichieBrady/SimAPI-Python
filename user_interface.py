import json
from tkinter import *
from tkinter import filedialog
from tkinter import scrolledtext
import threading
import polling2
import requests

from setup import Setup
from user_interface_controller import Controller


class UserInterface:
    controller = Controller()
    setup_user = Setup()

    font = "Arial"

    main_window = None
    idf_path = None
    epw_path = None

    # model name label and input box
    name_label = None
    name_txt = None

    # model count label and input box
    m_count_label = None
    m_count_text = None

    # time step label and input box
    t_step_label = None
    t_step_text = None

    # final time label and input box
    f_time_label = None
    f_time_text = None

    text_area = None

    def get_idf(self):
        self.idf_path = filedialog.askopenfilename()

    def get_epw(self):
        self.epw_path = filedialog.askopenfilename()

    def validate_model_parameters(self):
        self.text_area.config(state=NORMAL)
        self.text_area.delete(1.0, END)
        try:
            int(self.m_count_text.get())
            self.text_area.insert(END, "Model Count field is ok\n")
        except ValueError:
            self.text_area.insert(END, "Model Count field is not integer\n")

        try:
            int(self.t_step_text.get())
            self.text_area.insert(END, "Time Step field is ok\n")
        except ValueError:
            self.text_area.insert(END, "Time Step field is not integer\n")

        try:
            float(self.f_time_text.get())
            self.text_area.insert(END, "Final Time field is ok\n")
        except ValueError:
            self.text_area.insert(END, "Final Time field is not float\n")

        if self.name_txt.get() is None:
            self.text_area.insert(END, "Model Name not filled!\n")
        else:
            self.text_area.insert(END, "Model Name field is ok\n")

        if self.idf_path is not None:
            if self.idf_path.endswith('.idf'):
                self.text_area.insert(END, "idf path is ok\n")
                self.text_area.insert(END, self.idf_path + "\n")
        else:
            self.text_area.insert(END, "idf path is not set or path does not end with .idf\n")

        if self.epw_path is not None:
            if self.epw_path.endswith('.epw'):
                self.text_area.insert(END, "epw path is ok\n")
                self.text_area.insert(END, self.epw_path + "\n")
        else:
            self.text_area.insert(END, "epw path is not set or path does not end with .epw\n")

        self.text_area.config(state=DISABLED)

    def gen_fmu(self):
        gen_status = self.controller.send_and_generate(
            self.name_txt.get(),
            self.m_count_text.get(),
            self.idf_path,
            self.epw_path
        )
        self.text_area.config(state=NORMAL)
        self.text_area.delete('1.0', END)
        if gen_status == 201:
            self.text_area.insert(END, "FMU generated successfully. Initialize button now active\n")
        else:
            self.text_area.insert(END, "Something went wrong generating the FMU\n")

        self.text_area.config(state=DISABLED)
        # TODO if 200 activate next button

    def init_models(self):
        init_status = self.controller.send_and_init(
            self.name_txt.get(),
            self.m_count_text.get(),
        )
        self.text_area.config(state=NORMAL)
        self.text_area.delete('1.0', END)
        if init_status == 200:
            self.text_area.insert(END, "Model(s) initialized successfully. Simulate button now active\n")
        else:
            self.text_area.insert(END, "Something went wrong initializing the FMU\n")

        self.text_area.config(state=DISABLED)

    def run_gen(self):
        threading.Thread(target=self.gen_fmu).start()

    def run_init(self):
        threading.Thread(target=self.init_models).start()

    def run_sim(self, name, count):
        threading.Thread(target=self.simulate_models, args=(name, count)).start()

    def init_window(self):
        self.main_window = Tk()
        self.main_window.config(bg='#37474F')

        self.main_window.title("SimAPI GUI")

        self.main_window.geometry('768x708')

    def init_widgets(self):
        text_frame = Frame(self.main_window)
        self.main_window.grid_columnconfigure(0, weight=1)
        self.main_window.grid_rowconfigure(0, weight=1)
        text_frame.grid(row=0, column=0, padx=5, pady=5, sticky='NEWS')
        self.text_area = scrolledtext.ScrolledText(text_frame)
        self.text_area.pack(fill=BOTH, expand=True)
        self.text_area.config(border=2, relief='sunken', font=(self.font, 10), bg='#d3d3d3')

        input_frame = Frame(self.main_window, bg='#37474F')
        input_frame.grid(row=1, sticky='S')
        self.name_label = Label(input_frame, relief='raised', text="Model Name: ", font=(self.font, 10, "bold"))
        self.name_label.grid(column=0, row=0, padx=5, pady=5)
        self.name_txt = Entry(input_frame, width=13)
        self.name_txt.grid(column=1, row=0, padx=1, pady=5)

        self.m_count_label = Label(input_frame, relief='raised', text="Model Count: ", font=(self.font, 10, "bold"))
        self.m_count_label.grid(column=0, row=1, padx=5, pady=5)
        self.m_count_text = Entry(input_frame, width=13)
        self.m_count_text.grid(column=1, row=1, padx=1, pady=5)

        self.t_step_label = Label(input_frame, relief='raised', text="Step Size: ", font=(self.font, 10, "bold"))
        self.t_step_label.grid(column=2, row=0, padx=5, pady=5)
        self.t_step_text = Entry(input_frame, width=13)
        self.t_step_text.grid(column=3, row=0, padx=1, pady=5)

        self.f_time_label = Label(input_frame, relief='raised', text="Final Time: ", font=(self.font, 10, "bold"))
        self.f_time_label.grid(column=2, row=1, padx=5, pady=5)
        self.f_time_text = Entry(input_frame, width=13)
        self.f_time_text.grid(column=3, row=1, padx=1, pady=5)

        upload_idf = Button(input_frame, relief='raised', text="upload idf", font=(self.font, 10, "bold"),
                            command=lambda: self.get_idf())
        upload_idf.grid(column=4, row=0, padx=5, pady=5)

        upload_epw = Button(input_frame, relief='raised', text="upload epw", font=(self.font, 10, "bold"),
                            command=lambda: self.get_epw())
        upload_epw.grid(column=4, row=1, padx=5, pady=5)

        button_frame = Frame(self.main_window, bg='#37474F')
        button_frame.grid(row=2, sticky='S')

        test_entry_fields = Button(button_frame, text="Validate Input", font=(self.font, 10, "bold"),
                                   command=lambda: self.validate_model_parameters())
        test_entry_fields.grid(column=0, row=5, padx=5, pady=5)

        generate_fmu = Button(button_frame, text="Generate", font=(self.font, 10, "bold"),
                              command=lambda: self.run_gen())
        generate_fmu.grid(column=1, row=5, padx=5, pady=5)

        generate_fmu = Button(button_frame, text="Initialize", font=(self.font, 10, "bold"),
                              command=lambda: self.run_init())
        generate_fmu.grid(column=2, row=5, padx=5, pady=5)

        generate_fmu = Button(button_frame, text="Simulate", font=(self.font, 10, "bold"),
                              command=lambda: self.run_sim(
                                  self.name_txt.get(),
                                  int(self.m_count_text.get())))

        generate_fmu.grid(column=3, row=5, padx=5, pady=5)

    def simulate_models(self, initial_model_name, model_count):
        def test_method(query, url):
            resp = requests.get(url=url, json={'query': query})
            json_data = resp.json()['data']['outputs']

            return len(json_data)

        header = self.setup_user.login()

        # query for all models in db related to initial_model_name.
        model_query = """
                   {{
                       fmuModels(modelN: "{0}"){{
                            modelName
                        }}
                   }}
                   """.format(initial_model_name)

        r = requests.get(url=self.setup_user.graphql_url, json={'query': model_query})

        i = 0
        sim_names = []

        while i < model_count:
            name = r.json()['data']['fmuModels'][i]['modelName']  # extract model name from graphql query response
            print(name)
            sim_names.append(name)  # store extracted model names.
            i += 1

        shade = 1.0  # input value. Stays same on each iteration.

        self.text_area.config(state=NORMAL)
        self.text_area.delete('1.0', END)
        i = 0  # first step
        # run 24 hour (86400sec) simulation at 10 minute (600sec) time steps
        while i < 86400:  # outer loop iterates over time steps

            j = 0
            while j < model_count:
                input_dict = {'time_step': i, 'yShadeFMU': shade}  # input is user defined, can be any number of inputs

                input_data = {
                    'fmu_model': sim_names[j],
                    'time_step': i,
                    'input_json': json.dumps(input_dict)
                }

                r = requests.post(self.setup_user.input_url, headers=header, data=input_data)
                print(r.text + ' ' + str(r.status_code))

                output_query = """
                {{
                    outputs(modelN: "{0}", tStep: {1}) {{
                        outputJson
                    }}
                }}
                """.format(sim_names[j], i)

                # move outside loop and poll once for len() = n, where n is number of simulations!
                polling2.poll(
                    lambda: test_method(query=output_query, url=self.setup_user.graphql_url) == 1,
                    step=0.1,
                    poll_forever=True)

                json_output = \
                    requests.get(url=self.setup_user.graphql_url, json={'query': output_query}).json()['data'][
                        'outputs']

                test = json.loads(json_output[0]['outputJson'])
                self.text_area.insert(END, "Output: " + str(test) + "\n")
                j += 1

            i += 600

        self.text_area.insert(END, "\nSimulation(s) finished!\n")
        self.text_area.config(state=DISABLED)
        return 200

    def run(self):
        self.init_window()
        self.init_widgets()
        self.main_window.mainloop()
