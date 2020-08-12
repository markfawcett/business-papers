#!/usr/local/bin/python3

# next to lines are required for GUI file pickers
import tkinter as tk
from tkinter import ttk, filedialog, StringVar, messagebox
# this is the brains of the operation
import Python_Resources.transfrom_EDMs_HTML_cmd as cmd_version
from datetime import datetime  # dates
import os


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

    tk_instance = tk.Tk()
    gui_app(tk_instance)
    tk_instance.mainloop()


# class for the GUI app
class gui_app:
    def __init__(self, master):

        self.input_file_path = ''
        self.template_file_path = ''
        self.prepared_date = StringVar()  # in YYYY-MM-DD form

        # add title to the window
        master.title("Transform EDMs HTML for web")

        # create a counter to for the rows for the grid geometry
        r = Counter()

        # make background frame
        self.frame_background = ttk.Frame(master)
        self.frame_background.pack(fill=tk.BOTH, expand=tk.TRUE)
        # add margin space
        self.inner_background = ttk.Frame(self.frame_background)
        self.inner_background.pack(fill=tk.BOTH, expand=tk.TRUE, padx=5, pady=20)

        # make frames for each step
        step_1 = ttk.LabelFrame(self.inner_background, text='Step 1')
        step_1.pack(padx=10, pady=5, fill=tk.BOTH, expand=tk.TRUE)
        step_2 = ttk.LabelFrame(self.inner_background, text='Step 2')
        step_2.pack(padx=10, pady=5, fill=tk.BOTH, expand=tk.TRUE)
        step_3 = ttk.LabelFrame(self.inner_background, text='Step 3')
        step_3.pack(padx=10, pady=5, fill=tk.BOTH, expand=tk.TRUE)
        step_4 = ttk.LabelFrame(self.inner_background, text='Step 4')
        step_4.pack(padx=10, pady=5, fill=tk.BOTH, expand=tk.TRUE)

        # Input html lable
        input_lable = ttk.Label(
            step_1, text='Select the EDMs HTML file you have exported from InDesign.', wraplength=300)
        input_lable.grid(
            row=r.count(), column=0, stick='w', padx=5, pady=10)
        # input html button
        input_file_button = ttk.Button(
            step_1, text="Input HTML File", width=14, command=self.get_input_file)
        input_file_button.grid(
            row=r.count(), column=0, stick='w', padx=5, pady=5)

        # template file lable
        template_lable = ttk.Label(
            step_2, text='Find the Template HTML file.', wraplength=300)
        template_lable.grid(
            row=r.count(), column=0, stick='w', padx=5, pady=10)
        # tamplate html button
        template_file_button = ttk.Button(
            step_2, text="Template File", width=14, command=self.get_template_file)
        template_file_button.grid(
            row=r.count(), column=0, stick='w', padx=5, pady=5)

        # Date lable
        date_label = ttk.Label(
            step_3, text='Check the Date is correct. This date will be inserted at the bottom of the HTML page. (YYYY-MM-DD)', wraplength=300)
        date_label.grid(
            row=r.count(), column=0, stick='w', padx=5, pady=10)
        # date text entry box
        prepared_box = ttk.Entry(
            step_3, textvariable=self.prepared_date, width=10)
        prepared_box.grid(
            row=r.count(), column=0, stick='w', pady=3, padx=5)
        # Insert the current date into the date box. In YYY-MM-DD form
        prepared_box.insert(0, datetime.now().strftime('%Y-%m-%d'))

        # Run lable
        date_lable = ttk.Label(
            step_4, text="Press Run and then look for the 'All Done' message in the console window. You should then see a new HTML file ready for the parliament website in the same folder as the input", wraplength=300)
        date_lable.grid(
            row=r.count(), column=0, stick='w', padx=5, pady=10)
        # Run button
        run_button = ttk.Button(
            step_4, text="Run", width=20, command=self.run_script_cmd_version)
        run_button.grid(
            row=r.count(), column=0, columnspan=3, padx=10, pady=15)

    def get_input_file(self):
        directory = filedialog.askopenfilename()
        self.input_file_path = directory
        print('Input file path: ', directory, '\n')

    def get_template_file(self):
        directory = filedialog.askopenfilename()
        self.template_file_path = directory
        print('Template file path: ', directory, '\n')

    def run_script_cmd_version(self):
        # need to use getter to get prepared date
        prepared_date = self.prepared_date.get()
        # First check user input
        try:
            datetime.strptime(prepared_date, '%Y-%m-%d')
        except ValueError:
            error_date_text = 'Looks like "{}" isn\'t a valid date. Try Entering it again.'
            show_error(error_date_text.format(prepared_date))
            return

        # run functions
        cmd_version.transform_xml(self.input_file_path, self.template_file_path, prepared_date)
        print('\nAll Done!')


def show_error(error_text):
    error_text = 'ERROR: ' + error_text
    # if os.name == 'posix':
    print('\033[91m' + error_text + '\033[0m')
    # else: print(error_text)
    messagebox.showerror("Error", error_text)


# counter
class Counter:
    def __init__(self):
        self.number = 0

    def increment(self):
        self.number += 1

    def count(self):
        self.increment()
        return self.number


if __name__ == "__main__": main()
