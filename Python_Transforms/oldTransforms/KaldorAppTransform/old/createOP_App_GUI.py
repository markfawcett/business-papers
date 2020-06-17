#!/usr/local/bin/python3

# next to lines are required for GUI file pickers
from tkinter import ttk, filedialog, Tk, StringVar, BOTH, TRUE

# this is the brains of the operation
import Python_Resources.createOP_App4 as cmd_vsn


# class for the GUI app
class OPApp:
    def __init__(self, master):

        # input file path
        self.input_file_path  = StringVar()
        # folder path
        self.temp_folder_path = StringVar()
        # OP number
        self.OP_number        = StringVar()
        # dates should be of the form YYYYMMDD
        self.sitting_date     = StringVar()


        # add title to the window
        master.title("Make OP App")

        # make background frame
        self.frame_background = ttk.Frame(master)
        self.frame_background.pack(fill=BOTH, expand=TRUE)

        # make frames
        self.frame = ttk.LabelFrame(self.frame_background, text='Input')
        self.frame.pack(padx=10, pady=10, fill=BOTH, expand=TRUE)

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        # Buttons
        self.input_file_button = ttk.Button(self.frame, text="Input HTML File", width=20, command=self.get_input_file)
        self.input_file_button.grid(row=0, column=0, stick='w', padx=10, pady=3)
        self.temp_folder_button = ttk.Button(self.frame, text="app_templates Folder", width=20, command=self.get_temp_folder)
        self.temp_folder_button.grid(row=1, column=0, stick='w', padx=10, pady=3)


        # EB text entry lable
        self.EB_box_lable = ttk.Label(self.frame, text='OP Number:  ')
        self.EB_box_lable.grid(row=2, column=0, stick='w', pady=3)
        # EB text entry box
        self.EB_box = ttk.Entry(self.frame, textvariable=self.OP_number, width=4)
        self.EB_box.grid(row=2, column=1, stick='w', pady=3)

        # Sitting date lable
        self.Sitting_box_lable = ttk.Label(self.frame, text='Sitting Date\t(e.g. 2016-09-12):  ')
        self.Sitting_box_lable.grid(row=3, column=0, stick='w', pady=3)
        # Sitting date box
        self.Sitting_box = ttk.Entry(self.frame, textvariable=self.sitting_date, width=9)
        self.Sitting_box.grid(row=3, column=1, stick='w', pady=3)

        self.run_OP_tool_button = ttk.Button(self.frame, text="Run", width=12, command=self.run_OP_tool)
        self.run_OP_tool_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10)


    def run_OP_tool(self):

        infilename   = self.input_file_path.get()
        temp_folder  = self.temp_folder_path.get()
        sitting_date = self.sitting_date.get()
        op_number    = self.OP_number.get()

        # run functions
        cmd_vsn.create_app(infilename, temp_folder, sitting_date, op_number)

        print('\nAll Done!')
        input('Press any Key to exit')
        exit()


    def get_input_file(self):
        directory = filedialog.askopenfilename()
        self.input_file_path.set(directory)
        print('Input file is at:  ' + self.input_file_path.get())


    def get_temp_folder(self):
        directory = filedialog.askdirectory()
        self.temp_folder_path.set(directory)
        print('App Template folder is at:  ' + self.temp_folder_path.get())


def main():
    run_OP_toolapp = Tk()
    OPApp(run_OP_toolapp)
    run_OP_toolapp.mainloop()


if __name__ == "__main__": main()
