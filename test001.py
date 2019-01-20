import tkinter as tk
from tkinter import ttk
import subprocess
import threading

import adb.client

from hucontrol import *


# Default is "127.0.0.1" and 5037
client = adb.client.Client(host="127.0.0.1", port=5037)

adb_path = resource_path('venv/Lib/adb/adb.exe')
# calculator_apk_4_4_path = resource_path('adb/calculator_apk/4.4.2_sec_calculator.apk')

sub_p_adb = subprocess.call([adb_path, 'devices'])

try:
    devices = client.devices()
except:
    print("error")

adb_threads = []

exitFlag = 0


class AdbDeviceThread(threading.Thread):
    def __init__(self, threadID, name, counter, each_device, command, arg1="", arg2=""):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.device = each_device
        self.command = command
        self.arg1 = arg1
        self.arg2 = arg2

    def run(self):
        print("Starting " + self.name)
        print_time(self.name, 1, self.counter)
        if exitFlag:
            self.name.exit()

        if self.command == "openEngineeringMode":
            open_engineering_mode(self.device)
        if self.command == "openTelematicsTest":
            open_telematics_test(self.device)
        if self.command == "inputText":
            shell_input_text(self.device, self.arg1)
        if self.command == "takeScreenshot":
            take_screenshot(self.device, self.arg1)
        if self.command == "pullAfterChmod":
            pull_after_chmod(self.device, self.arg1, self.arg2)

        print("Exiting " + self.name)


def print_time(thread_name, counter, delay):
    while counter:
        if exitFlag:
            thread_name.exit()

        time.sleep(delay)
        print("%s: %s" % (thread_name, time.ctime(time.time())))
        counter -= 1


def threads_button_action(cmd, arg_1="", arg_2=""):
    for thr in adb_threads:
        thr.command = cmd
        if arg_1 != "":
            thr.arg1 = arg_1
        if arg_2 != "":
            thr.arg2 = arg_2
        thr.start()
    adb_threads[len(adb_threads) - 1].join()


def enter_on_text_input(temp_args):
    print("enter key pressed on text input entry")
    threads_button_action("inputText", entry_input_text.get())


def enter_on_screenshot(temp_args):
    print("enter key pressed on screenshot entry")
    threads_button_action("takeScreenshot", entry_screenshot_path.get())


# Tkinter
root = tk.Tk()
root.wm_title("M HU Controller")

entry_value = ''

device_number_label = tk.Label(root, text="Connected HU: ", width=25)
device_number_label.grid(row=0, column=0)

connected_devices_indicator = tk.Entry(root, textvariable=entry_value, width=25)
connected_devices_indicator.grid(row=0, column=1, stick='nsew')

blank_label = tk.Label(root, text=" ", width=50)
blank_label.grid(row=0, column=2, columnspan=2)

empty_line = tk.Label(root, text=" ")
empty_line.grid(row=1, column=0)


btn_engineering_mode = tk.Button(root,
                                 text="ENG Mode",
                                 command=lambda: threads_button_action("openEngineeringMode"))
btn_engineering_mode.grid(row=2, column=0, rowspan=2, sticky='nsew')
btn_telematics_test = tk.Button(root,
                                text="Telematics Test",
                                command=lambda: threads_button_action("openTelematicsTest"))
btn_telematics_test.grid(row=2, column=1, rowspan=2, sticky='nsew')

empty_line2 = tk.Label(root, text=" ")
empty_line2.grid(row=4, column=0)

btn_input_text = tk.Button(root,
                           text="Input Text",
                           command=lambda: threads_button_action("inputText", entry_input_text.get()))
btn_input_text.grid(row=5, column=0, sticky='nsew')

entry_input_text = tk.Entry(root)
entry_input_text.grid(row=5, column=1, columnspan=2, sticky='nsew')
entry_input_text.insert(10, "")
entry_input_text.bind('<Return>', enter_on_text_input)

empty_line3 = tk.Label(root, text=" ")
empty_line3.grid(row=6, column=0)

btn_screenshot = tk.Button(root,
                           text="Screenshot",
                           command=lambda: threads_button_action("takeScreenshot", entry_screenshot_path.get()))
btn_screenshot.grid(row=7, column=0, sticky='nsew')

entry_screenshot_path = tk.Entry(root)
entry_screenshot_path.grid(row=7, column=1, columnspan=2, sticky='nsew')
entry_screenshot_path.insert(10, os.path.expanduser("~\Desktop"))
entry_screenshot_path.bind('<Return>', enter_on_screenshot)

empty_line4 = tk.Label(root, text=" ")
empty_line4.grid(row=8, column=0)


lbl_src_path = tk.Label(root, text=" * Source Path: ")
lbl_src_path.grid(row=9, column=0, sticky='e')

entry_pull_src_path = tk.Entry(root)
entry_pull_src_path.grid(row=9, column=1, columnspan=3, sticky='nsew')
entry_pull_src_path.insert(10, "/data/data/com.hkmc.telematics.common.db/databases/VehicleSetting.db")

lbl_dst_path = tk.Label(root, text=" * Destination Path: ")
lbl_dst_path.grid(row=10, column=0, sticky='e')

entry_pull_dst_path = tk.Entry(root)
entry_pull_dst_path.grid(row=10, column=1, columnspan=3, sticky='nsew')
entry_pull_dst_path.insert(10, os.path.expanduser("~\Desktop"))

btn_pull = tk.Button(root,
                     text="Pull",
                     command=lambda: threads_button_action("pullAfterChmod", entry_pull_src_path.get(), entry_pull_dst_path.get()))
btn_pull.grid(row=11, column=0, columnspan=4, sticky='nsew')

notebook = ttk.Notebook(root)
notebook_page_1 = tk.Frame(notebook)
notebook.add(notebook_page_1, text='Tab 1')
lbl_test = tk.Label(notebook_page_1, text="Test")
lbl_test.grid(row=0, column=0, sticky='nsew')

notebook_page_2 = tk.Frame(notebook)
notebook.add(notebook_page_2, text='Tab 2')

notebook.grid(row=12, rowspan=4, column=0, columnspan=4, sticky='nsew')

root.pack_propagate(0)


cnt = 0


# Main Loop
def main_loop():
    adb_device_counter = 0
    new_devices = client.devices()
    global devices
    devices = new_devices
    for device in new_devices:
        try:
            if device.get_state() == "device":
                adb_device_counter = adb_device_counter + 1
        except:
            print("error")

    global adb_threads
    adb_threads = []

    thread_num = 0
    for device in devices:
        # print(device.get_serial_no())
        temp_thread = AdbDeviceThread(thread_num, "Thread", 1, device, "")
        adb_threads.append(temp_thread)
        thread_num += 1

    global entry_value
    entry_value = adb_device_counter
    connected_devices_indicator.delete(0, "end")
    connected_devices_indicator.insert("end", entry_value)
    # print("Number of ADB devices connected: ", entry_value)
    # print("ADB Threads list length :", len(adb_threads))

    print(len(adb_threads))

    global cnt
    cnt += 1
    print("TIME: ", cnt)
    root.after(1000, main_loop)

    if entry_value == 0:
        btn_engineering_mode.config(state="disabled")
        btn_telematics_test.config(state="disabled")
        btn_input_text.config(state="disabled")
        btn_screenshot.config(state="disabled")
        btn_pull.config(state="disabled")
    else:
        btn_engineering_mode.config(state="normal")
        btn_telematics_test.config(state="normal")
        btn_input_text.config(state="normal")
        btn_screenshot.config(state="normal")
        btn_pull.config(state="normal")


root.after(1000, main_loop)

root.mainloop()
