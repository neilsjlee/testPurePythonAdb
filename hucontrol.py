import os
import sys
import time
import re
import serial
import serial.tools.list_ports


def serial_test():
    comlist = serial.tools.list_ports.comports()
    connected = []
    for element in comlist:
        connected.append(element.device)
    print("Connected COM ports: " + str(connected))

    ser = serial.Serial('COM3', 115200)
    print("Hello! ", ser)
    # ser.open()

    ser.write(b'd_audio\r\n')
    print(ser.readline(20))
    ser.write(b'am start -n com.hkmc.telematics.apps.main/.testmode.TestModeMain\r\n')
    print(ser.readline(20))


# serial_test()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

telematics_test_apk_path = resource_path('venv/Lib/external_apk/TelematicsTest.apk')


def check_ui_component_value(each_device, component):
    each_device.shell("uiautomator dump")
    xml_text = each_device.shell("cat /sdcard/window_dump.xml")
    each_device.shell("rm /sdcard/window_dump.xml")
    # print(xml_text)
    ui_dump = xml_text.split("<node ")

    i = 0
    result_component = "not_found"
    while i < len(ui_dump):
        if component in ui_dump[i]:
            # If the component has empty text value
            if "text=\"\"" not in ui_dump[i]:
                result_component = re.search(r'text=\"(.*?)\"', ui_dump[i]).group()
            else:
                result_component = ""
        i += 1

    if result_component == "not_found":
        print("ERROR: check_ui_component_value: The component was not found: " + component)
    else:
        print("The component was found: " + component + ": " + result_component)
    return result_component


def check_ui_component_bound(each_device, component):
    each_device.shell("uiautomator dump")
    xml_text = each_device.shell("cat /sdcard/window_dump.xml")
    each_device.shell("rm /sdcard/window_dump.xml")
    # print(xml_text)
    ui_dump = xml_text.split("<node ")

    i = 0
    result_component = "false"
    component_bound_xy = [0, 0]
    while i < len(ui_dump):
        if component in ui_dump[i]:
            result_component = "true"
            # If the component has empty text value
            component_bound_str = re.search(r'bounds="\[.*\]', ui_dump[i]).group()
            component_bound_str_list = re.findall('\d+', component_bound_str)
            component_bound_xy = [int((int(component_bound_str_list[0]) + int(component_bound_str_list[2])) / 2),
                                  int((int(component_bound_str_list[1]) + int(component_bound_str_list[3])) / 2)]
        i += 1

    if result_component == "false":
        print("ERROR: check_ui_component_value: The component was not found: " + component)
    else:
        print("The component was found: " + component + ": " + str(component_bound_xy[0]) + ", " + str(
            component_bound_xy[1]))
    return component_bound_xy



def take_screenshot(each_device, file_save_path):
    '''
    each_device.shell("screencap -p " + "/storage/log/screenshot_temp.png")
    print("/storage/log/screenshot_temp.png SAVED")
    current_time = time.strftime('%Y%m%d%H%M%S', time.gmtime(int(each_device.shell("date +%s"))))
    print(current_time + " " + file_save_path)
    print("/storage/log/screenshot_temp.png", file_save_path + "/screenshot_" + current_time + ".png")
    time.sleep(3)
    print(each_device.pull("/storage/log/screenshot_temp.png", file_save_path + "/screenshot_" + current_time + ".png"))
    #print(each_device.pull("/storage/log/screenshot_temp.png", file_save_path + "/screenshot" + ".png"))
    print("pull complete")
    each_device.shell("rm /storage/log/screenshot_temp.png")
    '''
    result = each_device.screencap()
    current_time = time.strftime('%Y%m%d%H%M%S', time.gmtime(int(each_device.shell("date +%s"))))
    with open(file_save_path + "/screenshot_" + current_time + ".png", "wb") as fp:
        fp.write(result)
    print("Screenshot Saved: " + file_save_path + "/screenshot_" + current_time + ".png")


def shell_input_text(each_device, input_text):
    each_device.shell("input text \"" + input_text + "\"")


def install_telematics_test_apk(each_device):
    result = 'false'
    target_apk = telematics_test_apk_path
    try:
        print(each_device.install(target_apk))
        result ='true'
    except:
        result = 'false'

    return result


def open_engineering_mode(each_device):
    print(each_device.shell("d_audio -c am start -n com.hkmc.system.app.engineering/.EngineeringModeMainActivity"))


def open_telematics_test(each_device):
    if each_device.shell("pm list packages | grep com.hkmc.telematics.apps.main") == "":
        print("open_telematics_test(): Telematics TEST apk not found. Installing APK...")
        result = install_telematics_test_apk(each_device)
        if result == 'true':
            print("open_telematics_test(): Telematics Test apk installed.")
        elif result == 'false':
            print("open_telematics_test(): Failed to install Telematics Test apk.")
    print(each_device.shell("d_audio -c am start -n com.hkmc.telematics.apps.main/.testmode.TestModeMain"))


def auto_provisioning(each_device):
    open_telematics_test(each_device)
    uibtn_xy = check_ui_component_bound(each_device, "btn_setting")
    each_device.shell("input tap " + str(uibtn_xy[0]) + " " + str(uibtn_xy[1]))
    uibtn_xy = check_ui_component_bound(each_device, "Change PhoneNumber")
    each_device.shell("input tap " + str(uibtn_xy[0]) + " " + str(uibtn_xy[1]))


def serial_port_pull(file_src_path):
    ser = serial.Serial('COM3', 115200)
    print("Hello! COM Port Connected!", ser)
    # ser.open()

    parse_list = file_src_path.split("/")
    print(file_src_path, len(parse_list), parse_list[len(parse_list) - 1])

    ser.write(b'd_audio\r\n')
    ser.readline(20)
    print("Entered d_audio")
    raw_str_command = "cp " + file_src_path + " /storage/log/" + "\r\n"
    print(raw_str_command)
    bytes_str_command = str.encode(raw_str_command)
    # print(type(bytes_str_command))
    ser.write(bytes_str_command)

    raw_str_command = "chmod 777 /storage/log/" + parse_list[len(parse_list) - 1] + "\r\n"
    print(raw_str_command)
    bytes_str_command = str.encode(raw_str_command)
    # print(type(bytes_str_command))
    ser.write(bytes_str_command)

    print(ser.readline(20))


def pull_detour_ready(each_device, file_src_path):
    parse_list = file_src_path.split("/")
    print(file_src_path, len(parse_list), parse_list[len(parse_list) - 1])

    str_command = "d_audio -c cp " + file_src_path + " /storage/log/"
    print(str_command)

    print(each_device.shell(str_command))

    str_command = "d_audio -c chmod 777 /storage/log/" + parse_list[len(parse_list) - 1]
    print(str_command)
    print(each_device.shell(str_command))


def pull_after_chmod(each_device, file_src_path, file_dst_path):
    print("Not Yet Implemented.....")
    ro_product_model = each_device.shell("getprop | grep ro.product.model")
    if "[wp_daudioplus" in ro_product_model:
        print("GEN5 WIDE: COM Port needed")
        serial_port_pull(file_src_path)
    else:
        pull_detour_ready(each_device, file_src_path)
        print(each_device.shell("d_audio -c chmod 777 " + file_src_path))

    parse_list = file_src_path.split("/")
    print(file_src_path, len(parse_list), parse_list[len(parse_list) - 1])

    print("File detour on HU is complete. Start Pulling...")
    each_device.pull("storage/log/" + parse_list[len(parse_list) - 1],
                     file_dst_path + "/" + parse_list[len(parse_list) - 1])
    each_device.shell("rm /storage/log/" + parse_list[len(parse_list) - 1])


def serial_port_push(file_src_path):
    ser = serial.Serial('COM3', 115200)
    print("Hello! COM Port Connected!", ser)
    # ser.open()

    parse_list = file_src_path.split("/")
    print(file_src_path, len(parse_list), parse_list[len(parse_list) - 1])

    ser.write(b'd_audio\r\n')
    ser.readline(20)
    print("Entered d_audio")
    raw_str_command = "cp " + file_src_path + " /storage/log/" + "\r\n"
    print(raw_str_command)
    bytes_str_command = str.encode(raw_str_command)
    # print(type(bytes_str_command))
    ser.write(bytes_str_command)

    raw_str_command = "chmod 777 /storage/log/" + parse_list[len(parse_list) - 1] + "\r\n"
    print(raw_str_command)
    bytes_str_command = str.encode(raw_str_command)
    # print(type(bytes_str_command))
    ser.write(bytes_str_command)

    print(ser.readline(20))


def push_after_chmod(each_device, file_src_path, file_dst_path):
    print("Not Yet Implemented.....")
    ro_product_model = each_device.shell("getprop | grep ro.product.model")

    parse_list = file_src_path.split("\\")
    print(file_src_path, len(parse_list), parse_list[len(parse_list) - 1])

    if file_dst_path.endswith('/') == False:
        file_dst_path += "/"
        print(file_dst_path)

    if "[wp_daudioplus" in ro_product_model:
        each_device.push(file_src_path, "/storage/log/" + parse_list[len(parse_list) - 1])
        print("File pushed to /storage/log")
        print("GEN5 WIDE: COM Port needed")

        #serial_port_push(file_src_path)

        ser = serial.Serial('COM3', 115200)
        ser.write(b'd_audio\r\n')
        ser.readline(20)
        print("Entered d_audio")

        raw_str_command = "cp /storage/log/" + parse_list[len(parse_list) - 1] + " " + file_dst_path + "\r\n"
        print(raw_str_command)
        bytes_str_command = str.encode(raw_str_command)
        ser.write(bytes_str_command)

        print(ser.readline(20))

        # raw_str_command = "rm /storage/log/" + parse_list[len(parse_list) - 1] + "\r\n"
        # print(raw_str_command)
        # bytes_str_command = str.encode(raw_str_command)
        # ser.write(bytes_str_command)
        serial_command("rm /storage/log/" + parse_list[len(parse_list) - 1])

        print(ser.readline(20))

    elif "[daudioplus" in ro_product_model:
        each_device.push(file_src_path, "/storage/log/" + parse_list[len(parse_list) - 1])
        print(each_device.shell("d_audio -c cp /storage/log/" + parse_list[len(parse_list) - 1] + " " + file_dst_path))
        each_device.shell("rm /storage/log/" + parse_list[len(parse_list) - 1])
    else:
        print("Unknown HU. Trying to push directly without detour...")
        print(each_device.push(file_src_path, file_dst_path + parse_list[len(parse_list) - 1]))


def serial_command(cmd):
    ser = serial.Serial('COM3', 115200)
    ser.write(b'd_audio\r\n')
    ser.readline(20)

    raw_str_command = cmd + "\r\n"
    print(raw_str_command)
    bytes_str_command = str.encode(raw_str_command)
    ser.write(bytes_str_command)
    print(ser.readline(20))

