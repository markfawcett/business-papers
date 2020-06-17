#!/usr/local/bin/python3

# next to lines are required for GUI file pickers
from tkinter import *
from tkinter import ttk, filedialog
import os

# this is the brains of the part 1 operation
import Python_Resources.get_part1_xml_cmd_v2 as part1_script
# this is the brains of the fba operation
import Python_Resources.get_fba_xml_cmd as fba_script
# this is the brains of the announcements operation
import Python_Resources.get_announcements_xml_cmd_v1 as ann_script

# for getting files form urls
import urllib.request
import ssl


# working with paths
from os import path

# for geting tomorows date
import datetime

# class for the GUI app
class EBApp:
    def __init__(self, master):

        # input file path
        self.folder_path   = StringVar()
        # input file path
        self.input_url     = StringVar()
        # template file path

        # Date of OP we want to produce
        self.sitting_date  = StringVar()


        # add title to the window
        master.title("Create OP XML from VnP XML")

        # create a counter to for the rows for the grid geometry
        rows = Counter()

        # make background frame
        self.frame_background = ttk.Frame(master)
        self.frame_background.pack(fill=BOTH, expand=TRUE)
        # add margin space
        self.inner_background = ttk.Frame(self.frame_background)
        self.inner_background.pack(fill=BOTH, expand=TRUE, padx=5, pady=20)

        # make frames for each step
        self.step_0 = ttk.LabelFrame(self.inner_background, text='Step 0')
        self.step_0.pack(padx=10, pady=5, fill=BOTH, expand=TRUE)
        self.step_1 = ttk.LabelFrame(self.inner_background, text='Step 1')
        self.step_1.pack(padx=10, pady=5, fill=BOTH, expand=TRUE)
        self.step_2 = ttk.LabelFrame(self.inner_background, text='Step 2')
        self.step_2.pack(padx=10, pady=5, fill=BOTH, expand=TRUE)
        self.step_3 = ttk.LabelFrame(self.inner_background, text='Step 3')
        self.step_3.pack(padx=10, pady=5, fill=BOTH, expand=TRUE)


        # url text entry lable
        self.url_box_lable = ttk.Label(self.step_0, text='You should not need to do anything here!\nIf you need to, You can change the base URL.\t(This can be usefull when testing the dev version of the OP portal)')
        self.url_box_lable.config(wraplength=350)
        self.url_box_lable.grid(row=rows.count(), column=0, stick='sw', padx=5, pady=3)
        # url text entry box
        self.url_box = ttk.Entry(self.step_0, textvariable=self.input_url, width=42)
        self.url_box.grid(row=rows.count(), column=0, stick='w', padx=5, pady=10)
        self.url_box.insert(0, 'http://services.orderpaper.parliament.uk/businessitems/tableditemswithdate.xml?key=e16ca3cd-8645-4076-aaba-3f1f31028da1&fromDate={date}&toDate={date}&type=effectives')

        # select folder lable
        self.select_folder_lable = ttk.Label(self.step_1, text='Select the folder that you would like the XML to be saved into. Usually this will be a dated folder on the O drive.')
        self.select_folder_lable.config(wraplength=350)
        self.select_folder_lable.grid(row=rows.count(), column=0, stick='sw', padx=5, pady=3)
        # select folder button
        self.select_folder_button = ttk.Button(self.step_1, text="Select Folder", width=12, command=self.get_folder_for_outputs)
        self.select_folder_button.grid(row=rows.count(), column=0, stick='sw', padx=5, pady=10)


        # OP date lable
        self.Creation_box_lable = ttk.Label(self.step_2, text='Check the effective OP date is correct. The date must be in the form YYYY-MM-DD (e.g. 2016-09-11).')
        self.Creation_box_lable.config(wraplength=350)
        self.Creation_box_lable.grid(row=rows.count(), column=0, stick='sw', padx=5, pady=10)
        # OP date box
        self.Creation_box = ttk.Entry(self.step_2, textvariable=self.sitting_date, width=10)
        self.Creation_box.grid(row=rows.count(), column=0, stick='w', padx=5, pady=3)
        self.Creation_box.insert(0, get_tomorow_date())

        # Get XML buttons
        self.run_lable = ttk.Label(self.step_3, text="Press the buttons below (one at a time) to get the XML for the sections you are interested in. Look for the 'All Done' message in the console window.")
        self.run_lable.config(wraplength=350)
        self.run_lable.grid(row=rows.count(), column=0, stick='sw', padx=5, pady=10)
        # run button
        self.part1_button = ttk.Button(self.step_3, text="Get Part 1 XML", width=26, command=self.run_part1_comand_line_script)
        # self.run_Transform_VnP_XML_button.config()
        self.part1_button.grid(row=rows.count(), column=0, padx=10, pady=10)
        # Announcements Button
        self.FBA_button = ttk.Button(self.step_3, text="Get Announcements XML", width=26, command=self.run_ann_comand_line_script)
        self.FBA_button.grid(row=rows.count(), column=0, padx=10, pady=1)
        # FBA button
        self.FBA_button = ttk.Button(self.step_3, text="Get FBA XML", width=26, command=self.run_FBA_comand_line_script)
        self.FBA_button.grid(row=rows.count(), column=0, padx=10, pady=10)


    def get_folder_for_outputs(self):
        directory = filedialog.askdirectory()
        self.folder_path.set(directory)

    def run_part1_comand_line_script(self):

        url     = self.input_url.get()
        op_date = self.sitting_date.get()
        folder_path = self.folder_path.get()

        output_file_name = path.join(folder_path, 'as-downloaded-' + op_date + '.xml')
        # print(output_file_name)

        print('\nThe URL we are trying is:\n{}'.format(url))
        infilename = get_file_from_url(url, output_file_name=output_file_name)

        part1_script.process_xml(infilename, op_date)


    def run_FBA_comand_line_script(self):

        url     = self.input_url.get()
        op_date = self.sitting_date.get()
        folder_path = self.folder_path.get()

        output_file_name = path.join(folder_path, 'as-downloaded-' + op_date + '.xml')
        # print(output_file_name)

        print('\nThe URL we are trying is:\n{}'.format(url))
        infilename = get_file_from_url(url, output_file_name=output_file_name)

        fba_script.process_xml(infilename, op_date)


    def run_ann_comand_line_script(self):
        url     = self.input_url.get()
        op_date = self.sitting_date.get()
        folder_path = self.folder_path.get()

        output_file_name = path.join(folder_path, 'as-downloaded-' + op_date + '.xml')
        # print(output_file_name)

        print('\nThe URL we are trying is:\n{}'.format(url))
        infilename = get_file_from_url(url, output_file_name=output_file_name)

        ann_script.process_xml(infilename, op_date)


def get_tomorow_date():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return tomorrow.strftime('%Y-%m-%d')


def get_file_from_url(url, output_file_name='output.xml'):
    try:
        # ignore the ssl certificate
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(url, context=context)
    except:
        print('\nERROR:\tCan\'t get the XML from:\n{}\nCheck the url is right.'.format(url))
        return -1
    data = response.read()      # a `bytes` object
    # text = data.decode('utf-8')  # a `str`; this step can't be used if data is binary
    output_file = open(output_file_name, 'wb')
    output_file.write(data)
    output_file_path = path.abspath(output_file.name)
    output_file.close()
    print('\nDownloaded XML is at:\n{}'.format(output_file_path))
    return output_file_path


# counter
class Counter:
    def __init__(self):
        self.number = 0

    def increment(self):
        self.number += 1

    def count(self):
        self.increment()
        return self.number


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

    run_toolapp = Tk()
    app = EBApp(run_toolapp)
    run_toolapp.mainloop()


if __name__ == "__main__": main()
