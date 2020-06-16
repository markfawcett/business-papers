#!/usr/local/bin/python3

# next to lines are required for GUI file pickers
from tkinter import *
from tkinter import ttk, filedialog

# this is the brains of the operation
import Python_Resources.TransformQuestionsXML_cmd

# working with paths
import os.path

# class for the GUI app
class EBApp:
    def __init__(self, master):

        # input file path
        self.input_file_path     = StringVar()

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
        self.input_file_button = ttk.Button(self.frame_top, text="Input XML File", width=20, command=self.get_input_file)
        self.input_file_button.grid(row=0, column=0, stick='w', padx=10, pady=3)

        self.run_TransformQuestionsXML_button = ttk.Button(self.frame_top, text="Run", width=12, command=self.run_TransformQuestionsXML)
        self.run_TransformQuestionsXML_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)


    def run_TransformQuestionsXML(self):

        infilename     = self.input_file_path.get()

        # run functions
        Python_Resources.TransformQuestionsXML_cmd.transform_xml(infilename)

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
