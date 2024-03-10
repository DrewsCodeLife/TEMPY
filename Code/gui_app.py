# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 13:59:27 2024

@author: Drew Mortenson
"""

import sys
import threading
import queue
import customtkinter as ctk
from CTkListbox import *
from tkinter import BooleanVar
from simulation import run_simulation

class TopLevelWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")

class MainApp(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.pack()
        
        self.after(0, self.setup)
        
    def setup(self):
        self.winfo_toplevel().title("CRPPP")
        
        # Containers for file names, these will be passed to the run_simulation function to handle GUI file assignment
        self.solarFile = None
        self.windFile = None
        self.tempFile = None
        
        self.simulation_thread = threading.Thread(target = self.run_simulation_in_thread)
        
        self.post_process = BooleanVar(value = False) # run postprocess or not, True or False
        self.Ucode = BooleanVar(value = False)        # this is used to run the sensitivity analysis for delta_e_1 and delta_e_6
        # Identifying the variables as BooleanVar enables connection to GUI, call with .get() to get standard boolean value for use.
        
        self.stop_simulation = False
        self.thermo_depth = None

        ### Beginning of label definitions

        self.solarLabel = ctk.CTkLabel(self, text = "Solar Data")
        self.solarLabel.place(relx = .025, rely = .025, anchor = ctk.CENTER)
        
        self.solarFileLabel = ctk.CTkLabel(self, text = "No file...")
        self.solarFileLabel.place(relx = .15, rely = .025, anchor = "w")
        
        self.windLabel = ctk.CTkLabel(self, text = "Wind Data")
        self.windLabel.place(relx = .025, rely = .075, anchor = ctk.CENTER)
        
        self.windFileLabel = ctk.CTkLabel(self, text = "No file...")
        self.windFileLabel.place(relx = .15, rely = .075, anchor = "w")
        
        self.tempLabel = ctk.CTkLabel(self, text = "Temp Data")
        self.tempLabel.place(relx = .025, rely = .125, anchor = ctk.CENTER)
        
        self.tempFileLabel = ctk.CTkLabel(self, text = "No file...")
        self.tempFileLabel.place(relx = .15, rely = .125, anchor = "w")
        
        self.depthEntryLabel = ctk.CTkLabel(self, text = "Enter desired depth values")
        self.depthEntryLabel.place(relx = .7, rely = .01725, anchor = ctk.CENTER)
        
        ### End of label definitions
        
        ### Beginning of list box definitions
        
        self.depthList = CTkListbox(master = self) #### NEED TO ADD A COMMAND TO HAPPEN WHEN ELEMENT IS CLICKED (delete item pop up)
        self.depthList.place(relx = .8, rely = .1, anchor = ctk.CENTER)
        
        ### End of list box definitions
        
        ### Beginning of button definitions
        
        self.exitButton = ctk.CTkButton(master = self, text = "Exit", command = self.exit_function)
        self.exitButton.place(relx = .95, rely = 0.025, anchor = ctk.CENTER)
        
        self.simButton = ctk.CTkButton(master = self, text = "Run", command = self.simulation_button)
        self.simButton.place(relx = .5, rely = .5, anchor = ctk.CENTER)
        
        self.solarFileButton = ctk.CTkButton(master = self, text = "Select file...", command = lambda: self.selectfile(0))
        self.solarFileButton.place(relx = .1, rely = .025, anchor = ctk.CENTER)
        
        self.windFileButton = ctk.CTkButton(master = self, text = "Select file...", command = lambda: self.selectfile(1))
        self.windFileButton.place(relx = .1, rely = .075, anchor = ctk.CENTER)
        
        self.tempFileButton = ctk.CTkButton(master = self, text = "Select file...", command = lambda: self.selectfile(2))
        self.tempFileButton.place(relx = .1, rely = .125, anchor = ctk.CENTER)
        
        self.depthEntryButton = ctk.CTkButton(master = self, text = "Add", command = self.addDepth)
        self.depthEntryButton.place(relx = .7, rely = .08, anchor = ctk.CENTER)
        
        ### End of button definitions
        
        ### Beginning of input widget definitions
        #### Check boxes
        
        self.pp_box = ctk.CTkCheckBox(master = self, text = "Post Processing?", variable = self.post_process, onvalue = True, offvalue = False)
        self.pp_box.place(relx = .5, rely = .55, anchor = "w")
        
        self.uc_box = ctk.CTkCheckBox(master = self, text = "Ucode?", variable = self.Ucode, onvalue = True, offvalue = False)
        self.uc_box.place(relx = .5, rely = .6, anchor = "w")
        
        #### Number entry
        
        self.depthEntry = ctk.CTkEntry(master = self)
        self.depthEntry.place(relx = .7, rely = .05, anchor = ctk.CENTER)
        
        self.queue = queue.Queue()
    
    def removeDepth(self):
        # called when user selects a value in the listbox, should generate a pop-up which confirms that the user wants to remove it
        self.popup = TopLevelWindow(self)
        self.popup.title("Remove depth")
        #### NOT FINISHED
    
    def addDepth(self):
        if len(self.thermo_depth) > 10:
            # Generate a pop-up asking which value the user wants to remove, if any (option to back out with no change)
            self.popup = TopLevelWindow(self)
            self.popup.title("Too many depths!")
        else:
            value = float(self.depthEntry.get())
            self.thermo_depth.append(value)
            self.depthEntry.delete(0, ctk.END)
    
    def stopSim(self, popup):
        self.stop_simulation = True
        popup.destroy()
        
    def closePopup(self, popup):
        popup.destroy()
    
    def exit_function(self):
        self.stop_simulation = True
        self.post_process = None
        self.Ucode = None
        self.parent.destroy()
        sys.exit()
        
    def simulation_button(self):
        # We initialize a separate thread for the simulation to run on, this enables the GUI to continue working while the simulation is running
        self.simulation_thread.start()
        self.after(100, self.check_queue)
    
    def run_simulation_in_thread(self):
        solarFile = self.solarFile
        windFile = self.windFile
        tempFile = self.tempFile
        run_simulation(self.post_process.get(), self.Ucode.get(), should_stop=lambda: self.stop_simulation, solarFile = solarFile, windFile = windFile, tempFile = tempFile)
        self.queue.put("Simulation Finished")
        
    def check_queue(self):
        try:
            message = self.queue.get_nowait()
            if message == "Simulation Finished":
                pass
        except queue.Empty:
            self.after(100, self.check_queue)
            
    def blockSelectFile(self):
        self.popup = TopLevelWindow(self)
        self.popup.title("Oh No!")
        
        self.popup.choice = ctk.CTkLabel(self.popup, text = "Would you like to end the simulation and choose new data?")
        self.popup.choice.place(relx = .5, rely = .3, anchor = ctk.CENTER)
        
        self.popup.buttonEnd = ctk.CTkButton(master = self.popup, text = "End simulation", command = lambda: self.stopSim(self.popup))
        self.popup.buttonEnd.place(relx = .25, rely = .7, anchor = ctk.CENTER)
        
        self.popup.buttonContinue = ctk.CTkButton(master = self.popup, text = "Continue simulation", command = lambda: self.closePopup(self.popup))
        self.popup.buttonContinue.place(relx = .75, rely = .7, anchor = ctk.CENTER)
        
        self.popup.update()
    
    def selectfile(self, data):
        if self.simulation_thread.is_alive():
            self.blockSelectFile()
        else:
            if data == 0:
                self.solarFile = ctk.filedialog.askopenfilename()
                self.solarFileLabel.configure(text = self.solarFile)
            elif data == 1:
                self.windFile = ctk.filedialog.askopenfilename()
                self.windFileLabel.configure(text = self.windFile)
            else:
                self.tempFile = ctk.filedialog.askopenfilename()
                self.tempFileLabel.configure(text = self.tempFile)

    
if __name__ == "__main__":
    
    root = ctk.CTk()
    root.geometry("1600x900")
    MainApp(root).pack(side = "top", fill = "both", expand = True)
    

    
    root.mainloop()