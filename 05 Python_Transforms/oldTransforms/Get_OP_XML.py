#!/usr/local/bin/python3

# next to lines are required for GUI file pickers
from tkinter import *
from tkinter import ttk, filedialog

# this is the brains of the part 1 operation
import Python_Resources.get_part1_xml_cmd
# this is the brains of the fba operation
import Python_Resources.get_fba_xml_cmd

# working with paths
import os.path

# for geting tomorows date
import datetime

# class for the GUI app
class EBApp:
    def __init__(self, master):

        # input file path
        self.input_url     = StringVar()
        # template file path

        # Date of OP we want to produce
        self.sitting_date  = StringVar()


        # add title to the window
        master.title("Create OP XML from VnP XML")

        # make background frame
        self.frame_background = ttk.Frame(master)
        self.frame_background.pack(fill=BOTH, expand=TRUE)

        # make frames
        self.frame_top = ttk.LabelFrame(self.frame_background, text='Input')
        self.frame_top.pack(padx=10, pady=10, fill=BOTH, expand=TRUE)

        # self.frame_top.columnconfigure(0, weight=1)
        # self.frame_top.columnconfigure(1, weight=1)

        # url text entry lable
        self.EB_box_lable = ttk.Label(self.frame_top, text='File URL:  ')
        self.EB_box_lable.grid(row=1, column=0, stick='sw', pady=3)
        # url text entry box
        self.EB_box = ttk.Entry(self.frame_top, textvariable=self.input_url, width=40)
        self.EB_box.grid(row=2, column=0, stick='w', pady=10)
        self.EB_box.insert(0, 'http://services.orderpaper.parliament.uk/businessitems/tableditemswithdate.xml?key=e16ca3cd-8645-4076-aaba-3f1f31028da1&fromDate={date}&toDate={date}&type=effectives')

        # OP date lable
        self.Creation_box_lable = ttk.Label(self.frame_top, text='Effective OP date\t(e.g. 2016-09-11):  ')
        self.Creation_box_lable.grid(row=3, column=0, stick='sw', pady=10)
        # OP date box
        self.Creation_box = ttk.Entry(self.frame_top, textvariable=self.sitting_date, width=10)
        self.Creation_box.grid(row=4, column=0, stick='w', pady=3)
        self.Creation_box.insert(0, get_tomorow_date())

        # Part 1 button
        self.part1_button = ttk.Button(self.frame_top, text="Get Part 1 XML", width=20, command=self.run_part1_comand_line_script)
        self.part1_button.grid(row=7, column=0, columnspan=3, padx=10, pady=10)
        # FBA button
        self.FBA_button = ttk.Button(self.frame_top, text="Get FBA XML", width=20, command=self.run_FBA_comand_line_script)
        self.FBA_button.grid(row=8, column=0, columnspan=3, padx=10, pady=10)


    def run_part1_comand_line_script(self):

        url     = self.input_url.get()
        op_date = self.sitting_date.get()

        Python_Resources.get_part1_xml_cmd.process_xml(url, op_date)

    def run_FBA_comand_line_script(self):

        url     = self.input_url.get()
        op_date = self.sitting_date.get()

        Python_Resources.get_fba_xml_cmd.process_xml(url, op_date)


def get_tomorow_date():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return tomorrow.strftime('%Y-%m-%d')




def main():
    run_toolapp = Tk()
    app = EBApp(run_toolapp)
    run_toolapp.mainloop()

if __name__ == "__main__": main()