'''
def screen_on(each_device):
    scr_status = each_device.shell("dumpsys input_method | grep mInteractive")
    if scr_status == "  mSystemReady=true mInteractive=false\n":
        each_device.shell("input keyevent KEYCODE_POWER")
        each_device.shell("input keyevent KEYCODE_MENU")
    else:
        scr_status_dim = each_device.shell("dumpsys display | grep mPendingRequestLocked=policy=")
        if "mPendingRequestLocked=policy=DIM" in scr_status_dim:
            each_device.shell("input keyevent KEYCODE_POWER")
            each_device.shell("input keyevent KEYCODE_POWER")
            each_device.shell("input keyevent KEYCODE_MENU")


def install_calculator(each_device):
    result = "fail"
    target_apk = ""

    screen_on(each_device)
    android_ver = each_device.shell("getprop | grep ro.build.version.release")
    if "[4.4" in android_ver:
        # 4.4
        target_apk = calculator_apk_4_4_path
    elif "[5" in android_ver:
        # 5 or 5.1.. hopefully
        target_apk = calculator_apk_5_1_path
    elif "[6" in android_ver:
        # 6
        target_apk = calculator_apk_6_0_path
    elif "[7.0" in android_ver:
        # 7.0
        target_apk = calculator_apk_7_0_path
    elif "[7.1" in android_ver:
        # 7.1
        target_apk = calculator_apk_7_1_path
    elif "[8.0" in android_ver:
        # 8.0
        target_apk = calculator_apk_8_0_path
    elif "[8.1" in android_ver:
        # 8.1
        target_apk = calculator_apk_8_1_path
    elif "[9" in android_ver:
        # 9
        target_apk = calculator_apk_9_0_path
    else:
        print("Error: Android version is not compatible with this tool.")
        result = "fail"

    if target_apk != "":
        try:
            each_device.install(target_apk)
            result = "success"
        except:
            result = "fail"

    return result


def open_keystring_app(each_device):
    result = "fail"

    screen_on(each_device)
    time.sleep(2)
    if "com.sec.android.app.parser" in each_device.shell("dumpsys window windows | grep mCurrentFocus"):
        if check_ui_component_value(each_device, "EditText") != "" and "not_found":
            clear_btn_coordinate = check_ui_component_bound(each_device, "bt_clear")
            each_device.shell("input tap " + str(clear_btn_coordinate[0]) + " " + str(clear_btn_coordinate[1]))
        result = "ok"

    elif "com.sec.android.app.popupcalculator" in each_device.shell("dumpsys window windows | grep mCurrentFocus"):
        each_device.shell("am force-stop com.sec.android.app.parser")
        if check_ui_component_value(each_device, "EditText") != "" and "not_found":
            clear_btn_coordinate = check_ui_component_bound(each_device, "bt_clear")
            each_device.shell("input tap " + str(clear_btn_coordinate[0]) + " " + str(clear_btn_coordinate[1]))
        each_device.shell("input text \(+30012012732+")
        time.sleep(1)
        if "com.sec.android.app.parser" in each_device.shell("dumpsys window windows | grep mCurrentFocus"):
            result = "ok"
        else:
            result = "Unable to open Keystring app"
    else:
        each_device.shell("am force-stop com.sec.android.app.popupcalculator")
        each_device.shell("am force-stop com.sec.android.app.parser")
        if each_device.shell("pm list packages | grep com.sec.android.app.popupcalculator") == "":
            install_calculator(each_device)
        each_device.shell("am start com.sec.android.app.popupcalculator/.Calculator")
        time.sleep(1)
        each_device.shell("input text \(+30012012732+")
        time.sleep(1)
        if "com.sec.android.app.parser" in each_device.shell("dumpsys window windows | grep mCurrentFocus"):
            result = "ok"
        else:
            result = "Unable to open Keystring app"
    time.sleep(1)
    return result


def keystring_dmmode_on(each_device):
    if open_keystring_app(each_device) == "ok":
        each_device.shell("input text \##366633#")
        each_device.shell("input keyevent KEYCODE_DPAD_UP")
        each_device.shell("input keyevent KEYCODE_ENTER")
    else:
        print("ERROR: Unable to open Keystring App...")


def keystring_cpramdump_on(each_device):
    if open_keystring_app(each_device) == "ok":
        each_device.shell("input text \*#66336#")
        time.sleep(1)
        if "com.sec.android.app.servicemodeapp" in each_device.shell("dumpsys window windows | grep mCurrentFocus"):
            if "CP RAMDUMP OFF" in check_ui_component_value(each_device, "bt_cp_debug"):
                each_device.shell("input keyevent KEYCODE_ENTER")
                each_device.shell("input keyevent KEYCODE_ENTER")
                print("Turning CP RAMDUMP ON")
            else:
                print("CP RAMDUMP was ON")
        else:
            print("Error: CP RAMPDUMP Service App was not opened. Please try again later")
    else:
        print("ERROR: Unable to open Keystring App...")


def keystring_sysdump(each_device):
    if open_keystring_app(each_device) == "ok":
        each_device.shell("input text \*#9900#")
    else:
        print("ERROR: Unable to open Keystring App...")


def keystring_rtn(each_device):
    if open_keystring_app(each_device) == "ok":
        each_device.shell("input text \##786#")
        each_device.shell("input keyevent KEYCODE_DPAD_DOWN")
        each_device.shell("input keyevent KEYCODE_DPAD_DOWN")
        each_device.shell("input keyevent KEYCODE_ENTER")
    else:
        print("ERROR: Unable to open Keystring App...")


def reboot_download(each_device):
    each_device.shell("reboot download")


def thread_skip_suw(thread_name, delay, each_device):
   if exitFlag:
        thread_name.exit()

    time.sleep(delay)
    screen_on(each_device)
    each_device.shell("settings put global setup_wizard_has_run 1")
    each_device.shell("settings put secure user_setup_complete 1")
    each_device.shell("settings put global device_provisioned 1")
    each_device.shell("input keyevent KEYCODE_ENTER")
    each_device.shell("input keyevent KEYCODE_ENTER")
    time.sleep(3)
    each_device.shell("uiautomator dump")
    xml_text = each_device.shell("cat /sdcard/window_dump.xml")
    # print(xml_text)
    # xml_text.split("")

    time.sleep(3)
    each_device.shell("rm /sdcard/window_dump.xml")
    time.sleep(3)

def show_toast_message(each_device, text):
    each_device.shell("input keyevent KEYCODE_MENU")
    if each_device.shell("pm list packages -f | grep com.rja.utility") == "":
        each_device.install("ShowToastMessage_NoDrawerIcon.apk")
    toast_text = "Hello! Connected ADB"
    if each_device.shell("pm list packages -f | grep com.rja.utility") != "":
        each_device.shell("am start -a android.intent.action.MAIN -e message \"" + toast_text + "\" -n com.rja.utility/.ShowToast")


def say_hello_button_action():
    for device in devices:
        screen_on(device)
        show_toast_message(device, "Hello! ADB Connected")


def test_touch_play(each_device):
    print("starting recording touch event")
    # each_device.shell("getevent /dev/input/event2 > /sdcard/touch_event_rec.txt")
    # time.sleep(5)
    # each_device.shell("^C")

    each_device.shell(
        "sendevent /dev/input/event2 1 330 1 ; sendevent /dev/input/event2 1 325 1 ; sendevent /dev/input/event2 3 53 562 ; sendevent /dev/input/event2 3 54 1778 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 559 ; sendevent /dev/input/event2 3 54 1736 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 557 ; sendevent /dev/input/event2 3 54 1660 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 562 ; sendevent /dev/input/event2 3 54 1560 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 573 ; sendevent /dev/input/event2 3 54 1455 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 588 ; sendevent /dev/input/event2 3 54 1308 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 1 330 0 ; sendevent /dev/input/event2 1 325 0 ; sendevent /dev/input/event2 0 0 0")
    time.sleep(1)
    each_device.shell(
        "sendevent /dev/input/event2 1 330 1 ; sendevent /dev/input/event2 1 325 1 ; sendevent /dev/input/event2 3 54 1099 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 54 1112 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 713 ; sendevent /dev/input/event2 3 54 1151 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 711 ; sendevent /dev/input/event2 3 54 1235 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 713 ; sendevent /dev/input/event2 3 54 1387 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 717 ; sendevent /dev/input/event2 3 54 1706 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 1 330 0 ; sendevent /dev/input/event2 1 325 0 ; sendevent /dev/input/event2 0 0 0")
    time.sleep(1)
    each_device.shell(
        "sendevent /dev/input/event2 1 330 1 ; sendevent /dev/input/event2 1 325 1 ; sendevent /dev/input/event2 3 53 785 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 767 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 713 ; sendevent /dev/input/event2 3 54 1472 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 608 ; sendevent /dev/input/event2 3 54 1485 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 463 ; sendevent /dev/input/event2 3 54 1512 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 316 ; sendevent /dev/input/event2 3 54 1552 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 189 ; sendevent /dev/input/event2 3 54 1603 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 37 ; sendevent /dev/input/event2 3 54 1664 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 1 330 0 ; sendevent /dev/input/event2 1 325 0 sendevent /dev/input/event2 0 0 0")
    time.sleep(1)
    each_device.shell(
        "sendevent /dev/input/event2 1 330 1 ; sendevent /dev/input/event2 1 325 1 ; sendevent /dev/input/event2 3 53 252 ; sendevent /dev/input/event2 3 54 1474 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 256 ; sendevent /dev/input/event2 3 54 1472 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 275 ; sendevent /dev/input/event2 3 54 1463 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 330 ; sendevent /dev/input/event2 3 54 1439 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 433 ; sendevent /dev/input/event2 3 54 1399 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 580 ; sendevent /dev/input/event2 3 54 1352 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 736 ; sendevent /dev/input/event2 3 54 1315 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 879 ; sendevent /dev/input/event2 3 54 1299 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 1000 ; sendevent /dev/input/event2 3 54 1302 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 1110 ; sendevent /dev/input/event2 3 54 1316 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 3 53 1264 ; sendevent /dev/input/event2 3 54 1335 ; sendevent /dev/input/event2 0 0 0 ; sendevent /dev/input/event2 1 330 0 ; sendevent /dev/input/event2 1 325 0 ; sendevent /dev/input/event2 0 0 0")
    time.sleep(1)

    print("end touch event play")


'''