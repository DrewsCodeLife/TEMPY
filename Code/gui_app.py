# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 13:59:27 2024

@author: Drew Mortenson
"""

import sys
import threading
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
        self.solarFileShort = None
        self.windFileShort = None
        self.tempFileShort = None
        
        self.totalThickness = 3
        self.thicknessAC = 1
        self.thicknessBase = .5
        self.thicknessSubbase = 1
        self.thicknessSubgrade = self.totalThickness - self.thicknessAC - self.thicknessBase - self.thicknessSubbase
        
        # For now, we initialize
        self.thermo_depth = [0]
        
        self.post_process = tk.BooleanVar(value = False) # run postprocess or not, True or False
        self.Ucode = tk.BooleanVar(value = False)        # this is used to run the sensitivity analysis for delta_e_1 and delta_e_6
        # Identifying the variables as BooleanVar enables connection to GUI, call with .get() to get standard boolean value for use.
        
        ### Middle (dividing column)
        # This must be defined prior to the left/right side frame(s) to ensure it is on top
        self.middleCol = ctk.CTkFrame(self, width=10, height=720, fg_color="black")
        self.middleCol.place(relx=.5, rely=0, anchor="n")
        ###

        ### Left side frame
        self.leftFrame = ctk.CTkFrame(self, width=635, height=720)
        self.leftFrame.place(relx=0, rely=0, anchor="nw")
        ###
        
        ### Project name/folder frame
        self.leftFrame.projectFrame = ctk.CTkFrame(self.leftFrame, width=500, height=125)
        self.leftFrame.projectFrame.place(relx=.01, rely=.13, anchor="w")
        
        self.leftFrame.projectFrame.projName = ctk.CTkLabel(self.leftFrame.projectFrame, text=shared.proj_name, wraplength=500, font=("Segoe UI", 20, "bold"))
        self.leftFrame.projectFrame.projName.place(relx=.005, rely=0, anchor="nw")
        self.leftFrame.projectFrame.nameEntry = ctk.CTkEntry(self.leftFrame.projectFrame, placeholder_text="Enter a project name")
        self.leftFrame.projectFrame.nameEntry.place(relx=.005, rely=.45, anchor="nw")
        self.leftFrame.projectFrame.nameSubmit = ctk.CTkButton(self.leftFrame.projectFrame, text="Update project name", command=self.updateName)
        self.leftFrame.projectFrame.nameSubmit.place(relx=.005, rely=.95, anchor="sw")
        
        self.leftFrame.projectFrame.projFolder = ctk.CTkLabel(self.leftFrame.projectFrame, text="Project Folder: " + shared.proj_folder)
        self.leftFrame.projectFrame.projFolder.place(relx=.7, rely=.625, anchor=ctk.CENTER)
        self.leftFrame.projectFrame.folderSubmit = ctk.CTkButton(self.leftFrame.projectFrame, text="Choose new project folder", command=lambda: self.selectfile(3))
        self.leftFrame.projectFrame.folderSubmit.place(relx=.7, rely=.85, anchor=ctk.CENTER)
        ### End of project name/folder frame

        ### Constant input frame
        self.leftFrame.constFrame = ctk.CTkFrame(self.leftFrame, width=500, height=125)
        self.leftFrame.constFrame.place(relx=.01, rely=.325, anchor="w")
        
        # Thickness AC (asphalt concrete)
        self.leftFrame.constFrame.tacEntry = ctk.CTkEntry(self.leftFrame.constFrame)
        self.leftFrame.constFrame.tacEntry.place(relx=.005, rely=.05, anchor="nw")
        self.leftFrame.constFrame.tacEnter = ctk.CTkButton(self.leftFrame.constFrame, text="Update", command=self.updateTAC)
        self.leftFrame.constFrame.tacEnter.place(relx=.3, rely=.05, anchor="nw")
        self.leftFrame.constFrame.tacLabel = ctk.CTkLabel(self.leftFrame.constFrame, text=("Total AC thickness:              " + str(self.thicknessAC) + " m"))
        self.leftFrame.constFrame.tacLabel.place(relx=.6, rely=.05, anchor="nw")
        
        # Creating tooltip to let the user know that AC = Asphalt Concrete
        self.leftFrame.constFrame.ACtt = CreateToolTip(self.leftFrame.constFrame.tacLabel, "AC = Asphalt Concrete")
        
        # Thickness base
        self.leftFrame.constFrame.tbEntry = ctk.CTkEntry(self.leftFrame.constFrame)
        self.leftFrame.constFrame.tbEntry.place(relx=.005, rely=.5, anchor="w")
        self.leftFrame.constFrame.tbEnter = ctk.CTkButton(self.leftFrame.constFrame, text="Update", command=self.updateTB)
        self.leftFrame.constFrame.tbEnter.place(relx=.3, rely=.5, anchor="w")
        self.leftFrame.constFrame.tbLabel = ctk.CTkLabel(self.leftFrame.constFrame, text=("Total base thickness:          " + str(self.thicknessBase) + " m"))
        self.leftFrame.constFrame.tbLabel.place(relx=.6, rely=.5, anchor="w")
        
        # Thickness subbase
        self.leftFrame.constFrame.tsbEntry = ctk.CTkEntry(self.leftFrame.constFrame)
        self.leftFrame.constFrame.tsbEntry.place(relx=.005, rely=.95, anchor="sw")
        self.leftFrame.constFrame.tsbEnter = ctk.CTkButton(self.leftFrame.constFrame, text="Update", command=self.updateTSB)
        self.leftFrame.constFrame.tsbEnter.place(relx=.3, rely=.95, anchor="sw")
        self.leftFrame.constFrame.tsbLabel = ctk.CTkLabel(self.leftFrame.constFrame, text=("Total subbase thickness:   " + str(self.thicknessSubbase) + " m"))
        self.leftFrame.constFrame.tsbLabel.place(relx=.6, rely=.95, anchor="sw")
        ### End of constant input frame

        ### Depth selection frame
        self.leftFrame.depthFrame = ctk.CTkFrame(self.leftFrame, width=500, height=125)
        self.leftFrame.depthFrame.place(relx=.01, rely=.521, anchor="w")
        
        self.leftFrame.depthFrame.depthList = CTkListbox(self.leftFrame.depthFrame, height=50)
        self.leftFrame.depthFrame.depthList.place(relx=0.0125, rely=.95, anchor="sw")
        self.leftFrame.depthFrame.depthEntryLabel = ctk.CTkLabel(self.leftFrame.depthFrame, text="Enter depths (m) for temperature profile", font=("Segoe UI", 16))
        self.leftFrame.depthFrame.depthEntryLabel.place(relx=.0125, rely=.05, anchor="nw")
        
        self.leftFrame.depthFrame.depthEntryButton = ctk.CTkButton(self.leftFrame.depthFrame, text="Add", command=self.addDepth)
        self.leftFrame.depthFrame.depthEntryButton.place(relx=.975, rely=.65, anchor="se")
        self.leftFrame.depthFrame.depthDeleteButton = ctk.CTkButton(self.leftFrame.depthFrame, text="Delete selection", command=self.removeDepth)
        self.leftFrame.depthFrame.depthDeleteButton.place(relx=.975, rely=.95, anchor="se")
        self.leftFrame.depthFrame.depthEntry = ctk.CTkEntry(self.leftFrame.depthFrame)
        self.leftFrame.depthFrame.depthEntry.place(relx=.975, rely=.35, anchor="se")
        ### End of depth selection frame

        ### File input frame
        self.leftFrame.fileFrame = ctk.CTkFrame(self.leftFrame, width=500, height=125)
        self.leftFrame.fileFrame.place(relx=.01, rely=.716, anchor = "w")
        
        self.leftFrame.fileFrame.tempLabel = ctk.CTkLabel(self.leftFrame.fileFrame, text="Temp Data")
        self.leftFrame.fileFrame.tempLabel.place(relx=.005, rely=.15, anchor="w")
        self.leftFrame.fileFrame.tempFileLabel = ctk.CTkLabel(self.leftFrame.fileFrame, text="No file...")
        self.leftFrame.fileFrame.tempFileLabel.place(relx =.5025, rely=.15, anchor="w")
        self.leftFrame.fileFrame.tempFileButton = ctk.CTkButton(self.leftFrame.fileFrame, text="Select file...", command=lambda: self.selectfile(2))
        self.leftFrame.fileFrame.tempFileButton.place(relx=.1525, rely=.15, anchor="w")
        
        self.leftFrame.fileFrame.windLabel = ctk.CTkLabel(self.leftFrame.fileFrame, text = "Wind Data")
        self.leftFrame.fileFrame.windLabel.place(relx=.005, rely=.48, anchor="w")
        self.leftFrame.fileFrame.windFileLabel = ctk.CTkLabel(self.leftFrame.fileFrame, text="No file...")
        self.leftFrame.fileFrame.windFileLabel.place(relx=.5025, rely=.48, anchor="w")
        self.leftFrame.fileFrame.windFileButton = ctk.CTkButton(self.leftFrame.fileFrame, text="Select file...", command=lambda: self.selectfile(1))
        self.leftFrame.fileFrame.windFileButton.place(relx=.1525, rely=.48, anchor="w")
        
        self.leftFrame.fileFrame.solarLabel = ctk.CTkLabel(self.leftFrame.fileFrame, text="Solar Data")
        self.leftFrame.fileFrame.solarLabel.place(relx=.005, rely=.81, anchor="w")
        self.leftFrame.fileFrame.solarFileLabel = ctk.CTkLabel(self.leftFrame.fileFrame, text="No file...")
        self.leftFrame.fileFrame.solarFileLabel.place(relx=.5025, rely=.81, anchor="w")
        self.leftFrame.fileFrame.solarFileButton = ctk.CTkButton(self.leftFrame.fileFrame, text="Select file...", command=lambda: self.selectfile(0))
        self.leftFrame.fileFrame.solarFileButton.place(relx=.1525, rely=.81, anchor="w")
        
        ### End of file input frame
        
        self.rightFrame = ctk.CTkFrame(self, width=635, height=720)
        self.rightFrame.place(relx=.50390625, rely=0, anchor="nw") # frame should start 5 pix from center (640 + 5), 645 / 1280 ~= .50390625
        
        ### Seasonal adjustment frame
        
        
        
        ### End of seasonal adjustment frame
        
        ### Simulation Frame
        self.rightFrame.simFrame = ctk.CTkFrame(self.rightFrame, width=500, height=125)
        self.rightFrame.simFrame.place(relx=.99, rely=.5, anchor="e")
        
        self.rightFrame.simFrame.simRunButton = ctk.CTkButton(self.rightFrame.simFrame, text="Run", command=self.simulation_button)
        self.rightFrame.simFrame.simRunButton.place(relx=.05, rely=.95, anchor="sw")
        
        self.rightFrame.simFrame.simPauseButton = ctk.CTkButton(self.rightFrame.simFrame, text="Pause", command=None) # ADD COMMAND
        self.rightFrame.simFrame.simPauseButton.place(relx=.5, rely=.95, anchor="s")
        
        self.rightFrame.simFrame.simStopButton = ctk.CTkButton(self.rightFrame.simFrame, text="Stop", command=self.stopSim)
        self.rightFrame.simFrame.simStopButton.place(relx=.95, rely=.95, anchor="se")
        
        self.rightFrame.simFrame.pp_box = ctk.CTkCheckBox(self.rightFrame.simFrame, text="Post Processing Plot", variable=self.post_process, onvalue=True, offvalue=False)
        self.rightFrame.simFrame.pp_box.place(relx=.05, rely=.05, anchor="nw")
        
        self.rightFrame.simFrame.uc_box = ctk.CTkCheckBox(self.rightFrame.simFrame, text="Calibration by Ucode", variable=self.Ucode, onvalue=True, offvalue=False)
        self.rightFrame.simFrame.uc_box.place(relx=.05, rely=.3, anchor="nw")
        
        ### End simulation frame
        
        ### Beginning of button definitions
        
        

        ### End of button definitions
        
        ### Beginning of input widget definitions
        #### Check boxes
        
        
        
        # Top-level menu bar
        self.mainMenuBar = ctkmb.CTkMenuBar(self)
        self.mmb_file = self.mainMenuBar.add_cascade("File")
        self.mmb_option = self.mainMenuBar.add_cascade("Options")
        self.mmb_settings = self.mainMenuBar.add_cascade("Settings")
        self.mmb_about = self.mainMenuBar.add_cascade("About")
        self.mmb_exit = self.mainMenuBar.add_cascade("Exit", command=self.exit_function)
        
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
    
    def updateName(self):
        shared.proj_name = str(self.leftFrame.projectFrame.nameEntry.get())
        self.leftFrame.projectFrame.projName.configure(text=shared.proj_name)
    
    def updateTSB(self):
        try:
            self.thicknessSubbase = float(self.constFrame.tsbEntry.get())
            
            self.thicknessSubgrade = self.totalThickness - self.thicknessAC - self.thicknessBase - self.thicknessSubbase
            
            self.constFrame.tsbLabel.configure(text=("Total subbase thickness:   " + str(self.thicknessSubbase) + " m"))
            self.constFrame.tsgLabel.configure(text=("Subgrade thickness:            " + str(self.thicknessSubgrade) + " m"))
        except ValueError:
            self.popup = TopLevelWindow(self)
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(master=self.popup,
                                                     text="Oops! You tried to enter an invalid value for the total thickness. Ensure all values are entered as numeric",
                                                     wraplength=300, justify="center")
            self.popup.warningMessage.place(relx=.5, rely=.5, anchor=ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(master=self.popup, text="Close pop-up window", command=lambda: self.closePopup(self.popup))
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
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

            self.popup.warningMessage = ctk.CTkLabel(master=self.popup,
                                                     text="Oops! You tried to enter an invalid value for the total thickness. Ensure all values are entered as numeric",
                                                     wraplength=300, justify="center")
            self.popup.warningMessage.place(relx=.5, rely=.5, anchor=ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(master=self.popup, text="Close pop-up window", command=lambda: self.closePopup(self.popup))
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
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

            self.popup.warningMessage = ctk.CTkLabel(master=self.popup,
                                                     text="Oops! You tried to enter an invalid value for the total thickness. Ensure all values are entered as numeric",
                                                     wraplength=300, justify="center")
            self.popup.warningMessage.place(relx=.5, rely=.5, anchor=ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(master=self.popup, text="Close pop-up window", command=lambda: self.closePopup(self.popup))
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
            self.popup.update()
        
    
    def removeDepth(self):
        selected_index = self.leftFrame.depthFrame.depthList.curselection()
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
                value = float(self.leftFrame.depthFrame.depthEntry.get())
                self.thermo_depth.append(value)
            except ValueError:
                self.popup = TopLevelWindow(self)
                self.popup.title("Invalid selection!")

                self.popup.warningMessage = ctk.CTkLabel(master=self.popup,
                                                         text="Oops! You tried to enter an invalid value for the depth list. Ensure all depth values are entered as numeric",
                                                         wraplength=300, justify="center")
                self.popup.warningMessage.place(relx=.5, rely=.5, anchor=ctk.CENTER)
                
                self.popup.exitPopup = ctk.CTkButton(master=self.popup, text="Close pop-up window", command=lambda: self.closePopup(self.popup))
                self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
                
                self.popup.update()
            # except value > max depth
            ### ADD EXCEPTION
        self.update_depthlist()
    
    def stopSim(self):
        shared.endEarly.set()
    
    def stopPopupSim(self, popup):
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
            self.simulation_thread = threading.Thread(target=self.run_simulation_in_thread, daemon=True)
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
                       solarFile=solarFile, windFile=windFile, tempFile=tempFile, # File paths for the data
                       Thermo_depth=self.thermo_depth, # Share the current thermo_depth list with the function
                       thickness_AC=self.thicknessAC, thickness_Base=self.thicknessBase, thickness_subbase=self.thicknessSubbase, thickness_subgrade=self.thicknessSubgrade
                       )
        
        shared.running.clear()
        self.closePopup(self.popup)
            
    def blockSelectFile(self):
        self.popup = TopLevelWindow(self)
        self.popup.title("Oh No!")
        
        self.popup.choice = ctk.CTkLabel(self.popup, text="Would you like to end the simulation and choose new data?")
        self.popup.choice.place(relx=.5, rely=.3, anchor=ctk.CENTER)
        
        self.popup.buttonEnd = ctk.CTkButton(master=self.popup, text="End simulation", command=lambda: self.stopPopupSim(self.popup))
        self.popup.buttonEnd.place(relx=.25, rely=.7, anchor=ctk.CENTER)
        
        self.popup.buttonContinue = ctk.CTkButton(master=self.popup, text="Continue simulation", command=lambda: self.closePopup(self.popup))
        self.popup.buttonContinue.place(relx=.75, rely=.7, anchor=ctk.CENTER)
        
        self.popup.update()
    
    def selectfile(self, data):
        if shared.running.is_set():
            self.blockSelectFile()
        else:
            if data == 0:
                self.solarFile = ctk.filedialog.askopenfilename()
                if  self.solarFile[len(self.solarFile) - 5:] == ".xlsx":
                    solarFileParts = self.solarFile.split('/')
                    if len(solarFileParts) > 1:
                        self.solarFileShort = solarFileParts[0] + '\\' + solarFileParts[1] + "\\...\\" + solarFileParts[-1]
                    self.leftFrame.fileFrame.solarFileLabel.configure(text=self.solarFileShort)
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
                    windFileParts = self.windFile.split('/')
                    if len(windFileParts) > 1:
                        self.windFileShort = windFileParts[0] + '\\' + windFileParts[1] + "\\...\\" + windFileParts[-1]
                    self.leftFrame.fileFrame.windFileLabel.configure(text=self.windFileShort)
                else:
                    self.windFile = None
                    self.popup = TopLevelWindow(self)
                    self.popup.title("Bad file input, expected .xlsx")
                    
                    self.popup.warning = ctk.CTkLabel(self.popup, text="The file you provided was not a .xlsx file, please double check file format and resubmit.",
                                                      wraplength=300, justify="center")
                    self.popup.warning.pack()
            elif data == 2:
                self.tempFile = ctk.filedialog.askopenfilename()
                if self.tempFile[len(self.tempFile) - 5:] == ".xlsx":
                    tempFileParts = self.tempFile.split('/')
                    if len(tempFileParts) > 1:
                        self.tempFileShort = tempFileParts[0] + '\\' + tempFileParts[1] + "\\...\\" + tempFileParts[-1]
                    self.leftFrame.fileFrame.tempFileLabel.configure(text=self.tempFileShort)
                else:
                    self.tempFile = None
                    self.popup = TopLevelWindow(self)
                    self.popup.title("Bad file input, expected .xlsx")
                    
                    self.popup.warning = ctk.CTkLabel(self.popup, text="The file you provided was not a .xlsx file, please double check file format and resubmit.",
                                                      wraplength=300, justify="center")
                    self.popup.warning.pack()
            elif data == 3:
                shared.proj_folder_long = tk.filedialog.askdirectory()
                shared.proj_folder_parts = shared.proj_folder_long.split('/')
                if len(shared.proj_folder_parts) > 1:
                    shared.proj_folder = shared.proj_folder_parts[0] + '\\' + shared.proj_folder_parts[1] + "\\...\\" + shared.proj_folder_parts[-1]
                else:
                    shared.proj_folder = shared.proj_folder_long
                    
                self.leftFrame.projectFrame.projFolder.configure(text="Project Folder: " + shared.proj_folder)

    def update_depthlist(self):
        # Clear the listbox
        self.leftFrame.depthFrame.depthList.delete("all")
        # Repopulate with the values in thermo_depth
        for depth in self.thermo_depth:
            self.leftFrame.depthFrame.depthList.insert(ctk.END, depth)
        
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
    root.geometry("1280x720")
    
    app = MainApp(root)
    app.pack(side="top", fill="both", expand=True)
    
    root.protocol("WM_DELETE_WINDOW", app._quit)
    
    main()
