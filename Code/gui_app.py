# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 13:59:27 2024

@author: Drew Mortenson
"""

import sys
import threading
import queue
import shared
import tkinter as tk
import customtkinter as ctk
import CTkMenuBar as ctkmb
from CTkListbox import CTkListbox
from TEMPY import run_simulation
from tooltipGen import CreateToolTip

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class TopLevelWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")
        
        self.attributes('-topmost', 1)

class MainApp(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.pack()
        
        self.winfo_toplevel().title("TEMPY")
        
        # Containers for file names, these will be passed to the run_simulation function to handle GUI file assignment
        self.solarFile = None
        self.windFile = None
        self.tempFile = None
        
        self.totalThickness = 3
        self.thicknessAC = 1
        self.thicknessBase = .5
        self.thicknessSubbase = 1
        self.thicknessSubgrade = self.totalThickness - self.thicknessAC - self.thicknessBase - self.thicknessSubbase
        
        # For now, we initialize
        self.thermo_depth = [0.025, 0.027, 0.029]
        self.depthList = CTkListbox(master = self)
        
        self.post_process = tk.BooleanVar(value = False) # run postprocess or not, True or False
        self.Ucode = tk.BooleanVar(value = False)        # this is used to run the sensitivity analysis for delta_e_1 and delta_e_6
        # Identifying the variables as BooleanVar enables connection to GUI, call with .get() to get standard boolean value for use.

        ### Constant input window

        self.constFrame = ctk.CTkFrame(self, width=500, height=200)
        self.constFrame.place(relx = .0025, rely = .035, anchor="nw")
        
        # Total thickness
        self.constFrame.ttEntry = ctk.CTkEntry(self.constFrame)
        self.constFrame.ttEntry.place(relx=0.0125, rely=0.05, anchor="nw")
        
        self.constFrame.ttEnter = ctk.CTkButton(self.constFrame, text="Update", command=self.updateTT)
        self.constFrame.ttEnter.place(relx=.3, rely=0.05, anchor="nw")
        
        self.constFrame.ttLabel = ctk.CTkLabel(self.constFrame, text=("Total pavement thickness: " + str(self.totalThickness)+ " m"))
        self.constFrame.ttLabel.place(relx=0.6, rely=0.05, anchor="nw")
        
        # Thickness AC (asphalt concrete)
        self.constFrame.tacEntry = ctk.CTkEntry(self.constFrame)
        self.constFrame.tacEntry.place(relx=0.0125, rely=.25, anchor="nw")
        
        self.constFrame.tacEnter = ctk.CTkButton(self.constFrame, text="Update", command=self.updateTAC)
        self.constFrame.tacEnter.place(relx=.3, rely=.25, anchor="nw")
        
        self.constFrame.tacLabel = ctk.CTkLabel(self.constFrame, text=("Total AC thickness:              " + str(self.thicknessAC) + " m"))
        self.constFrame.tacLabel.place(relx=0.6, rely=.25, anchor="nw")
        
        # Creating tooltip to let the user know that AC = Asphalt Concrete
        self.constFrame.ACtt = CreateToolTip(self.constFrame.tacLabel, "AC = Asphalt Concrete")
        
        # Thickness base
        self.constFrame.tbEntry = ctk.CTkEntry(self.constFrame)
        self.constFrame.tbEntry.place(relx=0.0125, rely=.45, anchor="nw")
        
        self.constFrame.tbEnter = ctk.CTkButton(self.constFrame, text="Update", command=self.updateTB)
        self.constFrame.tbEnter.place(relx=.3, rely=.45, anchor="nw")
        
        self.constFrame.tbLabel = ctk.CTkLabel(self.constFrame, text=("Total base thickness:          " + str(self.thicknessBase) + " m"))
        self.constFrame.tbLabel.place(relx=0.6, rely=.45, anchor="nw")
        
        # Thickness subbase
        self.constFrame.tsbEntry = ctk.CTkEntry(self.constFrame)
        self.constFrame.tsbEntry.place(relx=0.0125, rely=.65, anchor="nw")
        
        self.constFrame.tsbEnter = ctk.CTkButton(self.constFrame, text="Update", command=self.updateTSB)
        self.constFrame.tsbEnter.place(relx=.3, rely=.65, anchor="nw")
        
        self.constFrame.tsbLabel = ctk.CTkLabel(self.constFrame, text=("Total subbase thickness:   " + str(self.thicknessSubbase) + " m"))
        self.constFrame.tsbLabel.place(relx=0.6, rely=.65, anchor="nw")
        
        # Thickness subgrade
        self.constFrame.tsgLabel = ctk.CTkLabel(self.constFrame, text=("Subgrade thickness:            " + str(self.thicknessSubgrade) + " m"))
        self.constFrame.tsgLabel.place(relx=0.6, rely=.85, anchor="nw")
        
        ### End of constant input window

        ### Beginning of label definitions

        self.solarLabel = ctk.CTkLabel(self, text = "Solar Data")
        self.solarLabel.place(relx = .025, rely = .425, anchor = ctk.CENTER)
        
        self.solarFileLabel = ctk.CTkLabel(self, text = "No file...")
        self.solarFileLabel.place(relx = .15, rely = .425, anchor = "w")
        
        self.windLabel = ctk.CTkLabel(self, text = "Wind Data")
        self.windLabel.place(relx = .025, rely = .375, anchor = ctk.CENTER)
        
        self.windFileLabel = ctk.CTkLabel(self, text = "No file...")
        self.windFileLabel.place(relx = .15, rely = .375, anchor = "w")
        
        self.tempLabel = ctk.CTkLabel(self, text = "Temp Data")
        self.tempLabel.place(relx = .025, rely = .325, anchor = ctk.CENTER)
        
        self.tempFileLabel = ctk.CTkLabel(self, text = "No file...")
        self.tempFileLabel.place(relx = .15, rely = .325, anchor = "w")
        
        self.depthEntryLabel = ctk.CTkLabel(self, text = "Enter desired depth values")
        self.depthEntryLabel.place(relx = .7, rely = .21725, anchor = ctk.CENTER)
        
        ### End of label definitions
        
        ### Beginning of list box definitions
    
        self.depthList.place(relx = .8, rely = .3, anchor = ctk.CENTER)
        
        ### End of list box definitions
        
        ### Beginning of button definitions
        
        self.exitButton = ctk.CTkButton(master = self, text = "Exit", command = self.exit_function)
        self.exitButton.place(relx = .95, rely = 0.225, anchor = ctk.CENTER)
        
        self.simButton = ctk.CTkButton(master = self, text = "Run", command = self.simulation_button)
        self.simButton.place(relx = .5, rely = .5, anchor = ctk.CENTER)
        
        self.solarFileButton = ctk.CTkButton(master = self, text = "Select file...", command = lambda: self.selectfile(0))
        self.solarFileButton.place(relx = .1, rely = .425, anchor = ctk.CENTER)
        
        self.windFileButton = ctk.CTkButton(master = self, text = "Select file...", command = lambda: self.selectfile(1))
        self.windFileButton.place(relx = .1, rely = .375, anchor = ctk.CENTER)
        
        self.tempFileButton = ctk.CTkButton(master = self, text = "Select file...", command = lambda: self.selectfile(2))
        self.tempFileButton.place(relx = .1, rely = .325, anchor = ctk.CENTER)
        
        self.depthEntryButton = ctk.CTkButton(master = self, text = "Add", command = self.addDepth)
        self.depthEntryButton.place(relx = .7, rely = .282, anchor = ctk.CENTER)
        
        self.depthDeleteButton = ctk.CTkButton(master = self, text = "Delete selection", command = self.removeDepth)
        self.depthDeleteButton.place(relx = .7, rely = .314, anchor = ctk.CENTER)
        
        ### End of button definitions
        
        ### Beginning of input widget definitions
        #### Check boxes
        
        self.pp_box = ctk.CTkCheckBox(master = self, text = "Post Processing Plot", variable = self.post_process, onvalue = True, offvalue = False)
        self.pp_box.place(relx = .5, rely = .55, anchor = "w")
        
        self.uc_box = ctk.CTkCheckBox(master = self, text = "Calibration by Ucode", variable = self.Ucode, onvalue = True, offvalue = False)
        self.uc_box.place(relx = .5, rely = .6, anchor = "w")
        
        #### Number entry
        
        self.depthEntry = ctk.CTkEntry(master = self)
        self.depthEntry.place(relx = .7, rely = .25, anchor = ctk.CENTER)

        # Top-level menu bar
        self.mainMenuBar = ctkmb.CTkMenuBar(self)
        self.mmb_file = self.mainMenuBar.add_cascade("File")
        self.mmb_option = self.mainMenuBar.add_cascade("Options")
        self.mmb_settings = self.mainMenuBar.add_cascade("Settings")
        self.mmb_about = self.mainMenuBar.add_cascade("About")
        
        # Defining "File" drop down menu
        self.dd_file = ctkmb.CustomDropdownMenu(widget=self.mmb_file)
        self.dd_file.add_option(option="Open", command=lambda: print("Open"))
        self.dd_file.add_option(option="Save", command=lambda: print("Save"))
        
        # This adds a small line between the options listed above and the next option (or commonly used above a submenu)
        self.dd_file.add_separator()
        
        # Adding sub menu to file menu
        self.dd_file_submenu = self.dd_file.add_submenu("Export As")
        self.dd_file_submenu.add_option(option=".TXT", command=lambda: print("TXT"))
        self.dd_file_submenu.add_option(option=".PDF", command=lambda: print("PDF"))
        
        # Defining "Option" drop down menu
        self.dd_option = ctkmb.CustomDropdownMenu(widget=self.mmb_option)
        self.dd_option.add_option(option="Cut")
        self.dd_option.add_option(option="Copy")
        self.dd_option.add_option(option="Paste")

        self.dd_help = ctkmb.CustomDropdownMenu(widget=self.mmb_settings)
        self.dd_help.add_option(option="Preferences")
        self.dd_help.add_option(option="Update")
        
        self.dd_about = ctkmb.CustomDropdownMenu(widget=self.mmb_about)
        self.dd_about.add_option(option="Hello World")
    
    def updateTSB(self):
        try:
            self.thicknessSubbase = float(self.constFrame.tsbEntry.get())
            
            self.thicknessSubgrade = self.totalThickness - self.thicknessAC - self.thicknessBase - self.thicknessSubbase
            
            self.constFrame.tsbLabel.configure(text=("Total subbase thickness:   " + str(self.thicknessSubbase) + " m"))
            self.constFrame.tsgLabel.configure(text=("Subgrade thickness:            " + str(self.thicknessSubgrade) + " m"))
        except ValueError:
            self.popup = TopLevelWindow(self)
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(master = self.popup,
                                                     text = "Oops! You tried to enter an invalid value for the total thickness. Ensure all values are entered as numeric",
                                                     wraplength=300, justify="center")
            self.popup.warningMessage.place(relx = .5, rely = .5, anchor = ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(master = self.popup, text = "Close pop-up window", command = lambda: self.closePopup(self.popup))
            self.popup.exitPopup.place(relx = .5, rely = .7, anchor = ctk.CENTER)
            
            self.popup.update()
    
    def updateTB(self):
        try:
            self.thicknessBase = float(self.constFrame.tbEntry.get())
            
            self.thicknessSubgrade = self.totalThickness - self.thicknessAC - self.thicknessBase - self.thicknessSubbase
            
            self.constFrame.tbLabel.configure(text=("Total base thickness:          " + str(self.thicknessBase) + " m"))
            self.constFrame.tsgLabel.configure(text=("Subgrade thickness:            " + str(self.thicknessSubgrade) + " m"))
        except ValueError:
            self.popup = TopLevelWindow(self)
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(master = self.popup,
                                                     text = "Oops! You tried to enter an invalid value for the total thickness. Ensure all values are entered as numeric",
                                                     wraplength=300, justify="center")
            self.popup.warningMessage.place(relx = .5, rely = .5, anchor = ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(master = self.popup, text = "Close pop-up window", command = lambda: self.closePopup(self.popup))
            self.popup.exitPopup.place(relx = .5, rely = .7, anchor = ctk.CENTER)
            
            self.popup.update()
    
    def updateTAC(self):
        try:
            self.thicknessAC = float(self.constFrame.tacEntry.get())
            
            self.thicknessSubgrade = self.totalThickness - self.thicknessAC - self.thicknessBase - self.thicknessSubbase
            
            self.constFrame.tacLabel.configure(text=("Total AC thickness:               " + str(self.thicknessAC) + " m"))
            self.constFrame.tsgLabel.configure(text=("Subgrade thickness:            " + str(self.thicknessSubgrade) + " m"))
        except ValueError:
            self.popup = TopLevelWindow(self)
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(master = self.popup,
                                                     text = "Oops! You tried to enter an invalid value for the total thickness. Ensure all values are entered as numeric",
                                                     wraplength=300, justify="center")
            self.popup.warningMessage.place(relx = .5, rely = .5, anchor = ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(master = self.popup, text = "Close pop-up window", command = lambda: self.closePopup(self.popup))
            self.popup.exitPopup.place(relx = .5, rely = .7, anchor = ctk.CENTER)
            
            self.popup.update()
    
    def updateTT(self): # Update Total Thickness
        try:
            self.totalThickness = float(self.constFrame.ttEntry.get())
            
            self.thicknessSubgrade = self.totalThickness - self.thicknessAC - self.thicknessBase - self.thicknessSubbase
            
            self.constFrame.ttLabel.configure(text=("Total pavement thickness: " + str(self.totalThickness) + " m"))
            self.constFrame.tsgLabel.configure(text=("Subgrade thickness:            " + str(self.thicknessSubgrade) + " m"))
        except ValueError:
            self.popup = TopLevelWindow(self)
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(master = self.popup,
                                                     text = "Oops! You tried to enter an invalid value for the total thickness. Ensure all values are entered as numeric",
                                                     wraplength=300, justify="center")
            self.popup.warningMessage.place(relx = .5, rely = .5, anchor = ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(master = self.popup, text = "Close pop-up window", command = lambda: self.closePopup(self.popup))
            self.popup.exitPopup.place(relx = .5, rely = .7, anchor = ctk.CENTER)
            
            self.popup.update()
        
    
    def removeDepth(self):
        selected_index = self.depthList.curselection()
        if selected_index is not None:
            index = int(selected_index)
            self.thermo_depth.pop(index)
            self.update_depthlist()
        else:
            print("Nothing selected") ### IN THE FUTURE, ADD POP UP WINDOW TO WARN
    
    def addDepth(self):
        if len(self.thermo_depth) > 10:
            # Generate a pop-up asking which value the user wants to remove, if any (option to back out with no change)
            self.popup = TopLevelWindow(self)
            self.popup.title("Too many depths!")
        else:
            try:
                value = float(self.depthEntry.get())
                self.thermo_depth.append(value)
            except ValueError:
                self.popup = TopLevelWindow(self)
                self.popup.title("Invalid selection!")

                self.popup.warningMessage = ctk.CTkLabel(master = self.popup,
                                                         text = "Oops! You tried to enter an invalid value for the depth list. Ensure all depth values are entered as numeric",
                                                         wraplength=300, justify="center")
                self.popup.warningMessage.place(relx = .5, rely = .5, anchor = ctk.CENTER)
                
                self.popup.exitPopup = ctk.CTkButton(master = self.popup, text = "Close pop-up window", command = lambda: self.closePopup(self.popup))
                self.popup.exitPopup.place(relx = .5, rely = .7, anchor = ctk.CENTER)
                
                self.popup.update()
            # except value > max depth
            ### ADD EXCEPTION
        self.update_depthlist()
    
    def stopSim(self, popup):
        shared.endEarly.set()
        popup.destroy()
        
    def closePopup(self, popup):
        popup.destroy()
    
    def exit_function(self):
        self.post_process = None
        self.Ucode = None
        shared.endEarly.set()
        self.parent.quit()
        self.parent.destroy()
        sys.exit()
        
    def simulation_button(self):
        if not shared.running.is_set() \
            and self.solarFile is not None \
            and self.windFile is not None \
            and self.tempFile is not None:
            shared.running.set()
            self.simulation_thread = threading.Thread(target = self.run_simulation_in_thread, daemon=True)
            self.post_processing = self.post_process.get()
            self.Ucoding = self.Ucode.get()
            self.simulation_thread.start()
        elif shared.running.is_set():
            # The simulation is already running, we should notify the user to be patient
            self.popup = TopLevelWindow(self)
            self.popup.title("Please wait!")
            
            self.popup.pleaseWait = ctk.CTkLabel(self.popup, text="Please wait while the simulation is running (popup will close). Running the simulation more than once at a time is not advised due to hardware requirements",
                                                 wraplength=300, justify="center")
            self.popup.pleaseWait.pack()
        else:
            self.popup = TopLevelWindow(self)
            self.popup.title("Missing data!")
            
            needed = ""
            
            if self.tempFile is None:
                needed = "\nTemp Data "
            if self.windFile is None:
                needed = needed + "\nWind data "
            if self.solarFile is None:
                needed = needed + "\nSolar data "
            
            
            self.popup.pleaseWait = ctk.CTkLabel(self.popup, text=("You forgot to add the following data sets: " + needed),
                                                 wraplength=300, justify="center")
            self.popup.pleaseWait.pack()
            
    
    def run_simulation_in_thread(self):
        self.popup = TopLevelWindow(self)
        self.popup.title("Simulation running, please wait")
        
        self.popup.pleaseWait = ctk.CTkLabel(self.popup, text="Please wait while the simulation is running (popup will close)")
        self.popup.pleaseWait.pack()
        
        solarFile = self.solarFile
        windFile = self.windFile
        tempFile = self.tempFile
        run_simulation(self.post_processing, self.Ucoding, # Check boxes, if these are true than we run post processing and Ucode calibration respectively
                       solarFile = solarFile, windFile = windFile, tempFile = tempFile, # File paths for the data
                       Thermo_depth=self.thermo_depth, # Share the current thermo_depth list with the function
                       thickness_AC = self.thicknessAC, thickness_Base = self.thicknessBase, thickness_subbase = self.thicknessSubbase, thickness_subgrade = self.thicknessSubgrade
                       )
        
        shared.running.clear()
        self.closePopup(self.popup)
            
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
        if shared.running.is_set():
            self.blockSelectFile()
        else:
            if data == 0:
                self.solarFile = ctk.filedialog.askopenfilename()
                if  self.solarFile[len(self.solarFile) - 5:] == ".xlsx":
                    self.solarFileLabel.configure(text = self.solarFile)
                else:
                    self.solarFile = None
                    self.popup = TopLevelWindow(self)
                    self.popup.title("Bad file input, expected .xlsx")
                    
                    self.popup.warning = ctk.CTkLabel(self.popup, text="The file you provided was not a .xlsx file, please double check file format and resubmit",
                                                      wraplength=300, justify="center")
                    self.popup.warning.pack()
                    
            elif data == 1:
                self.windFile = ctk.filedialog.askopenfilename()
                if self.windFile[len(self.windFile) - 5:] == ".xlsx":
                    self.windFileLabel.configure(text = self.windFile)
                else:
                    self.windFile = None
                    self.popup = TopLevelWindow(self)
                    self.popup.title("Bad file input, expected .xlsx")
                    
                    self.popup.warning = ctk.CTkLabel(self.popup, text="The file you provided was not a .xlsx file, please double check file format and resubmit.",
                                                      wraplength=300, justify="center")
                    self.popup.warning.pack()
            else:
                self.tempFile = ctk.filedialog.askopenfilename()
                if self.tempFile[len(self.tempFile) - 5:] == ".xlsx":
                    self.tempFileLabel.configure(text = self.tempFile)
                else:
                    self.tempFile = None
                    self.popup = TopLevelWindow(self)
                    self.popup.title("Bad file input, expected .xlsx")
                    
                    self.popup.warning = ctk.CTkLabel(self.popup, text="The file you provided was not a .xlsx file, please double check file format and resubmit.",
                                                      wraplength=300, justify="center")
                    self.popup.warning.pack()

    def update_depthlist(self):
        # Clear the listbox
        self.depthList.delete("all")
        # Repopulate with the values in thermo_depth
        for depth in self.thermo_depth:
            self.depthList.insert(ctk.END, depth)
        
    def _quit(self):
        shared.endEarly.set()
        root.quit()
        root.destroy()

def main():
    # Populate the values in our depth list
    app.update_depthlist()

    root.mainloop()

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1600x900")
    
    app = MainApp(root)
    app.pack(side = "top", fill = "both", expand = True)
    
    root.protocol("WM_DELETE_WINDOW", app._quit)
    
    main()
