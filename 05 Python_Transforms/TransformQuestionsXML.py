#!/usr/local/bin/python3

# for geting tomorows date
import datetime
# next to lines are required for GUI file pickers
import tkinter as tk
# from tkinter import *
from tkinter import ttk, filedialog, Text
# for making the program pause
import time
# working with paths
import os

# for getting files form urls
import ssl
import urllib.request

# this is the brains of the operation
import Python_Resources.TransformQuestionsXML_cmd as cmd_version

# default URL. (Needs date in YYYY-MM-DD to work)
default_bace_url = 'https://api.eqm.parliament.uk/feed/Xml/OrderPaper.xml?sittingDate='


def main():
    tk_instance = tk.Tk()
    Gui_app(tk_instance)
    # tk_instance.wm_minsize(500, None)
    tk_instance.mainloop()


# class for the GUI app
class Gui_app:
    def __init__(self, master):

        # input file path
        self.input_file_path = tk.StringVar()
        self.local_file_path = tk.StringVar()
        # dates should be of the form YYYYMMDD
        self.sitting_date    = tk.StringVar()
        # input file path
        self.working_folder  = tk.StringVar()
        # radio button val
        self.rad_val = tk.IntVar(value=1)
        # self.rad_val.set(1)
        # input url path
        # self.input_url       = tk.StringVar()

        # add title to the window
        master.title("Transform Questions XML")

        # make background frame
        frame_background = ttk.Frame(master)
        frame_background.pack(fill=tk.BOTH, expand=tk.TRUE)
        # add margin space
        inner_background = ttk.Frame(frame_background)
        inner_background.pack(fill=tk.BOTH, expand=tk.TRUE, padx=5, pady=15)

        # make frames for each step
        step_1 = ttk.LabelFrame(inner_background, text='Step 1')
        step_1.pack(padx=10, pady=5, fill=tk.BOTH, expand=tk.TRUE)
        step_2 = ttk.LabelFrame(inner_background, text='Step 2')
        step_2.pack(padx=10, pady=5, fill=tk.BOTH, expand=tk.TRUE)
        step_3 = ttk.LabelFrame(inner_background, text='Step 3')
        step_3.pack(padx=10, pady=5, fill=tk.BOTH, expand=tk.TRUE)
        step_4 = ttk.LabelFrame(inner_background, text='Step 4')
        step_4.pack(padx=10, pady=5, fill=tk.BOTH, expand=tk.TRUE)
        step_5 = ttk.LabelFrame(inner_background, text='Step 5')
        step_5.pack(padx=10, pady=5, fill=tk.BOTH, expand=tk.TRUE)

        # radio buttons
        ttk.Label(
            step_1,
            text='How would you like to get the raw Questions XML:'
        ).pack(padx=5, anchor=tk.W)
        ttk.Radiobutton(
            step_1,
            command=self.toggle_modes,
            text="Option 1: from the URL below",
            variable=self.rad_val,
            value=1
        ).pack(padx=5, anchor=tk.W)
        ttk.Radiobutton(
            step_1,
            command=self.toggle_modes,
            text="Option 2: from a file on my system",
            variable=self.rad_val,
            value=2
        ).pack(padx=5, pady=2, anchor=tk.W)

        # url text entry lable
        self.url_box_lable = ttk.Label(
            step_2,
            text='If you selected option 1\n'
            'you can change the base URL. Don\'t put the date in here.'
            '(This can be useful when testing the dev version of EQM)')
        self.url_box_lable.config(wraplength=400)
        self.url_box_lable.pack(anchor=tk.W, padx=5, pady=3)
        # url text entry box
        self.url_box = Text(step_2, width=50, height=4, wrap='word')
        self.url_box.pack(anchor=tk.W, padx=5, pady=5)
        self.url_box.insert(
            0.0, 'https://api.eqm.parliament.uk/feed/Xml/OrderPaper.xml?sittingDate=')

        # select input file
        self.select_file_lable = ttk.Label(
            step_2,
            text='If you selected option 2\n'
            'select the input XML file. '
            'This is XML from EQM that has not been transformed for InDesign.'
        )
        self.select_file_lable.pack(anchor=tk.W, padx=5, pady=2)
        self.select_file_lable.config(wraplength=400, state='disabled')
        # select folder button
        self.select_file_button = ttk.Button(
            step_2, text="Select raw XML file",
            width=20, command=self.get_input_file_local, state='disabled')
        self.select_file_button.pack(anchor=tk.W, padx=5, pady=5)

        # select folder lable
        self.select_folder_lable = ttk.Label(
            step_3,
            text='Select the folder that you would like the (transformed) XML to be saved into.')
        self.select_folder_lable.config(wraplength=400)
        self.select_folder_lable.pack(anchor=tk.W, padx=5, pady=2)
        # select folder button
        self.select_folder_button = ttk.Button(
            step_3, text="Select Folder",
            width=12, command=self.get_working_folder)
        self.select_folder_button.pack(anchor=tk.W, padx=5, pady=5)

        # OP sitting date box
        self.sitting_date_box_lable = ttk.Label(
            step_4,
            text='Check that the OP sitting is correct. '
            'It should be in the form YYYY-MM-DD (e.g. 2017-09-12)')
        self.sitting_date_box_lable.config(wraplength=400)
        self.sitting_date_box_lable.pack(anchor=tk.W, padx=5, pady=3)
        self.sitting_date_box = ttk.Entry(step_4, textvariable=self.sitting_date, width=10)
        self.sitting_date_box.pack(anchor=tk.W, padx=5, pady=3)
        self.sitting_date_box.insert(0, get_tomorow_date())

        # Run button lable
        self.run_lable = ttk.Label(
            step_5,
            text='Press Run and then look for "All Done" in the console '
            'window. *You need to select a folder above before this button will '
            'become active.')
        self.run_lable.config(wraplength=400)
        self.run_lable.pack(anchor=tk.W, padx=5, pady=3)
        # run button
        self.run_button = ttk.Button(
            step_5, text="Run", state='disabled', width=20, command=self.run_TransformQsXML)
        self.run_button.pack(padx=10, pady=15)

        # try and set min dimensions
        master.update_idletasks()
        master.after_idle(lambda: master.minsize(master.winfo_width(), master.winfo_height()))



    def run_TransformQsXML(self):

        sittingdate    = self.sitting_date.get()
        output_folder  = self.working_folder.get()

        if self.rad_val.get() == 1:
            input_file_uri = self.url_box.get("1.0", tk.END).strip()
            input_file_uri = input_file_uri + sittingdate

            print('\nTrying to get XML from:\n{}'.format(input_file_uri))
            output_file_name = os.path.join(
                output_folder, 'orals_as_downloaded_' + sittingdate + '.xml')
            input_file_uri = get_file_from_url(
                input_file_uri, output_file_name=output_file_name)
        else:
            input_file_uri = self.local_file_path.get()

        time.sleep(1)  # wait 1 second (so file date created is later)
        # run command line version
        cmd_version.transform_xml(
            input_file_uri, output_folder=output_folder, sitting_date=sittingdate)

        print('\nAll Done!')

    def toggle_modes(self):
        if self.rad_val.get() == 1:
            # url box
            self.url_box.config(state='normal')
            self.url_box.config(foreground='black')
            self.url_box_lable.config(state='normal')
            # input file box
            self.select_file_button.config(state='disabled')
            self.select_file_lable.config(state='disabled')
        else:
            # url box
            self.url_box.config(state='disabled')
            self.url_box.config(foreground='gray')
            self.url_box_lable.config(state='disabled')
            # input file box
            self.select_file_button.config(state='normal')
            self.select_file_lable.config(state='normal')

    def get_input_file_local(self):
        directory = filedialog.askopenfilename()
        self.local_file_path.set(directory)
        print('\nInput XML file is at:\n' + self.local_file_path.get())

    def get_working_folder(self):
        directory = filedialog.askdirectory()
        self.working_folder.set(directory)
        # also make the run button active
        self.run_button.config(state='normal')


def get_tomorow_date():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return tomorrow.strftime('%Y-%m-%d')


def get_file_from_url(uri, output_file_name='orals_as_downloaded.xml'):
    try:
        # ignore the ssl certificate
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(uri, context=context)
    except:
        print('\nERROR:\tCan\'t get the XML from:\n{}\nCheck the url is right.'.format(uri))
        return -1
    data = response.read()      # a `bytes` object
    # text = data.decode('utf-8')  # a `str`; this step can't be used if data is binary
    output_file = open(output_file_name, 'wb')
    output_file.write(data)
    output_file_path = os.path.abspath(output_file.name)
    output_file.close()
    print('\nDownloaded XML is at:\n{}'.format(output_file_path))

    return output_file_path


if __name__ == "__main__": main()
