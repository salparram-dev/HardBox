# utils/window_utils.py
import os
import tkinter as tk

def top_focus(win):
    win.attributes('-topmost', True)   # la pone encima de todo
    win.lift()
    win.focus_force()

# Ruta absoluta al icono, relativa a este archivo
ICO_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "images", "HARDBOX.ico")
)

def set_icon(win):
    """Pone el icono .ico en la ventana indicada."""
    if os.path.exists(ICO_PATH):
        try:
            win.iconbitmap(ICO_PATH)
        except Exception as e:
            print(f"No se pudo poner el icono: {e}")
    else:
        print(f"Icono no encontrado en: {ICO_PATH}")

def ensure_icon(win):
    """Pone el icono ahora y lo vuelve a poner tras inicializar la ventana."""
    set_icon(win)
    try:
        win.after_idle(lambda: set_icon(win))
    except Exception:
        pass