# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 13:59:27 2024

@author: Drew Mortenson
"""

# See page 14 of my lab notebook for style guidelines

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


# %
class TopLevelWindow(ctk.CTkToplevel):
    def __init__(self, geometry="400x300", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry(geometry)
        
        self.attributes('-topmost', 1)


# %
class MainApp(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.pack()
        
        self.winfo_toplevel().title("TEMPY")
        
        # Containers for file names, these will be passed to the
        #   run_simulation function to handle GUI file assignment
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
        self.thicknessSubgrade = self.totalThickness - self.thicknessAC \
                                - self.thicknessBase \
                                - self.thicknessSubbase
        
        # For now, we initialize
        self.thermo_depth = [0]
        
        # run postprocess or not, True or False
        self.post_process = tk.BooleanVar(value=False)
        # this is used to run the sensitivity analysis
        #   for delta_e_1 and delta_e_6
        self.Ucode = tk.BooleanVar(value=False)
        # Identifying the variables as BooleanVar enables connection to GUI,
        #   call with .get() to get standard boolean value for use.
        
        # Middle (dividing column)
        # This must be defined prior to the left/right side frame(s)
        #   to ensure it is on top
        self.middleCol = ctk.CTkFrame(self, width=10, height=1080,
                                      fg_color="black"
        )
        self.middleCol.place(relx=.5, rely=0, anchor="n")

        # Left side frame
        self.leftFrame = ctk.CTkFrame(self, width=955, height=1055)
        self.leftFrame.place(relx=0, rely=.02315, anchor="nw")
        
        # %% Step one: Enter project name
        self.leftFrame.stepOne = ctk.CTkFrame(self.leftFrame, width=945,
                                              height=150
        )
        self.leftFrame.stepOne.pack(padx=5, pady=5, side=ctk.TOP)
        
        self.leftFrame.stepOne.projName = ctk.CTkLabel(
            self.leftFrame.stepOne, text=shared.proj_name, wraplength=500,
            font=("Segoe UI", 20, "bold")
        )
        self.leftFrame.stepOne.projName.place(relx=.005, rely=0, anchor="nw")
        self.leftFrame.stepOne.nameEntry = ctk.CTkEntry(
            self.leftFrame.stepOne, placeholder_text="Enter a project name"
        )
        self.leftFrame.stepOne.nameEntry.place(relx=.005, rely=.45,
                                               anchor="nw"
        )
        self.leftFrame.stepOne.nameSubmit = ctk.CTkButton(
            self.leftFrame.stepOne, text="Update project name",
            command=self.updateName
        )
        self.leftFrame.stepOne.nameSubmit.place(relx=.005, rely=.95,
                                                anchor="sw"
        )

        # %% Step two: Enter project folder
        self.leftFrame.stepTwo = ctk.CTkFrame(self.leftFrame, width=945,
                                              height=150
        )
        self.leftFrame.stepTwo.pack(padx=5, pady=5, side=ctk.TOP)
        
        self.leftFrame.stepTwo.projFolder = ctk.CTkLabel(
            self.leftFrame.stepTwo, text="Project Folder: "
            + shared.proj_folder
        )
        self.leftFrame.stepTwo.projFolder.place(relx=.7, rely=.625,
                                                anchor=ctk.CENTER
        )
        self.leftFrame.stepTwo.folderSubmit = ctk.CTkButton(
            self.leftFrame.stepTwo, text="Choose new project folder",
            command=lambda: self.selectfile(3)
        )
        self.leftFrame.stepTwo.folderSubmit.place(relx=.7, rely=.85,
                                                  anchor=ctk.CENTER
        )

        # %% Step three: Enter asphalt concrete structural data
        self.leftFrame.stepThree = ctk.CTkFrame(self.leftFrame, width=945,
                                                height=150
        )
        self.leftFrame.stepThree.pack(padx=5, pady=5, side=ctk.TOP)
        
        # Thickness AC (asphalt concrete)
        self.leftFrame.stepThree.tacEntry = ctk.CTkEntry(
            self.leftFrame.stepThree
        )
        self.leftFrame.stepThree.tacEntry.place(relx=.005, rely=.05,
                                                anchor="nw"
        )
        self.leftFrame.stepThree.tacEnter = ctk.CTkButton(
            self.leftFrame.stepThree, text="Update", command=self.updateTAC
        )
        self.leftFrame.stepThree.tacEnter.place(relx=.3, rely=.05, anchor="nw")
        self.leftFrame.stepThree.tacLabel = ctk.CTkLabel(
            self.leftFrame.stepThree,
            text=("Total AC thickness:              "
                  + str(self.thicknessAC) + " m")
        )
        self.leftFrame.stepThree.tacLabel.place(relx=.6, rely=.05, anchor="nw")
        
        # Creating tooltip to let the user know that AC = Asphalt Concrete
        self.leftFrame.stepThree.ACtt = CreateToolTip(
            self.leftFrame.stepThree.tacLabel, "AC = Asphalt Concrete"
        )
        
        # Thickness base
        self.leftFrame.stepThree.tbEntry = ctk.CTkEntry(
            self.leftFrame.stepThree
        )
        self.leftFrame.stepThree.tbEntry.place(relx=.005, rely=.5, anchor="w")
        self.leftFrame.stepThree.tbEnter = ctk.CTkButton(
            self.leftFrame.stepThree, text="Update", command=self.updateTB
        )
        self.leftFrame.stepThree.tbEnter.place(relx=.3, rely=.5, anchor="w")
        self.leftFrame.stepThree.tbLabel = ctk.CTkLabel(
            self.leftFrame.stepThree,
            text=("Total base thickness:          "
                  + str(self.thicknessBase) + " m")
        )
        self.leftFrame.stepThree.tbLabel.place(relx=.6, rely=.5, anchor="w")
        
        # Thickness subbase
        self.leftFrame.stepThree.tsbEntry = ctk.CTkEntry(
            self.leftFrame.stepThree
        )
        self.leftFrame.stepThree.tsbEntry.place(relx=.005, rely=.95,
                                                anchor="sw"
        )
        self.leftFrame.stepThree.tsbEnter = ctk.CTkButton(
            self.leftFrame.stepThree, text="Update", command=self.updateTSB
        )
        self.leftFrame.stepThree.tsbEnter.place(relx=.3, rely=.95, anchor="sw")
        self.leftFrame.stepThree.tsbLabel = ctk.CTkLabel(
            self.leftFrame.stepThree,
            text=("Total subbase thickness:   "
                  + str(self.thicknessSubbase) + " m")
        )
        self.leftFrame.stepThree.tsbLabel.place(relx=.6, rely=.95, anchor="sw")

        # %% Step four: Select seasonal adjustment parameters
        self.leftFrame.stepFour = ctk.CTkFrame(self.leftFrame, width=945,
                                               height=150
        )
        self.leftFrame.stepFour.pack(padx=5, pady=5, side=ctk.TOP)
        
        ''' MORE WORK NEEDED, NOT IMPLEMENTED THUS FAR'''

        # %% Step five: Select desired depths for calculations
        self.leftFrame.stepFive = ctk.CTkFrame(self.leftFrame, width=945,
                                               height=150
        )
        self.leftFrame.stepFive.pack(padx=5, pady=5, side=ctk.TOP)
        
        self.leftFrame.stepFive.depthList = CTkListbox(self.leftFrame.stepFive,
                                                       height=50
        )
        self.leftFrame.stepFive.depthList.place(relx=0.0125, rely=.95,
                                                anchor="sw"
        )
        self.leftFrame.stepFive.depthEntryLabel = ctk.CTkLabel(
            self.leftFrame.stepFive,
            text="Enter depths (m) for temperature profile",
            font=("Segoe UI", 16)
        )
        self.leftFrame.stepFive.depthEntryLabel.place(relx=.0125, rely=.05,
                                                      anchor="nw"
        )
        
        self.leftFrame.stepFive.depthEntryButton = ctk.CTkButton(
            self.leftFrame.stepFive, text="Add", command=self.addDepth
        )
        self.leftFrame.stepFive.depthEntryButton.place(relx=.975, rely=.65,
                                                       anchor="se"
        )
        self.leftFrame.stepFive.depthDeleteButton = ctk.CTkButton(
            self.leftFrame.stepFive, text="Delete selection",
            command=self.removeDepth
        )
        self.leftFrame.stepFive.depthDeleteButton.place(relx=.975, rely=.95,
                                                        anchor="se"
        )
        self.leftFrame.stepFive.depthEntry = ctk.CTkEntry(
            self.leftFrame.stepFive
        )
        self.leftFrame.stepFive.depthEntry.place(relx=.975, rely=.35,
                                                 anchor="se"
        )

        # %% Step six: Select files for data input
        self.leftFrame.stepSix = ctk.CTkFrame(self.leftFrame, width=945,
                                              height=150)
        self.leftFrame.stepSix.pack(padx=5, pady=5, side=ctk.TOP)
        
        self.leftFrame.stepSix.tempLabel = ctk.CTkLabel(
            self.leftFrame.stepSix, text="Temp Data"
        )
        self.leftFrame.stepSix.tempLabel.place(relx=.005, rely=.15,
                                               anchor="w"
        )
        self.leftFrame.stepSix.tempFileLabel = ctk.CTkLabel(
            self.leftFrame.stepSix, text="No file..."
        )
        self.leftFrame.stepSix.tempFileLabel.place(relx=.5025, rely=.15,
                                                   anchor="w"
        )
        self.leftFrame.stepSix.tempFileButton = ctk.CTkButton(
            self.leftFrame.stepSix, text="Select file...",
            command=lambda: self.selectfile(2)
        )
        self.leftFrame.stepSix.tempFileButton.place(relx=.1525, rely=.15,
                                                    anchor="w"
        )
        
        self.leftFrame.stepSix.windLabel = ctk.CTkLabel(
            self.leftFrame.stepSix, text="Wind Data"
        )
        self.leftFrame.stepSix.windLabel.place(relx=.005, rely=.48, anchor="w")
        self.leftFrame.stepSix.windFileLabel = ctk.CTkLabel(
            self.leftFrame.stepSix, text="No file..."
        )
        self.leftFrame.stepSix.windFileLabel.place(relx=.5025, rely=.48,
                                                   anchor="w"
        )
        self.leftFrame.stepSix.windFileButton = ctk.CTkButton(
            self.leftFrame.stepSix, text="Select file...",
            command=lambda: self.selectfile(1)
        )
        self.leftFrame.stepSix.windFileButton.place(relx=.1525, rely=.48,
                                                    anchor="w"
        )
        
        self.leftFrame.stepSix.solarLabel = ctk.CTkLabel(
            self.leftFrame.stepSix, text="Solar Data"
        )
        self.leftFrame.stepSix.solarLabel.place(relx=.005, rely=.81,
                                                anchor="w"
        )
        self.leftFrame.stepSix.solarFileLabel = ctk.CTkLabel(
            self.leftFrame.stepSix, text="No file..."
        )
        self.leftFrame.stepSix.solarFileLabel.place(relx=.5025, rely=.81,
                                                    anchor="w"
        )
        self.leftFrame.stepSix.solarFileButton = ctk.CTkButton(
            self.leftFrame.stepSix, text="Select file...",
            command=lambda: self.selectfile(0)
        )
        self.leftFrame.stepSix.solarFileButton.place(relx=.1525, rely=.81,
                                                     anchor="w"
        )
        
        # %% Step Seven: Run simulation
        self.leftFrame.stepSeven = ctk.CTkFrame(
            self.leftFrame, width=945, height=75
        )
        self.leftFrame.stepSeven.pack(padx=5, pady=5, side=ctk.TOP)
        
        self.leftFrame.stepSeven.simRunButton = ctk.CTkButton(
            self.leftFrame.stepSeven, text="Run",
            command=self.simulation_button
        )
        self.leftFrame.stepSeven.simRunButton.place(relx=.05, rely=.5,
                                                    anchor="w"
        )
        self.leftFrame.stepSeven.simPauseButton = ctk.CTkButton(
            self.leftFrame.stepSeven, text="Pause", command=None  # ADD COMMAND
        )
        self.leftFrame.stepSeven.simPauseButton.place(relx=.5, rely=.5,
                                                      anchor=ctk.CENTER
        )
        self.leftFrame.stepSeven.simStopButton = ctk.CTkButton(
            self.leftFrame.stepSeven, text="Stop", command=self.stopSim
        )
        self.leftFrame.stepSeven.simStopButton.place(relx=.95, rely=.5,
                                                     anchor="e"
        )
        '''
        self.leftFrame.stepSeven.pp_box = ctk.CTkCheckBox(
            self.rightFrame.simFrame, text="Post Processing Plot",
            variable=self.post_process, onvalue=True, offvalue=False
        )
        self.leftFrame.stepSeven.pp_box.place(relx=.05, rely=.05, anchor="nw")
        
        self.leftFrame.stepSeven.uc_box = ctk.CTkCheckBox(
            self.rightFrame.simFrame, text="Calibration by Ucode",
            variable=self.Ucode, onvalue=True, offvalue=False
        )
        self.leftFrame.stepSeven.uc_box.place(relx=.05, rely=.3, anchor="nw")
        '''
        self.rightFrame = ctk.CTkFrame(self, width=955, height=1080)
        self.rightFrame.place(relx=.5026, rely=.02315)
        
        self.rightFrame.rightFrameTop = ctk.CTkFrame(self.rightFrame,
                                                     width=955,
                                                     height=525
        )
        self.rightFrame.rightFrameTop.pack(side=ctk.TOP)
        
        self.rightFrame.rightDivider = ctk.CTkFrame(self.rightFrame,
                                                    width=960,
                                                    height=10,
                                                    fg_color="black"
        )
        self.rightFrame.rightDivider.pack(side=ctk.TOP)
        
        self.rightFrame.rightFrameBtm = ctk.CTkFrame(self.rightFrame,
                                                     width=955,
                                                     height=525
        )
        self.rightFrame.rightFrameBtm.pack(side=ctk.TOP)

        # %% Top-level menu bar
        self.mainMenuBar = ctkmb.CTkMenuBar(self)
        self.mmb_file = self.mainMenuBar.add_cascade("File")
        self.mmb_option = self.mainMenuBar.add_cascade("Options")
        self.mmb_settings = self.mainMenuBar.add_cascade("Settings")
        self.mmb_about = self.mainMenuBar.add_cascade("About")
        self.mmb_exit = self.mainMenuBar.add_cascade("Exit",
                                                     command=self.exit_function
        )
        
        # Defining "File" drop down menu
        self.dd_file = ctkmb.CustomDropdownMenu(widget=self.mmb_file)
        self.dd_file.add_option(option="Open", command=lambda: print("Open"))
        self.dd_file.add_option(option="Save", command=lambda: print("Save"))
        
        # This adds a small line between the options listed above and
        #   the next option (or commonly used above a submenu)
        self.dd_file.add_separator()
        
        # Adding sub menu to file menu
        self.dd_file_submenu = self.dd_file.add_submenu("Export As")
        self.dd_file_submenu.add_option(option=".TXT",
                                        command=lambda: print("TXT")
        )
        self.dd_file_submenu.add_option(option=".PDF",
                                        command=lambda: print("PDF")
        )
        
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
    
    # %% Functions
    def updateName(self):
        shared.proj_name = str(self.leftFrame.stepOne.nameEntry.get())
        self.leftFrame.stepOne.projName.configure(text=shared.proj_name)
    
    def updateTSB(self):
        try:
            self.thicknessSubbase = float(
                self.leftFrame.stepThree.tsbEntry.get()
            )
            
            self.thicknessSubgrade = self.totalThickness - self.thicknessAC \
                                    - self.thicknessBase \
                                    - self.thicknessSubbase
            
            self.leftFrame.stepThree.tsbLabel.configure(
                text=("Total subbase thickness:   "
                      + str(self.thicknessSubbase) + " m"))
        except ValueError:
            self.popup = TopLevelWindow(self)
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(master=self.popup,
                text="Oops! You tried to enter an invalid value for the total "
                        "thickness. Ensure all values are entered as numeric",
                wraplength=300, justify="center"
            )
            self.popup.warningMessage.place(relx=.5, rely=.5,
                                            anchor=ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(self.popup,
                text="Close pop-up window",
                command=lambda: self.closePopup(self.popup)
            )
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
            self.popup.update()
        except self.thicknessAC + self.thicknessBase + self.thicknessSubbase \
                > self.totalThickness:
            self.popup = TopLevelWindow(geometry="300x150")
            self.popup.title("Invalid subbase thickness!")
            
            self.popup.warningMessage = ctk.CTkLabel(self.popup,
                text="Entered subbase value causes negative subgrade value, "
                        "enter new subbase value, "
                        "or update base/subbase thickness",
                wraplength=300,
                justify="center"
            )
            self.popup.warningMessage.place(relx=.5, rely=.5,
                                            anchor=ctk.CENTER)
    
    def updateTB(self):
        try:
            self.thicknessBase = float(self.leftFrame.stepThree.tbEntry.get())
            
            self.thicknessSubgrade = self.totalThickness - self.thicknessAC \
                                    - self.thicknessBase \
                                    - self.thicknessSubbase
            
            self.leftFrame.stepThree.tbLabel.configure(
                text=("Total base thickness:          "
                      + str(self.thicknessBase) + " m"))
        except ValueError:
            self.popup = TopLevelWindow(self)
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(self.popup,
                text="Oops! You tried to enter an invalid value for the total "
                        "thickness. Ensure all values are entered as numeric",
                wraplength=300, justify="center"
            )
            self.popup.warningMessage.place(relx=.5, rely=.5,
                                            anchor=ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(self.popup,
                text="Close pop-up window",
                command=lambda: self.closePopup(self.popup)
            )
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
            self.popup.update()
        except self.thicknessAC + self.thicknessBase + self.thicknessSubbase \
                > self.totalThickness:
            self.popup = TopLevelWindow(geometry="300x150")
            self.popup.title("Invalid base thickness!")
            
            self.popup.warningMessage = ctk.CTkLabel(self.popup,
                text="Entered base value causes negative subgrade value, enter"
                        " new base value, or update base/subbase thickness",
                wraplength=300,
                justify="center"
            )
            self.popup.warningMessage.place(relx=.5, rely=.5,
                                            anchor=ctk.CENTER)
    
    def updateTAC(self):
        try:
            self.thicknessAC = float(self.leftFrame.stepThree.tacEntry.get())
            
            self.thicknessSubgrade = self.totalThickness - self.thicknessAC \
                                    - self.thicknessBase \
                                    - self.thicknessSubbase
            
            self.leftFrame.stepThree.tacLabel.configure(
                text=("Total AC thickness:               "
                     + str(self.thicknessAC) + " m"))
        except ValueError:
            self.popup = TopLevelWindow(self)
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(self.popup,
                text="Oops! You tried to enter an invalid value for the total "
                        "thickness. Ensure all values are entered as numeric",
                wraplength=300, justify="center"
            )
            self.popup.warningMessage.place(relx=.5, rely=.5,
                                            anchor=ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(master=self.popup,
                text="Close pop-up window",
                command=lambda: self.closePopup(self.popup)
            )
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
            self.popup.update()
        except self.thicknessAC + self.thicknessBase + self.thicknessSubbase \
                > self.totalThickness:
            self.popup = TopLevelWindow(geometry="300x150")
            self.popup.title("Invalid asphalt concrete thickness!")
            
            self.popup.warningMessage = ctk.CTkLabel(self.popup,
                text="Entered asphalt value causes negative subgrade value, "
                        "enter new AC value, or update base/subbase thickness",
                wraplength=300,
                justify="center"
            )
            self.popup.warningMessage.place(relx=.5, rely=.5,
                                            anchor=ctk.CENTER)
    
    def removeDepth(self):
        selected_index = self.leftFrame.stepFive.depthList.curselection()
        if selected_index is not None:
            index = int(selected_index)
            # Prevent user from deleting 0
            if self.thermo_depth[index] != 0:
                self.thermo_depth.pop(index)
            else:
                self.popup = TopLevelWindow(self)
                self.popup.title("Invalid deletion!")
                
                self.popup.warningMessage = ctk.CTkLabel(self.popup,
                    text="Unable to delete 0 (temperature at surface)",
                    wraplength=300, justify="center")
                self.popup.warningMessage.place(relx=.5, rely=.5,
                                                anchor=ctk.CENTER)
            self.update_depthlist()
        else:
            self.popup = TopLevelWindow(geometry="300x100")
            self.popup.title("Nothins selected!")
            
            self.popup.warningMessage(self.popup,
                                      text="No depth selected for deletion",
                                      wraplength=300, justify="center"
            )
            self.popup.warningMessage.place(relx=.5, rely=.5,
                                            anchor=ctk.CENTER
            )
    
    def addDepth(self):
        if len(self.thermo_depth) > 10:
            self.popup = TopLevelWindow(self)
            self.popup.title("Too many depths!")
        else:
            try:
                # Read the value in and append it to the list
                value = float(self.leftFrame.stepFive.depthEntry.get())
                self.thermo_depth.append(value)
                # Remove duplicates
                self.thermo_depth = list(set(self.thermo_depth))
                # Ensure the list stays in ascending order for readability
                self.thermo_depth.sort()
                self.leftFrame.stepFive.depthEntry.delete(0, 'end')
            except ValueError:
                self.popup = TopLevelWindow(self)
                self.popup.title("Invalid selection!")

                self.popup.warningMessage = ctk.CTkLabel(self.popup,
                    text="Oops! You tried to enter an invalid value for the "
                            "depth list. Ensure all depth values are entered "
                            "as numeric",
                    wraplength=300, justify="center"
                )
                self.popup.warningMessage.place(relx=.5, rely=.5,
                                                anchor=ctk.CENTER
                )
                
                self.popup.exitPp = ctk.CTkButton(master=self.popup,
                    text="Close pop-up window",
                    command=lambda: self.closePopup(self.popup)
                )
                self.popup.exitPp.place(relx=.5, rely=.7, anchor=ctk.CENTER)
                
                self.popup.update()
            except value > self.totalThickness:
                self.popup = TopLevelWindow(geometry="300x100")
                self.popup.title("Invalid depth!")
                
                self.popup.warningMessage = ctk.CTkLabel(self.popup,
                    text="Depth entered is larger than total depth, "
                            "select new value",
                    wraplength=300, justify="center"
                )
                self.popup.update()
        self.update_depthlist()
    
    def stopSim(self):
        shared.endEarly.set()
        shared.running.clear()
    
    def stopPopupSim(self, popup):
        shared.endEarly.set()
        shared.running.clear()
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
            and self.tempFile is not None \
                and shared.proj_folder_long != "":
            shared.running.set()
            self.simulation_thread = threading.Thread(
                target=self.run_simulation_in_thread, daemon=True)
            self.post_processing = self.post_process.get()
            self.Ucoding = self.Ucode.get()
            self.simulation_thread.start()
        elif shared.running.is_set():
            # The simulation is already running, notify the user to be patient
            self.popup = TopLevelWindow(self)
            self.popup.title("Please wait!")
            
            self.popup.pleaseWait = ctk.CTkLabel(self.popup,
                text="Please wait while the simulation is running (popup will "
                        "close). Running the simulation more than once at a "
                        "time is not advised due to hardware requirements",
                wraplength=300,
                justify="center"
            )
            self.popup.pleaseWait.pack()
        elif shared.proj_folder_long == "":
            self.popup = TopLevelWindow(geometry="300x100")
            self.popup.title("No project folder!")
            
            self.popup.noProjFolder = ctk.CTkLabel(self.popup,
                        text="The simulation has no project folder to save the"
                                " results to, please repeat step 2",
                        wraplength=300,
                        justify="center"
            )
            self.popup.noProjFolder.place(relx=.5, rely=.5, anchor=ctk.CENTER)
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
            
            self.popup.pleaseWait = ctk.CTkLabel(self.popup,
                text=("You forgot to add the following data sets: " + needed),
                wraplength=300,
                justify="center"
            )
            self.popup.pleaseWait.pack()
            
    def run_simulation_in_thread(self):
        self.popup = TopLevelWindow(self)
        self.popup.title("Simulation running, please wait")
        
        self.popup.pleaseWait = ctk.CTkLabel(self.popup,
            text="Please wait while the simulation is running "
                    "(popup will close)"
        )
        self.popup.pleaseWait.pack()
        
        # Ensure the list has 0, remove duplicates, sort in ascending order
        self.thermo_depth.append(0)
        self.thermo_depth = list(set(self.thermo_depth))
        self.thermo_depth.sort()
        
        solarFile = self.solarFile
        windFile = self.windFile
        tempFile = self.tempFile
        run_simulation(self.post_processing, self.Ucoding,
                       # Check boxes, if these are true than we run post
                       #    processing and Ucode calibration respectively
                       solarFile=solarFile,
                       windFile=windFile,
                       tempFile=tempFile,
                       Thermo_depth=self.thermo_depth,
                       thickness_AC=self.thicknessAC,
                       thickness_Base=self.thicknessBase,
                       thickness_subbase=self.thicknessSubbase,
                       thickness_subgrade=self.thicknessSubgrade
                       )
        
        shared.running.clear()
        shared.endEarly.clear()
        self.closePopup(self.popup)
            
    def blockSelectFile(self):
        self.popup = TopLevelWindow(self)
        self.popup.title("Oh No!")

        self.popup.choice = ctk.CTkLabel(self.popup,
            text="Would you like to end the simulation and choose new data?")
        self.popup.choice.place(relx=.5, rely=.3, anchor=ctk.CENTER)
        
        self.popup.buttonEnd = ctk.CTkButton(self.popup,
            text="End simulation",
            command=lambda: self.stopPopupSim(self.popup)
        )
        self.popup.buttonEnd.place(relx=.25, rely=.7, anchor=ctk.CENTER)
        
        self.popup.buttonContinue = ctk.CTkButton(self.popup,
            text="Continue simulation",
            command=lambda: self.closePopup(self.popup)
        )
        self.popup.buttonContinue.place(relx=.75, rely=.7, anchor=ctk.CENTER)
        
        self.popup.update()
    
    def selectfile(self, data):
        if shared.running.is_set():
            self.blockSelectFile()
        else:
            if data == 0:
                self.solarFile = ctk.filedialog.askopenfilename()
                if self.solarFile[len(self.solarFile) - 5:] == ".xlsx":
                    solarFileParts = self.solarFile.split('/')
                    if len(solarFileParts) > 1:
                        self.solarFileShort = solarFileParts[0] + '\\' \
                            + solarFileParts[1] + "\\...\\" \
                            + solarFileParts[-1]
                    self.leftFrame.stepSix.solarFileLabel.configure(
                        text=self.solarFileShort
                    )
                else:
                    self.solarFile = None
                    self.popup = TopLevelWindow(self)
                    self.popup.title("Bad file input, expected .xlsx")
                    
                    self.popup.warning = ctk.CTkLabel(self.popup,
                        text="The file you provided was not a .xlsx file, "
                                "please double check file format and resubmit",
                        wraplength=300,
                        justify="center"
                    )
                    self.popup.warning.pack()
                    
            elif data == 1:
                self.windFile = ctk.filedialog.askopenfilename()
                if self.windFile[len(self.windFile) - 5:] == ".xlsx":
                    windFileParts = self.windFile.split('/')
                    if len(windFileParts) > 1:
                        self.windFileShort = windFileParts[0] + '\\' \
                            + windFileParts[1] + "\\...\\" \
                            + windFileParts[-1]
                    self.leftFrame.stepSix.windFileLabel.configure(
                        text=self.windFileShort
                    )
                else:
                    self.windFile = None
                    self.popup = TopLevelWindow(self)
                    self.popup.title("Bad file input, expected .xlsx")
                    
                    self.popup.warning = ctk.CTkLabel(self.popup,
                        text="The file you provided was not a .xlsx file, "
                        "please double check file format and resubmit.",
                        wraplength=300,
                        justify="center"
                    )
                    self.popup.warning.pack()
            elif data == 2:
                self.tempFile = ctk.filedialog.askopenfilename()
                if self.tempFile[len(self.tempFile) - 5:] == ".xlsx":
                    tempFileParts = self.tempFile.split('/')
                    if len(tempFileParts) > 1:
                        self.tempFileShort = tempFileParts[0] + '\\' \
                            + tempFileParts[1] + "\\...\\" \
                            + tempFileParts[-1]
                    self.leftFrame.stepSix.tempFileLabel.configure(
                        text=self.tempFileShort
                    )
                else:
                    self.tempFile = None
                    self.popup = TopLevelWindow(self)
                    self.popup.title("Bad file input, expected .xlsx")
                    
                    self.popup.warning = ctk.CTkLabel(self.popup,
                        text="The file you provided was not a .xlsx file, "
                                "please double check file format and retry.",
                        wraplength=300,
                        justify="center"
                    )
                    self.popup.warning.pack()
            elif data == 3:
                shared.proj_folder_long = tk.filedialog.askdirectory()
                shared.proj_folder_parts = shared.proj_folder_long.split('/')
                if len(shared.proj_folder_parts) > 1:
                    shared.proj_folder = shared.proj_folder_parts[0] + '\\' \
                        + shared.proj_folder_parts[1] + "\\...\\" \
                        + shared.proj_folder_parts[-1]
                else:
                    shared.proj_folder = shared.proj_folder_long
                    
                self.leftFrame.stepTwo.projFolder.configure(
                    text="Project Folder: " + shared.proj_folder
                )

    def update_depthlist(self):
        # Clear the listbox
        self.leftFrame.stepFive.depthList.delete("all")
        # Repopulate with the values in thermo_depth
        for depth in self.thermo_depth:
            self.leftFrame.stepFive.depthList.insert(ctk.END, depth)
        
    def _quit(self):
        shared.endEarly.set()
        root.quit()
        root.destroy()


# %% Main
def main():
    # Populate the values in our depth list
    app.update_depthlist()

    root.mainloop()


# %% Main init
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1920x1080")
    
    app = MainApp(root)
    app.pack(side="top", fill="both", expand=True)
    
    root.protocol("WM_DELETE_WINDOW", app._quit)
    
    main()
