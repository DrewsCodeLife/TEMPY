# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 16:55:27 2024

@author: drewm
"""

import sys
import threading
import queue
import tkinter as tk
import customtkinter as ctk
from script import runTest

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class MainApp(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.pack()
        
        self.queue = queue.Queue()
        
        self.post_process = tk.BooleanVar(value = False)
        self.Ucode = tk.BooleanVar(value = False)
        
        self.runButton = ctk.CTkButton(self, text="test", command=self.start_test)
        self.runButton.pack()
        
        self.dumbbox1 = ctk.CTkCheckBox(master = self, text = "Post Processing Plot", variable = self.post_process, onvalue = True, offvalue = False)
        self.dumbbox1.place(relx = .5, rely = .55, anchor = "w")
        
        self.uc_box = ctk.CTkCheckBox(master = self, text = "Calibration by Ucode", variable = self.Ucode, onvalue = True, offvalue = False)
        self.uc_box.place(relx = .5, rely = .6, anchor = "w")
        
        self.after(0, self.setup)
        
    def setup(self):
        self.winfo_toplevel().title("TEMPY")
        
        self.after(100, self.check_queue)
    
        
    def start_test(self):
        threading.Thread(target=self.run_test).start()
        
    def run_test(self):
        runTest(self.post_process.get(), self.Ucode.get())
        self.queue.put("yuh")
        
    def check_queue(self):
        while not self.queue.empty():
            result = self.queue.get()
            print(result)
        self.after(100, self.check_queue)
        
    def _quit(self):
        self.stop_simulation = True
        root.quit()
        root.destroy()

def main():
    root.mainloop()

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1600x900")
    
    app = MainApp(root)
    app.pack(side = "top", fill = "both", expand = True)
    
    root.protocol("WM_DELETE_WINDOW", app._quit)
    
    main()