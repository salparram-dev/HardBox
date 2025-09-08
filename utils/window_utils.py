# utils/window_utils.py
import os
import tkinter as tk

def top_focus(win):
    win.attributes('-topmost', True)   # la pone encima de todo
    win.lift()
    win.focus_force()

ICO_PATH = os.path.abspath("./assets/images/HARDBOX.ico")

def set_icon(win):
    """Pone el icono .ico en la ventana indicada."""
    if os.path.exists(ICO_PATH):
        try:
            win.iconbitmap(ICO_PATH)
        except Exception as e:
            print(f"No se pudo poner el icono: {e}")

def ensure_icon(win):
    """Pone el icono ahora y lo vuelve a poner tras inicializar la ventana."""
    set_icon(win)
    try:
        win.after_idle(lambda: set_icon(win))
    except Exception:
        pass