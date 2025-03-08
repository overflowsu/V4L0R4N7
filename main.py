import json, time, threading, keyboard, sys
import win32api
import win32gui
from ctypes import WinDLL
import numpy as np
from mss import mss as mss_module
import tkinter as tk
from random import choice

# Windows API
user32, kernel32, shcore = (
    WinDLL("user32", use_last_error=True),
    WinDLL("kernel32", use_last_error=True),
    WinDLL("shcore", use_last_error=True),
)
shcore.SetProcessDpiAwareness(2)
WIDTH, HEIGHT = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

ZONE = 5
GRAB_ZONE = (
    int(WIDTH / 2 - ZONE),
    int(HEIGHT / 2 - ZONE),
    int(WIDTH / 2 + ZONE),
    int(HEIGHT / 2 + ZONE),
)

class TriggerBot:
    def __init__(self):
        self.sct = mss_module()
        self.triggerbot = False
        self.exit_program = False 
        self.one_bullet_mode = False
        self.current_key = "k"
        self.captureline_enabled = False

        with open('config.json') as json_file:
            data = json.load(json_file)

        try:
            self.trigger_hotkey = int(data["trigger_hotkey"], 16)
            self.trigger_delay = data["trigger_delay"]
            self.base_delay = data["base_delay"]
            self.color_tolerance = data["color_tolerance"]
            self.R, self.G, self.B = (250, 100, 250)  # Mor
        except:
            sys.exit()

        self.setup_overlay()

    def setup_overlay(self):
        self.root = tk.Tk()
        self.root.attributes("-topmost", True)
        self.root.geometry(f"250x170+50+50")
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.7)
        self.root.configure(bg="black")

        self.title_label = tk.Label(self.root, text="OverFlow.Su V1.0", fg="aqua", bg="black", font=("Arial", 12, "bold"))
        self.title_label.pack(pady=5)
        
        self.status_label = tk.Label(self.root, text="Status: Disabled", fg="red", bg="black", font=("Arial", 10))
        self.status_label.pack(pady=5)

        self.key_label = tk.Label(self.root, text=f"Shoot Key: {self.current_key}", fg="white", bg="black", font=("Arial", 10))
        self.key_label.pack(pady=5)

        self.captureline_label = tk.Label(self.root, text="CaptureLine: Disabled", fg="white", bg="black", font=("Arial", 10))
        self.captureline_label.pack(pady=5)
        
        self.mode_label = tk.Label(self.root, text="Shoot Mode: Spread", fg="white", bg="black", font=("Arial", 10))
        self.mode_label.pack(pady=5)
        
        self.root.update()

    def update_overlay(self):
        self.status_label.config(text=f"Status: {'Enabled' if self.triggerbot else 'Disabled'}", fg="green" if self.triggerbot else "red")
        self.key_label.config(text=f"Shoot Key: {self.current_key}")
        self.captureline_label.config(text=f"CaptureLine: {'Enabled' if self.captureline_enabled else 'Disabled'}")
        self.mode_label.config(text=f"Mod: {'One Bullet' if self.one_bullet_mode else 'Spread'}")
        self.root.update()

    def searcherino(self):
        img = np.array(self.sct.grab(GRAB_ZONE))o
        pixels = img.reshape(-1, 4)
        color_mask = (
            (pixels[:, 0] > self.R - self.color_tolerance) & (pixels[:, 0] < self.R + self.color_tolerance) &
            (pixels[:, 1] > self.G - self.color_tolerance) & (pixels[:, 1] < self.G + self.color_tolerance) &
            (pixels[:, 2] > self.B - self.color_tolerance) & (pixels[:, 2] < self.B + self.color_tolerance)
        )
        if self.triggerbot and np.any(color_mask):
            time.sleep(self.base_delay * (1 + self.trigger_delay / 100.0))
            keyboard.press_and_release(self.current_key)
            if self.one_bullet_mode:
                time.sleep(1)

    def toggle(self):
        if keyboard.is_pressed("f10"):  
            self.triggerbot = not self.triggerbot
            self.update_overlay()
            time.sleep(0.2)

        if keyboard.is_pressed("insert"):  
            self.current_key = choice(["k", "o", "p"])
            self.update_overlay()
            time.sleep(0.2)

        if keyboard.is_pressed("home"):  
            self.captureline_enabled = not self.captureline_enabled
            self.update_overlay()
            time.sleep(0.2)

        if keyboard.is_pressed("end"):  
            self.one_bullet_mode = not self.one_bullet_mode
            self.update_overlay()
            time.sleep(0.2)

        if keyboard.is_pressed("ctrl+shift+x"):  
            self.exit_program = True
            sys.exit()

        # F12 tuşuna basıldığında arayüzü gizle veya göster
        if keyboard.is_pressed("f12"):
            self.toggle_overlay()
            time.sleep(0.2)

    def toggle_overlay(self):
        # Arayüzün görünürlüğünü kontrol et
        if self.root.winfo_ismapped():  # Eğer pencere açık ise
            self.root.withdraw()  # Pencereyi gizle
        else:
            self.root.deiconify()  # Pencereyi göster

    def draw_captureline(self):
        if self.captureline_enabled:
            hwnd = user32.GetDesktopWindow()
            hdc = user32.GetDC(hwnd)
            win32gui.MoveToEx(hdc, WIDTH // 2 - ZONE, HEIGHT // 2 - ZONE)
            win32gui.LineTo(hdc, WIDTH // 2 + ZONE, HEIGHT // 2 - ZONE)
            win32gui.LineTo(hdc, WIDTH // 2 + ZONE, HEIGHT // 2 + ZONE)
            win32gui.LineTo(hdc, WIDTH // 2 - ZONE, HEIGHT // 2 + ZONE)
            win32gui.LineTo(hdc, WIDTH // 2 - ZONE, HEIGHT // 2 - ZONE)
            user32.ReleaseDC(hwnd, hdc)

    def starterino(self):
        while not self.exit_program:
            self.toggle()
            if self.triggerbot:
                self.searcherino()
            if self.captureline_enabled:
                self.draw_captureline()
            time.sleep(0.05)

TriggerBot().starterino()
