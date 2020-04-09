from tkinter import *

window = Tk()

window.title("Welcome to LikeGeeks app")

window.geometry('1024x768')

name_label = Label(window, text="model name", font=("Bold", 12))
model_count = Label(window, text="model count", font=("Bold", 12))

name_label.grid(column=0, row=0)
model_count.grid(column=1, row=0)

txt = Entry(window, width=13)
txt1 = Entry(window, width=13)

txt.grid(column=0, row=1)
txt1.grid(column=1, row=1)



window.mainloop()
