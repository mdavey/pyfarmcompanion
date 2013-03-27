import os
import sys
import ctypes
from ctypes import wintypes
import win32con
import time
import datetime
import winsound

byref = ctypes.byref
user32 = ctypes.windll.user32

HOTKEYS = {
    1: (win32con.VK_F3, win32con.MOD_WIN),
    2: (win32con.VK_F4, win32con.MOD_WIN),
    3: (win32con.VK_F1, win32con.MOD_SHIFT),
    4: (win32con.VK_F2, win32con.MOD_SHIFT)
}


def handle_win_f3():
    os.startfile(os.environ['TEMP'])


def handle_win_f4():
    user32.PostQuitMessage(0)

################

LAST_TIMESTAMP = False
RUNS = 0
ESSENCES = 0


def handle_shift_f1():
    record_run(True)


def handle_shift_f2():
    record_run(False)


def record_run(got_essence):
    global LAST_TIMESTAMP
    global RUNS
    global ESSENCES

    RUNS += 1
    if got_essence:
        ESSENCES += 1

    timestamp = int(time.time())
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    drop_rate = 0
    if ESSENCES > 0:
        drop_rate = (ESSENCES / float(RUNS)) * 100

    run_length = 0
    if LAST_TIMESTAMP is not False:
        run_length = timestamp - LAST_TIMESTAMP

    if got_essence:
        print 'DROP - %d - %s - %d/%d - %0.2f%% - %d' % (timestamp, date_str, ESSENCES, RUNS, drop_rate, run_length)
    else:
        print 'NULL - %d - %s - %d/%d - %0.2f%% - %d' % (timestamp, date_str, ESSENCES, RUNS, drop_rate, run_length)

    winsound.PlaySound('C:\Users\Matthew\Downloads\PhonerLite\CallWaiting.wav', winsound.SND_FILENAME)

    LAST_TIMESTAMP = timestamp


################


HOTKEY_ACTIONS = {
    1: handle_win_f3,
    2: handle_win_f4,
    3: handle_shift_f1,
    4: handle_shift_f2
}


# RegisterHotKey takes:
#  Window handle for WM_HOTKEY messages (None = this thread)
#  arbitrary id unique within the thread
#  modifiers (MOD_SHIFT, MOD_ALT, MOD_CONTROL, MOD_WIN)
#  VK code (either ord ('x') or one of win32con.VK_*)
for id, (vk, modifiers) in HOTKEYS.items ():
    print "Registering id", id, "for key", vk
    if not user32.RegisterHotKey (None, id, modifiers, vk):
        print "Unable to register id", id


# Home-grown Windows message loop: does
#  just enough to handle the WM_HOTKEY
#  messages and pass everything else along.
try:
    msg = wintypes.MSG()
    while user32.GetMessageA(byref(msg), None, 0, 0) != 0:
        if msg.message == win32con.WM_HOTKEY:
            action_to_take = HOTKEY_ACTIONS.get(msg.wParam)
            if action_to_take:
                action_to_take()

        user32.TranslateMessage(byref(msg))
        user32.DispatchMessageA(byref(msg))

finally:
    for id in HOTKEYS.keys():
        user32.UnregisterHotKey(None, id)
