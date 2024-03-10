# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 13:59:27 2024

@author: Drew Mortenson
"""

import sys
import threading
import queue
import customtkinter as ctk
from tkinter import BooleanVar
from simulation import run_simulation

class MainApp(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        self.post_process = BooleanVar(value = False) # run postprocess or not, True or False
        self.Ucode = BooleanVar(value = False)        # this is used to run the sensitivity analysis for delta_e_1 and delta_e_6
        # Identifying the variables as BooleanVar enables connection to GUI, call with .get() to get standard boolean value for use.
        
        self.stop_simulation = False
        
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.label = ctk.CTkLabel(self, text = "Hello, world!")
        self.label.pack()
        
        self.exitButton = ctk.CTkButton(master = self, text = "Exit", command = self.exit_function)
        self.exitButton.place(relx = .95, rely = 0.025, anchor = ctk.CENTER)
        
        self.simButton = ctk.CTkButton(master = self, text = "Run", command = self.simulation_button)
        self.simButton.place(relx = .5, rely = .5, anchor = ctk.CENTER)
        
        self.pp_box = ctk.CTkCheckBox(master = self, text = "Post Processing?", variable = self.post_process, onvalue = True, offvalue = False)
        self.pp_box.place(relx = .5, rely = .55, anchor = "w")
        
        self.uc_box = ctk.CTkCheckBox(master = self, text = "Ucode?", variable = self.Ucode, onvalue = True, offvalue = False)
        self.uc_box.place(relx = .5, rely = .6, anchor = "w")
        
        self.queue = queue.Queue()
    
    def exit_function(self):
        self.stop_simulation = True
        self.parent.destroy()
        sys.exit()
        
    def simulation_button(self):
        # We initialize a separate thread for the simulation to run on, this enables the GUI to continue working while the simulation is running
        simulation_thread = threading.Thread(target = self.run_simulation_in_thread)
        simulation_thread.start()
        self.after(100, self.check_queue)
    
    def run_simulation_in_thread(self):
        while not self.stop_simulation:
            run_simulation(self.post_process.get(), self.Ucode.get())
            pass
        self.queue.put("Simulation Finished")
        
    def check_queue(self):
        try:
            message = self.queue.get_nowait()
            if message == "Simulation Finished":
                self.label.config(text = "Simulation Finished!")
                pass
        except queue.Empty:
            self.after(100, self.check_queue)
        
if __name__ == "__main__":
    
    root = ctk.CTk()
    root.geometry("1600x900")
    MainApp(root).pack(side = "top", fill = "both", expand = True)
    

    
    root.mainloop()