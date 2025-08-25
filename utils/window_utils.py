# utils/window_utils.py

def top_focus(win):
    win.attributes('-topmost', True)   # la pone encima de todo
    win.lift()
    win.focus_force()