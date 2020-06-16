#!/usr/local/bin/python3

# next to lines are required for GUI file pickers
from tkinter import *
from tkinter import ttk, filedialog

# this is the brains of the operation
import Python_Resources.CreateEMsForHansard_cmd as cmd_vsn

# working with paths
import os.path

# class for the GUI app
class EBApp:
    def __init__(self, master):

        # input file path
        self.input_file_path = StringVar()
        # dates should be of the form YYYYMMDD
        self.sitting_date    = StringVar()

        # add title to the window
        master.title("Transform Questions")

        # make background frame
        self.frame_background = ttk.Frame(master)
        self.frame_background.pack(fill=BOTH, expand=TRUE)

        # make frames
        self.frame_top = ttk.LabelFrame(self.frame_background, text='Input')
        self.frame_top.pack(padx=10, pady=10, fill=BOTH, expand=TRUE)

        self.frame_top.columnconfigure(0, weight=1)
        self.frame_top.columnconfigure(1, weight=1)

        # Buttons
        self.input_file_button = ttk.Button(self.frame_top, text="Input HTML File", width=20, command=self.get_input_file)
        self.input_file_button.grid(row=0, column=0, stick='w', padx=10, pady=3)

        # Sitting date lable
        self.Sitting_box_lable = ttk.Label(self.frame_top, text='Sitting Date\t(e.g. 2017-09-12):  ')
        self.Sitting_box_lable.grid(row=1, column=0, stick='w', pady=3)
        # Sitting date box
        self.Sitting_box = ttk.Entry(self.frame_top, textvariable=self.sitting_date, width=11)
        self.Sitting_box.grid(row=1, column=1, stick='w', pady=3)

        self.run_TransformQuestionsXML_button = ttk.Button(self.frame_top, text="Run", width=12, command=self.run_TransformQuestionsXML)
        self.run_TransformQuestionsXML_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)


    def run_TransformQuestionsXML(self):

        infilename     = self.input_file_path.get()
        sittingdate    = self.sitting_date.get()

        # run functions
        cmd_vsn.split_and_output(infilename, sittingdate)

        print('\nAll Done!')


    def get_input_file(self):
        directory = filedialog.askopenfilename()
        self.input_file_path.set(directory)
        print('Input file is at:  ' + self.input_file_path.get())


def main():
    run_TransformQuestionsXMLapp = Tk()
    app = EBApp(run_TransformQuestionsXMLapp)
    run_TransformQuestionsXMLapp.mainloop()

if __name__ == "__main__": main()
