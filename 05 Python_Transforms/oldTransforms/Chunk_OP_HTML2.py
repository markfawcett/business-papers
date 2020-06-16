#!/usr/local/bin/python3

# next to lines are required for GUI file pickers
import tkinter as tk
from tkinter import ttk, filedialog

# this is the brains of the operation
# import Python_Resources.html_chunk_tool_cmd as cmd_version
import Python_Resources.html_chunk_tool_cmd_with_class_warning as cmd_version

# working with paths
import os.path


# class for the GUI app
class OPApp:
    def __init__(self, master):

        # input file path
        self.input_file_path = tk.StringVar()
        # template file path
        self.template_file_path = tk.StringVar()
        # EB number
        self.EB_number = tk.StringVar()
        # dates should be of the form YYYYMMDD
        self.sitting_date  = tk.StringVar()
        self.creation_date = tk.StringVar()

        # add title to the window
        master.title("OP HTML")

        # make background frame
        self.frame_background = ttk.Frame(master)
        self.frame_background.pack(fill=tk.BOTH, expand=tk.TRUE)

        # make frames
        self.frame_top = ttk.LabelFrame(self.frame_background, text='Input')
        self.frame_top.pack(padx=10, pady=10, fill=tk.BOTH, expand=tk.TRUE)

        self.frame_top.columnconfigure(0, weight=1)
        self.frame_top.columnconfigure(1, weight=1)

        # Buttons
        input_file_button = ttk.Button(self.frame_top, text="Input HTML File", width=20, command=self.get_input_file)
        input_file_button.grid(row=0, column=0, stick='w', padx=10, pady=3)

        template_html_button = ttk.Button(self.frame_top, text="Template HTML", width=20, command=self.get_template_file)
        template_html_button.grid(row=1, column=0, stick='w', padx=10, pady=3)

        # EB text entry lable
        EB_box_lable = ttk.Label(self.frame_top, text='OP Number:  ')
        EB_box_lable.grid(row=4, column=0, stick='w', pady=3)
        # EB text entry box
        EB_box = ttk.Entry(self.frame_top, textvariable=self.EB_number, width=4)
        EB_box.grid(row=4, column=1, stick='w', pady=3)

        # Creation date lable
        Creation_box_lable = ttk.Label(self.frame_top, text='Creation Date\t(e.g. 2016-09-11):  ')
        Creation_box_lable.grid(row=5, column=0, stick='w', pady=3)
        # Creation date box
        Creation_box = ttk.Entry(self.frame_top, textvariable=self.creation_date, width=9)
        Creation_box.grid(row=5, column=1, stick='w', pady=3)

        # Sitting date lable
        Sitting_box_lable = ttk.Label(self.frame_top, text='Sitting Date\t(e.g. 2016-09-12):  ')
        Sitting_box_lable.grid(row=6, column=0, stick='w', pady=3)
        # Sitting date box
        Sitting_box = ttk.Entry(self.frame_top, textvariable=self.sitting_date, width=9)
        Sitting_box.grid(row=6, column=1, stick='w', pady=3)

        run_OP_tool_button = ttk.Button(self.frame_top, text="Run", width=12, command=self.run_OP_tool)
        run_OP_tool_button.grid(row=7, column=0, columnspan=3, padx=10, pady=10)


    def run_OP_tool(self):

        infilename     = self.input_file_path.get()
        templatefile   = self.template_file_path.get()
        sitting_date   = self.sitting_date.get()
        creation_date  = self.creation_date.get()
        op_number      = self.EB_number.get()

        # run functions
        cmd_version.DATES.set_up(creation_date, sitting_date)  # date should be of the form DDMMYYYY
        input_root = cmd_version.massarge_input_file(infilename)
        cmd_version.split_and_output(input_root, templatefile, infilename)

        self.print_to_user('\nAll Done!')


    def get_input_file(self):
        directory = filedialog.askopenfilename()
        self.input_file_path.set(directory)
        self.print_to_user('Input file is at:  ' + self.input_file_path.get())

    def get_template_file(self):
        directory = filedialog.askopenfilename()
        self.template_file_path.set(directory)
        self.print_to_user('Template file is at: ' + self.template_file_path.get())

    def print_to_user(self, string):
        print(string)


def main():
    # try and fix blury text on windows
    if os.name == "nt":
        from ctypes import windll
        try:
            windll.shcore.SetProcessDpiAwareness(1)
            kernel32 = windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass  # don't do anything

    run_OP_toolapp = tk.Tk()
    OPApp(run_OP_toolapp)
    run_OP_toolapp.mainloop()


if __name__ == "__main__": main()
