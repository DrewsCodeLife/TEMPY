# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 13:59:27 2024

@author: Drew Mortenson
"""

# See page 14 of my lab notebook for style guidelines

import sys
import threading
import shared
import ctypes
import tkinter as tk
import customtkinter as ctk
import CTkMenuBar as ctkmb
import statistics_calc as stclc
import environmental_adjustment_fetcher as eaf
from ctypes import wintypes
from CTkListbox import CTkListbox
from TEMPY import run_simulation
from tooltipGen import CreateToolTip


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# % Window setup
class RECT(ctypes.Structure):
    _fields_ = [
        ('left',   wintypes.LONG),
        ('top',    wintypes.LONG),
        ('right',  wintypes.LONG),
        ('bottom', wintypes.LONG)
    ]


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
        
        # Multipliers for object sizes, tuned to equal 1 at 1920x1080
        #   (eg. set to 2/3 for 1280x720)
        self.multX = 1
        self.multY = 1
        
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
        self.thermo_depth = []
        self.deltaE1 = -0.15
        self.deltaE6 = -0.12
        
        # run postprocess or not, True or False
        self.post_process = tk.BooleanVar(value=False)
        # this is used to run the sensitivity analysis
        #   for delta_e_1 and delta_e_6
        self.Ucode = tk.BooleanVar(value=False)
        
        # run statistic calculations true/false
        self.statsBool = tk.BooleanVar(value=False)
        
        self.statFrames = []
        
        # Middle (dividing column)
        # This must be defined prior to the left/right side frame(s)
        #   to ensure it is on top
        self.middleCol = ctk.CTkFrame(self, width=10 * self.multX,
                                      height=1080 * self.multY,
                                      fg_color="black"
        )
        self.middleCol.place(relx=.5, rely=0, anchor="n")

        # Left side frame
        self.leftFrame = ctk.CTkFrame(self, width=955 * self.multX,
                                      height=1055 * self.multY
        )
        self.leftFrame.place(relx=0, rely=.02315, anchor="nw")
        
        # %% Step one: Enter project name
        self.leftFrame.stepOne = ctk.CTkFrame(self.leftFrame,
                                              width=945 * self.multX,
                                              height=150 * self.multY
        )
        self.leftFrame.stepOne.pack(padx=5, pady=5, side=ctk.TOP)
        
        self.leftFrame.stepOne.stepName = ctk.CTkLabel(
            self.leftFrame.stepOne,
            text="Step 1: Enter project name",
            font=("Segoe UI", 16, "bold")
        )
        self.leftFrame.stepOne.stepName.place(relx=.005, rely=.05, anchor="nw")
        self.leftFrame.stepOne.projName = ctk.CTkLabel(
            self.leftFrame.stepOne, text=shared.proj_name, wraplength=500,
            font=("Segoe UI", 20, "bold")
        )
        self.leftFrame.stepOne.projName.place(relx=.665, rely=.45, anchor="nw")
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
        self.leftFrame.stepOne.nameSubmit.place(relx=.335, rely=.45,
                                                anchor="nw"
        )

        # %% Step two: Enter project folder
        self.leftFrame.stepTwo = ctk.CTkFrame(self.leftFrame,
                                              width=945 * self.multX,
                                              height=150 * self.multY
        )
        self.leftFrame.stepTwo.pack(padx=5, pady=5, side=ctk.TOP)
        
        self.leftFrame.stepTwo.stepName = ctk.CTkLabel(
            self.leftFrame.stepTwo,
            text="Step 2: Choose project folder",
            font=("Segoe UI", 16, "bold")
        )
        self.leftFrame.stepTwo.stepName.place(relx=.005,
                                              rely=.005,
                                              anchor="nw"
        )
        self.leftFrame.stepTwo.projFolder = ctk.CTkLabel(
            self.leftFrame.stepTwo, text="Project Folder: "
            + shared.proj_folder
        )
        self.leftFrame.stepTwo.projFolder.place(relx=.005, rely=.45,
                                                anchor="nw"
        )
        self.leftFrame.stepTwo.folderSubmit = ctk.CTkButton(
            self.leftFrame.stepTwo, text="Choose new project folder",
            command=lambda: self.selectfile(3)
        )
        self.leftFrame.stepTwo.folderSubmit.place(relx=.005, rely=.95,
                                                  anchor="sw"
        )

        # %% Step three: Enter asphalt pavement structural data
        self.leftFrame.stepThree = ctk.CTkFrame(self.leftFrame,
                                                width=945 * self.multX,
                                                height=150 * self.multY
        )
        self.leftFrame.stepThree.pack(padx=5, pady=5, side=ctk.TOP)
        
        self.leftFrame.stepThree.stepName = ctk.CTkLabel(
            self.leftFrame.stepThree,
            text="Step 3: Input\nasphalt\npavement \nstructural data",
            justify="left",
            font=("Segoe UI", 16, "bold")
        )
        self.leftFrame.stepThree.stepName.place(relx=.01,
                                                rely=.5,
                                                anchor="w"
        )
        
        # Thickness AC (asphalt concrete)
        self.leftFrame.stepThree.tacEntry = ctk.CTkEntry(
            self.leftFrame.stepThree
        )
        self.leftFrame.stepThree.tacEntry.place(relx=.2, rely=.05,
                                                anchor="nw"
        )
        self.leftFrame.stepThree.tacEnter = ctk.CTkButton(
            self.leftFrame.stepThree, text="Update", command=self.updateTAC
        )
        self.leftFrame.stepThree.tacEnter.place(relx=.44,
                                                rely=.05,
                                                anchor="nw"
        )
        self.leftFrame.stepThree.tacLabel = ctk.CTkLabel(
            self.leftFrame.stepThree,
            text=("Total AC thickness:              "
                  + str(self.thicknessAC) + " m")
        )
        self.leftFrame.stepThree.tacLabel.place(relx=.68,
                                                rely=.05,
                                                anchor="nw"
        )
        
        # Creating tooltip to let the user know that AC = Asphalt Concrete
        self.leftFrame.stepThree.ACtt = CreateToolTip(
            self.leftFrame.stepThree.tacLabel, "AC = Asphalt Concrete"
        )
        
        # Thickness base
        self.leftFrame.stepThree.tbEntry = ctk.CTkEntry(
            self.leftFrame.stepThree
        )
        self.leftFrame.stepThree.tbEntry.place(relx=.2, rely=.5, anchor="w")
        self.leftFrame.stepThree.tbEnter = ctk.CTkButton(
            self.leftFrame.stepThree, text="Update", command=self.updateTB
        )
        self.leftFrame.stepThree.tbEnter.place(relx=.44, rely=.5, anchor="w")
        self.leftFrame.stepThree.tbLabel = ctk.CTkLabel(
            self.leftFrame.stepThree,
            text=("Total base thickness:          "
                  + str(self.thicknessBase) + " m")
        )
        self.leftFrame.stepThree.tbLabel.place(relx=.68, rely=.5, anchor="w")
        
        # Thickness subbase
        self.leftFrame.stepThree.tsbEntry = ctk.CTkEntry(
            self.leftFrame.stepThree
        )
        self.leftFrame.stepThree.tsbEntry.place(relx=.2, rely=.95,
                                                anchor="sw"
        )
        self.leftFrame.stepThree.tsbEnter = ctk.CTkButton(
            self.leftFrame.stepThree, text="Update", command=self.updateTSB
        )
        self.leftFrame.stepThree.tsbEnter.place(relx=.44,
                                                rely=.95,
                                                anchor="sw"
        )
        self.leftFrame.stepThree.tsbLabel = ctk.CTkLabel(
            self.leftFrame.stepThree,
            text=("Total subbase thickness:   "
                  + str(self.thicknessSubbase) + " m")
        )
        self.leftFrame.stepThree.tsbLabel.place(relx=.68,
                                                rely=.95,
                                                anchor="sw"
        )

        # %% Step four: Select seasonal adjustment parameters
        self.leftFrame.stepFour = ctk.CTkFrame(self.leftFrame,
                                               width=945 * self.multX,
                                               height=150 * self.multY
        )
        self.leftFrame.stepFour.pack(padx=5, pady=5, side=ctk.TOP)
        
        # Left frame
        self.leftFrame.stepFour.left = ctk.CTkFrame(self.leftFrame.stepFour,
                                                    width=311 * self.multX,
                                                    height=150 * self.multY
        )
        self.leftFrame.stepFour.left.pack(padx=2.5, pady=2.5, side=ctk.LEFT)
        
        self.leftFrame.stepFour.left.stepName = ctk.CTkLabel(
            self.leftFrame.stepFour.left,
            text="Step 4: Climate Modifier",
            font=("Segoe UI", 16, "bold")
        )
        self.leftFrame.stepFour.left.stepName.place(relx=.5,
                                                    rely=.005,
                                                    anchor="n"
        )
        
        self.leftFrame.stepFour.left.recBox = ctk.CTkComboBox(
            self.leftFrame.stepFour.left,
            values=eaf.state,
            width=200,
            command=self.recommendedE1E6
        )
        self.leftFrame.stepFour.left.recBox.place(relx=.5,
                                                  rely=.3,
                                                  anchor="n"
        )
        
        self.leftFrame.stepFour.left.recLabel = ctk.CTkLabel(
            self.leftFrame.stepFour.left,
            text="Choose recommended values by state",
            wraplength=150,
            font=("Segoe UI", 14)
        )
        self.leftFrame.stepFour.left.recLabel.place(relx=.5,
                                               rely=.6,
                                               anchor="n"
        )
        
        # Middle frame needs to be defined in between left and right so
        #   placement is correct.
        self.leftFrame.stepFour.mid = ctk.CTkFrame(self.leftFrame.stepFour,
                                                    width=311 * self.multX,
                                                    height=150 * self.multY
        )
        self.leftFrame.stepFour.mid.pack(padx=2.5, pady=2.5, side=ctk.LEFT)
        
        # Right column
        self.leftFrame.stepFour.right = ctk.CTkFrame(self.leftFrame.stepFour,
                                                     width=311 * self.multX,
                                                     height=150 * self.multY
        
        )
        self.leftFrame.stepFour.right.pack(padx=2.5, pady=2.5, side=ctk.LEFT)
        
        self.leftFrame.stepFour.right.e1Label = ctk.CTkLabel(
            self.leftFrame.stepFour.right,
            text="Delta e1: " + str(self.deltaE1),
            font=("Segoe UI", 16, "bold")
        )
        self.leftFrame.stepFour.right.e1Label.place(relx=.05,
                                                    rely=.33,
                                                    anchor="w"
        )
        self.leftFrame.stepFour.right.e6Label = ctk.CTkLabel(
            self.leftFrame.stepFour.right,
            text="Delta e6: " + str(self.deltaE6),
            font=("Segoe UI", 16, "bold")
        )
        self.leftFrame.stepFour.right.e6Label.place(relx=.05,
                                                    rely=.66,
                                                    anchor="w"
        )
        
        # Middle column widgets must be defined last since
        #   they refer to other frames
        
        self.leftFrame.stepFour.mid.e1Entry = ctk.CTkEntry(
            self.leftFrame.stepFour.mid,
            placeholder_text="eg. -.15",
            width=120
        )
        self.leftFrame.stepFour.mid.e1Entry.place(relx=.025,
                                                  rely=.05,
                                                  anchor="nw"
        )
        self.leftFrame.stepFour.mid.e6Entry = ctk.CTkEntry(
            self.leftFrame.stepFour.mid,
            placeholder_text="eg. -.12",
            width=120
        )
        self.leftFrame.stepFour.mid.e6Entry.place(relx=.025,
                                                  rely=.35,
                                                  anchor="nw"
        )
        
        self.leftFrame.stepFour.mid.e1Submit = ctk.CTkButton(
            self.leftFrame.stepFour.mid,
            text="Submit e1",
            command=self.updateE1,
            width=25
        )
        self.leftFrame.stepFour.mid.e1Submit.place(relx=.975,
                                                   rely=.05,
                                                   anchor="ne"
        )
        self.leftFrame.stepFour.mid.e6Submit = ctk.CTkButton(
            self.leftFrame.stepFour.mid,
            text="Submit e6",
            command=self.updateE6,
            width=25
        )
        self.leftFrame.stepFour.mid.e6Submit.place(relx=.975,
                                                   rely=.35,
                                                   anchor="ne"
        )
        
        self.leftFrame.stepFour.mid.manEntryLabel = ctk.CTkLabel(
            self.leftFrame.stepFour.mid,
            text="Enter values manually",
            font=("Segoe UI", 14)
        )
        self.leftFrame.stepFour.mid.manEntryLabel.place(relx=.5,
                                                        rely=.65,
                                                        anchor="n"
        )
        
        # Label for the "OR" in between left and middle
        self.leftFrame.stepFour.orLabel = ctk.CTkLabel(
            self.leftFrame.stepFour,
            text="OR",
            font=("Segoe UI", 20, "bold")
        )
        self.leftFrame.stepFour.orLabel.place(relx=.33, rely=.65, anchor="n")

        # %% Step five: Select desired depths for calculations
        self.leftFrame.stepFive = ctk.CTkFrame(self.leftFrame,
                                               width=945 * self.multX,
                                               height=150 * self.multY
        )
        self.leftFrame.stepFive.pack(padx=5, pady=5, side=ctk.TOP)
        
        self.leftFrame.stepFive.depthList = CTkListbox(self.leftFrame.stepFive,
                                                       height=80
        )
        self.leftFrame.stepFive.depthList.place(relx=0.0125, rely=.95,
                                                anchor="sw"
        )
        self.leftFrame.stepFive.depthEntryLabel = ctk.CTkLabel(
            self.leftFrame.stepFive,
            text="Step 5: Enter depths (m) \nfor temperature profile",
            font=("Segoe UI", 16, "bold")
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
        self.leftFrame.stepSix = ctk.CTkFrame(self.leftFrame,
                                              width=945 * self.multX,
                                              height=150 * self.multY
        )
        self.leftFrame.stepSix.pack(padx=5, pady=5, side=ctk.TOP)
        
        self.leftFrame.stepSix.stepName = ctk.CTkLabel(
            self.leftFrame.stepSix,
            text="Step 6: Input data files",
            font=("Segoe UI", 16, "bold")
        )
        self.leftFrame.stepSix.stepName.place(relx=.005,
                                              rely=.005,
                                              anchor="nw"
        )
        
        self.leftFrame.stepSix.tempFileLabel = ctk.CTkLabel(
            self.leftFrame.stepSix, text="No file..."
        )
        self.leftFrame.stepSix.tempFileLabel.place(relx=.5025, rely=.15,
                                                   anchor="w"
        )
        self.leftFrame.stepSix.tempFileButton = ctk.CTkButton(
            self.leftFrame.stepSix, text="Select temp data file...",
            command=lambda: self.selectfile(2)
        )
        self.leftFrame.stepSix.tempFileButton.place(relx=.1525, rely=.15,
                                                    anchor="w"
        )
        
        self.leftFrame.stepSix.windFileLabel = ctk.CTkLabel(
            self.leftFrame.stepSix, text="No file..."
        )
        self.leftFrame.stepSix.windFileLabel.place(relx=.5025, rely=.48,
                                                   anchor="w"
        )
        self.leftFrame.stepSix.windFileButton = ctk.CTkButton(
            self.leftFrame.stepSix, text="Select wind data file...",
            command=lambda: self.selectfile(1)
        )
        self.leftFrame.stepSix.windFileButton.place(relx=.1525, rely=.48,
                                                    anchor="w"
        )

        self.leftFrame.stepSix.solarFileLabel = ctk.CTkLabel(
            self.leftFrame.stepSix, text="No file..."
        )
        self.leftFrame.stepSix.solarFileLabel.place(relx=.5025, rely=.81,
                                                    anchor="w"
        )
        self.leftFrame.stepSix.solarFileButton = ctk.CTkButton(
            self.leftFrame.stepSix, text="Select solar data file...",
            command=lambda: self.selectfile(0)
        )
        self.leftFrame.stepSix.solarFileButton.place(relx=.1525, rely=.81,
                                                     anchor="w"
        )
        
        # %% Step Seven: Run simulation
        self.leftFrame.stepSeven = ctk.CTkFrame(self.leftFrame,
                                                width=945 * self.multX,
                                                height=75 * self.multY
        )
        self.leftFrame.stepSeven.pack(padx=5, pady=5, side=ctk.TOP)
        
        self.leftFrame.stepSeven.simRunButton = ctk.CTkButton(
            self.leftFrame.stepSeven, text="Run",
            command=self.simulation_button
        )
        self.leftFrame.stepSeven.simRunButton.pack(padx=5,
                                                   pady=5,
                                                   side=ctk.LEFT
        )
        self.leftFrame.stepSeven.simPauseButton = ctk.CTkButton(
            self.leftFrame.stepSeven, text="Pause", command=None  # ADD COMMAND
        )
        self.leftFrame.stepSeven.simPauseButton.pack(padx=5,
                                                     pady=5,
                                                     side=ctk.LEFT
        )
        self.leftFrame.stepSeven.simStopButton = ctk.CTkButton(
            self.leftFrame.stepSeven, text="Stop", command=self.stopSim
        )
        self.leftFrame.stepSeven.simStopButton.pack(padx=5,
                                                    pady=5,
                                                    side=ctk.LEFT
        )
        
        self.leftFrame.stepSeven.statsBox = ctk.CTkCheckBox(
            self.leftFrame.stepSeven, text="Run statistics",
            variable=self.statsBool, onvalue=True, offvalue=False
        )
        self.leftFrame.stepSeven.statsBox.pack(padx=5,
                                               pady=5,
                                               side=ctk.LEFT)
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
        # %% Right Frame
        self.rightFrame = ctk.CTkFrame(self,
                                       width=955 * self.multX,
                                       height=1080 * self.multY
        )
        self.rightFrame.place(relx=.5026, rely=.02315)
        
        self.rightFrame.rightFrameTop = ctk.CTkFrame(self.rightFrame,
                                                     width=955 * self.multX,
                                                     height=525 * self.multY
        )
        self.rightFrame.rightFrameTop.pack(side=ctk.TOP)
        
        self.rightFrame.rightDivider = ctk.CTkFrame(self.rightFrame,
                                                    width=960 * self.multX,
                                                    height=10 * self.multY,
                                                    fg_color="black"
        )
        self.rightFrame.rightDivider.pack(side=ctk.TOP)
        
        self.rightFrame.bottom = ctk.CTkFrame(self.rightFrame,
                                                     width=955 * self.multX,
                                                     height=525 * self.multY
        )
        self.rightFrame.bottom.pack(side=ctk.TOP)

        # %% Top-level menu bar
        self.mainMenuBar = ctkmb.CTkMenuBar(self)
        self.mmb_file = self.mainMenuBar.add_cascade("File")
        self.mmb_option = self.mainMenuBar.add_cascade("Options")
        self.mmb_settings = self.mainMenuBar.add_cascade("Settings")
        self.mmb_about = self.mainMenuBar.add_cascade("About")
        self.mmb_fs = self.mainMenuBar.add_cascade("Full screen options")
        self.mmb_exit = self.mainMenuBar.add_cascade("Exit Application",
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
        
        self.dd_fs = ctkmb.CustomDropdownMenu(self.mmb_fs)
        self.dd_fs.add_option(option="Exit Fullscreen",
                              command=self.windowed
        )
        self.dd_fs.add_option(option="Enter Fullscreen",
                              command=self.fullscreen
        )
        
        # %% Finalizing setup
        # We call windowed manually on initialization for safe boot
        self.windowed()
        
    # %% Functions
    def recommendedE1E6(self, choice):
        i = 0
        while (i < len(eaf.state)):
            if str(choice) == eaf.state[i]:
                # Since the lists should be aligned (were grabbed line by line)
                #   We should be able to simply share the index.
                self.deltaE1 = eaf.e1[i]
                self.deltaE6 = eaf.e6[i]
                self.leftFrame.stepFour.right.e1Label.configure(
                    text="Delta e1: " + "{:.10f}".format(self.deltaE1)
                )
                self.leftFrame.stepFour.right.e6Label.configure(
                    text="Delta e6: " + "{:.10f}".format(self.deltaE6)
                )
                break
            i = i + 1
    
    def updateE1(self):
        try:
            self.deltaE1 = float(self.leftFrame.stepFour.mid.e1Entry.get())
            self.leftFrame.stepFour.mid.e1Entry.delete(0, 'end')
        except ValueError:
            self.popup = TopLevelWindow(geometry="300x150")
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(master=self.popup,
                text="Oops! You entered an invalid value for e1. \n"
                    + "Please try again to enter a numeric value",
                wraplength=300, justify="center"
            )
            self.popup.warningMessage.place(relx=.5, rely=.3,
                                            anchor=ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(self.popup,
                text="Close pop-up window",
                command=lambda: self.closePopup(self.popup)
            )
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
            self.popup.update()
        self.leftFrame.stepFour.right.e1Label.configure(text="Delta e1: "
                                                  + str(self.deltaE1)
        )
    
    def updateE6(self):
        try:
            self.deltaE6 = float(self.leftFrame.stepFour.mid.e6Entry.get())
            self.leftFrame.stepFour.mid.e6Entry.delete(0, 'end')
        except ValueError:
            self.popup = TopLevelWindow(geometry="300x150")
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(master=self.popup,
                text="Oops! You entered an invalid value for e6. \n"
                    + "Please try again to enter a numeric value",
                wraplength=300, justify="center"
            )
            self.popup.warningMessage.place(relx=.5, rely=.3,
                                            anchor=ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(self.popup,
                text="Close pop-up window",
                command=lambda: self.closePopup(self.popup)
            )
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
            self.popup.update()

        self.leftFrame.stepFour.right.e6Label.configure(text="Delta e6: "
                                                  + str(self.deltaE6)
        )
    
    def windowed(self):
        root.attributes("-fullscreen", False)
        root.geometry("1280x720")
        
        # Resize all elements to fit in the page.
        #   Some placement related modifications will need to be made.
        self.leftFrame.stepOne.pack(padx=2.5, pady=2.5, side=ctk.TOP)
        self.leftFrame.stepTwo.pack(padx=2.5, pady=2.5, side=ctk.TOP)
        self.leftFrame.stepThree.pack(padx=2.5, pady=2.5, side=ctk.TOP)
        self.leftFrame.stepFour.pack(padx=2.5, pady=2.5, side=ctk.TOP)
        self.leftFrame.stepFive.pack(padx=2.5, pady=2.5, side=ctk.TOP)
        self.leftFrame.stepSix.pack(padx=2.5, pady=2.5, side=ctk.TOP)
        self.leftFrame.stepSeven.pack(padx=2.5, pady=2.5, side=ctk.TOP)
        
        self.multX = 2 / 3
        self.multY = 2 / 3
        self.middleCol.configure(width=10 * self.multX,
                                 height=1080 * self.multY,
        )
        self.leftFrame.configure(width=955 * self.multX,
                                 height=1055 * self.multY
        )
        self.leftFrame.stepOne.configure(width=945 * self.multX,
                                         height=150 * self.multY
        )
        # Step one updates:
        self.leftFrame.stepOne.nameEntry.place(relx=.005,
                                               rely=.95,
                                               anchor="sw"
        )
        self.leftFrame.stepOne.nameSubmit.place(relx=.25,
                                                rely=.95,
                                                anchor="sw"
        )
        self.leftFrame.stepOne.projName.place(relx=.5,
                                              rely=.95,
                                              anchor="sw"
        )
        
        self.leftFrame.stepTwo.configure(width=945 * self.multX,
                                         height=150 * self.multY
        )
        self.leftFrame.stepThree.configure(width=945 * self.multX,
                                           height=150 * self.multY
        )
        self.leftFrame.stepFour.configure(width=945 * self.multX,
                                          height=150 * self.multY
        )
        # Step four updates:
        self.leftFrame.stepFour.left.configure(width=311 * self.multX,
                                               height=150 * self.multY
        )
        self.leftFrame.stepFour.mid.configure(width=311 * self.multX,
                                               height=150 * self.multY
        )
        self.leftFrame.stepFour.right.configure(width=311 * self.multX,
                                               height=150 * self.multY
        )
        
        self.leftFrame.stepFive.configure(width=945 * self.multX,
                                          height=150 * self.multY
        )
        # Step five updates:
        self.leftFrame.stepFive.depthList.place(relx=0.7, rely=.94,
                                                anchor="sw"
        )
        self.leftFrame.stepFive.depthList.configure(height=70)
        self.leftFrame.stepFive.depthEntry.place(relx=.46,
                                                 rely=.06,
                                                 anchor="nw"
        )
        self.leftFrame.stepFive.depthEntryButton.place(relx=.46,
                                                       rely=.36,
                                                       anchor="nw"
        )
        self.leftFrame.stepFive.depthDeleteButton.place(relx=.46,
                                                        rely=.66,
                                                        anchor="nw"
        )
        
        self.leftFrame.stepSix.configure(width=945 * self.multX,
                                         height=150 * self.multY
        )
        # Step six updates:
        self.leftFrame.stepSix.tempFileLabel.place(relx=.7,
                                                   rely=.05,
                                                   anchor="nw"
        )
        self.leftFrame.stepSix.windFileLabel.place(relx=.7,
                                                   rely=.38,
                                                   anchor="nw"
        )
        self.leftFrame.stepSix.solarFileLabel.place(relx=.7,
                                                    rely=.71,
                                                    anchor="nw"
        )
        
        self.leftFrame.stepSix.tempFileButton.place(relx=.46,
                                                    rely=.05,
                                                    anchor="nw"
        )
        self.leftFrame.stepSix.windFileButton.place(relx=.46,
                                                    rely=.38,
                                                    anchor="nw"
        )
        self.leftFrame.stepSix.solarFileButton.place(relx=.46,
                                                     rely=.71,
                                                     anchor="nw"
        )

        self.leftFrame.stepSeven.configure(width=945 * self.multX,
                                           height=75 * self.multY
        )
        self.rightFrame.configure(width=955 * self.multX,
                                  height=1080 * self.multY)
        self.rightFrame.rightFrameTop.configure(width=955 * self.multX,
                                                height=525 * self.multY
        )
        self.rightFrame.rightDivider.configure(width=960 * self.multX,
                                               height=10 * self.multY
        )
        self.rightFrame.bottom.configure(width=955 * self.multX,
                                                height=525 * self.multY
        )
        
        # Placement related modifications
        # Step 2
        self.leftFrame.stepTwo.projFolder.place(relx=.005, rely=.625,
                                                anchor="sw"
        )
        self.leftFrame.stepTwo.folderSubmit.place(relx=.005, rely=.95,
                                                  anchor="sw"
        )

    def fullscreen(self):
        root.attributes("-fullscreen", True)
        rect = RECT()
        ctypes.windll.user32.SystemParametersInfoW(48,
                                                   0,
                                                   ctypes.byref(rect),
                                                   0
        )
        screen_width, screen_height = rect.right, rect.bottom
        root.geometry(f'{screen_width}x{screen_height}+0+0')
        
        self.leftFrame.stepOne.pack(padx=5, pady=5, side=ctk.TOP)
        self.leftFrame.stepTwo.pack(padx=5, pady=5, side=ctk.TOP)
        self.leftFrame.stepThree.pack(padx=5, pady=5, side=ctk.TOP)
        self.leftFrame.stepFour.pack(padx=5, pady=5, side=ctk.TOP)
        self.leftFrame.stepFive.pack(padx=5, pady=5, side=ctk.TOP)
        self.leftFrame.stepSix.pack(padx=5, pady=5, side=ctk.TOP)
        self.leftFrame.stepSeven.pack(padx=5, pady=5, side=ctk.TOP)
        
        self.multX = 1
        self.multY = 1
        self.middleCol.configure(width=10 * self.multX,
                                 height=1080 * self.multY,
        )
        self.leftFrame.configure(width=955 * self.multX,
                                 height=1055 * self.multY
        )
        self.leftFrame.stepOne.configure(width=945 * self.multX,
                                         height=150 * self.multY
        )
        self.leftFrame.stepTwo.configure(width=945 * self.multX,
                                         height=150 * self.multY
        )
        self.leftFrame.stepThree.configure(width=945 * self.multX,
                                           height=150 * self.multY
        )
        self.leftFrame.stepFour.configure(width=945 * self.multX,
                                          height=150 * self.multY
        )
        
        # Step four updates:
        self.leftFrame.stepFour.left.configure(width=311 * self.multX,
                                               height=150 * self.multY
        )
        self.leftFrame.stepFour.mid.configure(width=311 * self.multX,
                                               height=150 * self.multY
        )
        self.leftFrame.stepFour.right.configure(width=311 * self.multX,
                                               height=150 * self.multY
        )
        
        self.leftFrame.stepFive.configure(width=945 * self.multX,
                                          height=150 * self.multY
        )
        self.leftFrame.stepSix.configure(width=945 * self.multX,
                                         height=150 * self.multY
        )
        self.leftFrame.stepSeven.configure(width=945 * self.multX,
                                           height=75 * self.multY
        )
        self.rightFrame.configure(width=955 * self.multX,
                                  height=1080 * self.multY)
        self.rightFrame.rightFrameTop.configure(width=955 * self.multX,
                                                height=525 * self.multY
        )
        self.rightFrame.rightDivider.configure(width=960 * self.multX,
                                               height=10 * self.multY
        )
        self.rightFrame.rightFrameBtm.configure(width=955 * self.multX,
                                                height=525 * self.multY
        )
        
        # Placement related modifications
        # Step 1
        self.leftFrame.stepOne.projName.place(relx=.005, rely=0, anchor="nw")
        self.leftFrame.stepOne.nameEntry.place(relx=.005, rely=.45,
                                               anchor="nw"
        )
        self.leftFrame.stepOne.nameSubmit.place(relx=.005, rely=.95,
                                                anchor="sw"
        )
        
        # Step 2
        self.leftFrame.stepTwo.projFolder.place(relx=.005, rely=.45,
                                                anchor="nw"
        )
        self.leftFrame.stepTwo.folderSubmit.place(relx=.005, rely=.95,
                                                  anchor="sw"
        )
        
        # Step 5
        self.leftFrame.stepFive.depthList.place(relx=0.0125, rely=.95,
                                                anchor="sw"
        )
        self.leftFrame.stepFive.depthList.configure(height=80)
        
        # Step 6
        self.leftFrame.stepSix.tempLabel.place(relx=.005, rely=.15,
                                               anchor="w"
        )
        self.leftFrame.stepSix.tempFileLabel.place(relx=.5025, rely=.15,
                                                   anchor="w"
        )
        self.leftFrame.stepSix.tempFileButton.place(relx=.1525, rely=.15,
                                                    anchor="w"
        )
        
        self.leftFrame.stepSix.windLabel.place(relx=.005, rely=.48, anchor="w")
        self.leftFrame.stepSix.windFileLabel.place(relx=.5025, rely=.48,
                                                   anchor="w"
        )
        self.leftFrame.stepSix.windFileButton.place(relx=.1525, rely=.48,
                                                    anchor="w"
        )
        
        self.leftFrame.stepSix.solarLabel.place(relx=.005, rely=.81,
                                                anchor="w"
        )
        self.leftFrame.stepSix.solarFileLabel.place(relx=.5025, rely=.81,
                                                    anchor="w"
        )
        self.leftFrame.stepSix.solarFileButton.place(relx=.1525, rely=.81,
                                                     anchor="w"
        )
        
    def updateName(self):
        shared.proj_name = str(self.leftFrame.stepOne.nameEntry.get())
        self.leftFrame.stepOne.projName.configure(text=shared.proj_name)
        self.leftFrame.stepOne.nameEntry.delete(0, "end")
    
    def updateTSB(self):
        try:
            if self.thicknessAC + self.thicknessBase \
                    + float(self.leftFrame.stepThree.tsbEntry.get()) \
                    > self.totalThickness:
                self.popup = TopLevelWindow(geometry="350x150")
                self.popup.title("Invalid subbase thickness!")
                
                self.popup.warningMessage = ctk.CTkLabel(self.popup,
                    text="Entered subbase value causes negative subgrade "
                            "value: \n\n(1) Enter new subbase value \n or \n"
                            "(2) Update base/AC thickness",
                    wraplength=350,
                    justify="center"
                )
                self.popup.warningMessage.place(relx=.5,
                                                rely=.3,
                                                anchor=ctk.CENTER
                )
                self.popup.exitPopup = ctk.CTkButton(self.popup,
                    text="Close pop-up window",
                    command=lambda: self.closePopup(self.popup)
                )
                self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
                
                self.popup.update()
            else:
                self.thicknessSubbase = float(
                    self.leftFrame.stepThree.tsbEntry.get()
                )
                
                self.thicknessSubgrade = self.totalThickness \
                                        - self.thicknessAC \
                                        - self.thicknessBase \
                                        - self.thicknessSubbase
                
                self.leftFrame.stepThree.tsbLabel.configure(
                    text=("Total subbase thickness:   "
                          + str(self.thicknessSubbase) + " m"))
                self.leftFrame.stepThree.tsbEntry.delete(0, "end")
        except ValueError:
            self.popup = TopLevelWindow(geometry="350x150")
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(master=self.popup,
                text="Oops! \n "
                    "You tried to enter an invalid value for the subbase "
                    "thickness. Ensure all values are entered as numeric",
                wraplength=350, justify="center"
            )
            self.popup.warningMessage.place(relx=.5, rely=.3,
                                            anchor=ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(self.popup,
                text="Close pop-up window",
                command=lambda: self.closePopup(self.popup)
            )
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
            self.popup.update()
    
    def updateTB(self):
        try:
            if self.thicknessAC \
                    + float(self.leftFrame.stepThree.tbEntry.get()) \
                    + self.thicknessBase \
                    > self.totalThickness:
                self.popup = TopLevelWindow(geometry="350x150")
                self.popup.title("Invalid base thickness!")
                
                self.popup.warningMessage = ctk.CTkLabel(self.popup,
                    text="Entered base value causes negative subgrade value:"
                            "\n\n(1) Enter new base value \n"
                            "or\n(2) Update AC/subbase thickness",
                    wraplength=350,
                    justify="center"
                )
                self.popup.warningMessage.place(relx=.5, rely=.3,
                                                anchor=ctk.CENTER)
                self.popup.exitPopup = ctk.CTkButton(self.popup,
                    text="Close pop-up window",
                    command=lambda: self.closePopup(self.popup)
                )
                self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
                
                self.popup.update()
            else:
                self.thicknessBase = float(
                    self.leftFrame.stepThree.tbEntry.get()
                )
                
                self.thicknessSubgrade = self.totalThickness \
                                        - self.thicknessAC \
                                        - self.thicknessBase \
                                        - self.thicknessSubbase
                
                self.leftFrame.stepThree.tbLabel.configure(
                    text=("Total base thickness:          "
                          + str(self.thicknessBase) + " m"))
                self.leftFrame.stepThree.tbEntry.delete(0, "end")
        except ValueError:
            self.popup = TopLevelWindow(geometry="350x150")
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(self.popup,
                text="Oops! \n"
                        "You tried to enter an invalid value for the base "
                        "thickness. Ensure all values are entered as numeric",
                wraplength=350, justify="center"
            )
            self.popup.warningMessage.place(relx=.5, rely=.3,
                                            anchor=ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(self.popup,
                text="Close pop-up window",
                command=lambda: self.closePopup(self.popup)
            )
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
            self.popup.update()

    def updateTAC(self):
        try:
            if float(self.leftFrame.stepThree.tacEntry.get()) \
                    + self.thicknessBase + self.thicknessSubbase \
                    > self.totalThickness:
                self.popup = TopLevelWindow(geometry="350x150")
                self.popup.title("Invalid asphalt concrete thickness!")
                
                self.popup.warningMessage = ctk.CTkLabel(self.popup,
                    text="Entered asphalt value causes negative subgrade "
                            "value:\n\n(1) Enter new AC value\nor\n"
                            "(2) Update base/subbase thickness",
                    wraplength=350,
                    justify="center"
                )
                self.popup.warningMessage.place(relx=.5, rely=.3,
                                                anchor=ctk.CENTER)
                self.popup.exitPopup = ctk.CTkButton(self.popup,
                    text="Close pop-up window",
                    command=lambda: self.closePopup(self.popup)
                )
                self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
                
                self.popup.update()
            else:
                self.thicknessAC = float(
                    self.leftFrame.stepThree.tacEntry.get()
                )
                
                self.thicknessSubgrade = self.totalThickness \
                                        - self.thicknessAC \
                                        - self.thicknessBase \
                                        - self.thicknessSubbase
                
                self.leftFrame.stepThree.tacLabel.configure(
                    text=("Total AC thickness:              "
                         + str(self.thicknessAC) + " m"))
                self.leftFrame.stepThree.tacEntry.delete(0, "end")
        except ValueError:
            self.popup = TopLevelWindow(geometry="350x150")
            self.popup.title("Invalid selection!")

            self.popup.warningMessage = ctk.CTkLabel(self.popup,
                text="Oops! \n"
                        "You tried to enter an invalid value for the total "
                        "thickness. Ensure all values are entered as numeric",
                wraplength=350, justify="center"
            )
            self.popup.warningMessage.place(relx=.5, rely=.3,
                                            anchor=ctk.CENTER)
            
            self.popup.exitPopup = ctk.CTkButton(master=self.popup,
                text="Close pop-up window",
                command=lambda: self.closePopup(self.popup)
            )
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
            self.popup.update()
    
    def removeDepth(self):
        selected_index = self.leftFrame.stepFive.depthList.curselection()
        if selected_index is not None:
            self.thermo_depth.pop(int(selected_index))
        else:
            self.popup = TopLevelWindow(geometry="300x100")
            self.popup.title("Nothing selected!")
            
            self.popup.warningMessage = ctk.CTkLabel(self.popup,
                                      text="No depth selected for deletion",
                                      wraplength=300, justify="center"
            )
            self.popup.warningMessage.place(relx=.5,
                                            rely=.3,
                                            anchor=ctk.CENTER
            )
            self.popup.exitPopup = ctk.CTkButton(self.popup,
                text="Close pop-up window",
                command=lambda: self.closePopup(self.popup)
            )
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
            self.popup.update()
    
    def addDepth(self):
        if len(self.thermo_depth) >= 10:
            self.popup = TopLevelWindow(geometry="300x150")
            self.popup.title("Too many depths!")
            
            self.popup.warningMessage = ctk.CTkLabel(
                self.popup,
                text="You've entered more than 10 depths!\n"
                        "Please only use the 10 most important depths.",
                wraplength=300,
                justify="center"
            )
            self.popup.warningMessage.place(relx=.5,
                                            rely=.3,
                                            anchor=ctk.CENTER
            )
            self.popup.exitPopup = ctk.CTkButton(self.popup,
                text="Close pop-up window",
                command=lambda: self.closePopup(self.popup)
            )
            self.popup.exitPopup.place(relx=.5, rely=.7, anchor=ctk.CENTER)
            
            self.popup.update()
        else:
            try:
                # Read the value in and append it to the list
                if float(self.leftFrame.stepFive.depthEntry.get()) \
                        > self.totalThickness:
                    self.popup = TopLevelWindow(geometry="300x100")
                    self.popup.title("Invalid depth!")
                    
                    self.popup.warningMessage = ctk.CTkLabel(self.popup,
                        text="Depth entered is larger than total depth, "
                                "select new value",
                        wraplength=300, justify="center"
                    )
                    self.popup.warningMessage.place(relx=.5,
                                                     rely=.3,
                                                     anchor=ctk.CENTER
                    )
                    self.popup.exitPopup = ctk.CTkButton(self.popup,
                        text="Close pop-up window",
                        command=lambda: self.closePopup(self.popup)
                    )
                    self.popup.exitPopup.place(relx=.5,
                                               rely=.7,
                                               anchor=ctk.CENTER
                    )
                    self.popup.update()
                else:
                    value = float(self.leftFrame.stepFive.depthEntry.get())
                    self.thermo_depth.append(value)
                    # Remove duplicates
                    self.thermo_depth = list(set(self.thermo_depth))
                    # Ensure the list stays in ascending order for readability
                    self.thermo_depth.sort()
                    self.leftFrame.stepFive.depthEntry.delete(0, 'end')
            except ValueError:
                self.popup = TopLevelWindow(geometry="300x150")
                self.popup.title("Invalid selection!")

                self.popup.warningMessage = ctk.CTkLabel(self.popup,
                    text="Oops!\n"
                            "You tried to enter an invalid value for the "
                            "depth list.\nEnsure all depth values are entered "
                            "as numeric",
                    wraplength=300,
                    justify="center"
                )
                self.popup.warningMessage.place(relx=.5, rely=.3,
                                                anchor=ctk.CENTER
                )
                
                self.popup.exitPp = ctk.CTkButton(master=self.popup,
                    text="Close pop-up window",
                    command=lambda: self.closePopup(self.popup)
                )
                self.popup.exitPp.place(relx=.5, rely=.7, anchor=ctk.CENTER)
                
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
                    
            if self.statsBool:
                # Ensure the list has .02 (used for Max temperature)
                self.thermo_depth.append(.02)
                # remove duplicates
                self.thermo_depth = list(set(self.thermo_depth))
                self.thermo_depth.sort()
            
            solarFile = self.solarFile
            windFile = self.windFile
            tempFile = self.tempFile
                    
            shared.running.set()
            self.simulation_thread = threading.Thread(
                target=self.run_simulation_in_thread(
                    self.post_process.get(), self.Ucode.get(),
                    solarFile=solarFile,
                    windFile=windFile,
                    tempFile=tempFile,
                    Thermo_depth=self.thermo_depth,
                    thickness_AC=self.thicknessAC,
                    thickness_Base=self.thicknessBase,
                    thickness_subbase=self.thicknessSubbase,
                    thickness_subgrade=self.thicknessSubgrade,
                    delta_e_1=self.deltaE1,
                    delta_e_6=self.deltaE6),
                daemon=True)
            self.simulation_thread.start()
            if self.statsBool:
                self.get_statistics()
        elif shared.running.is_set():
            # The simulation is already running, notify the user to be patient
            self.popup = TopLevelWindow(geometry="350x150")
            self.popup.title("Please wait!")
            
            self.popup.pleaseWait = ctk.CTkLabel(self.popup,
                text="Please wait while the simulation is running."
                        "\nRunning the simulation more than once at a "
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
            self.popup = TopLevelWindow(geometry="300x150")
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
            
    def run_simulation_in_thread(
            self, pp, uc, solarFile=None, windFile=None, tempFile=None,
            Thermo_depth=[], thickness_AC=0, thickness_Base=0,
            thickness_subbase=0, thickness_subgrade=0,
            delta_e_1=-.15, delta_e_6=-.12):
        
        self.popup = TopLevelWindow(geometry="350x150")
        self.popup.title("Simulation running, please wait")
        self.popup.pleaseWait = ctk.CTkLabel(self.popup,
                            text="Please wait while the simulation is running "
                                    "(popup will close)")
        self.popup.pleaseWait.pack()
        
 
        run_simulation(pp, uc,
                       # Check boxes, if these are true than we run post
                       #    processing and Ucode calibration respectively
                       solarFile=solarFile,
                       windFile=windFile,
                       tempFile=tempFile,
                       Thermo_depth=Thermo_depth,
                       thickness_AC=thickness_AC,
                       thickness_Base=thickness_Base,
                       thickness_subbase=thickness_subbase,
                       thickness_subgrade=thickness_subgrade,
                       delta_e_1=delta_e_1,
                       delta_e_6=delta_e_6
                       )
        
        shared.running.clear()
        shared.endEarly.clear()
        self.closePopup(self.popup)
            
    def blockSelectFile(self):
        self.popup = TopLevelWindow(geometry="350x150")
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
                    self.popup = TopLevelWindow(geometry="300x150")
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
                    self.popup = TopLevelWindow(geometry="300x150")
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
                    self.popup = TopLevelWindow(geometry="300x150")
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

    # Triggered whenever the user presses enter, checks all boxes for input and
    #   updates as necessary
    def clearEntries(self, event):
        potentialName = str(self.leftFrame.stepOne.nameEntry.get())
        if potentialName != "":
            self.updateName()
        potentialAC = str(self.leftFrame.stepThree.tacEntry.get())
        if potentialAC != "":
            self.updateTAC()
        potentialTSB = str(self.leftFrame.stepThree.tsbEntry.get())
        if potentialTSB != "":
            self.updateTSB()
        potentialTB = str(self.leftFrame.stepThree.tbEntry.get())
        if potentialTB != "":
            self.updateTB()
        potentialE1 = str(self.leftFrame.stepFour.mid.e1Entry.get())
        if potentialE1 != "":
            self.updateE1()
        potentialE6 = str(self.leftFrame.stepFour.mid.e6Entry.get())
        if potentialE6 != "":
            self.updateE6()
        potentialDepth = str(self.leftFrame.stepFive.depthEntry.get())
        if potentialDepth != "":
            self.addDepth()

    def update_depthlist(self):
        # Clear the listbox
        self.leftFrame.stepFive.depthList.delete("all")
        # Repopulate with the values in thermo_depth
        for depth in self.thermo_depth:
            self.leftFrame.stepFive.depthList.insert(ctk.END, depth)
    
    def get_statistics(self):
        if shared.running.is_set():
            print("repeat call")
            self.get_statistics().after(5000, self.get_statistics())
        else:
            stclc.run_calculations()
            
            self.rightFrame.bottom.info = ctk.CTkFrame(self.rightFrame.bottom)
            self.rightFrame.bottom.info.pack(padx=5, pady=5, side=ctk.LEFT)
            
            self.rightFrame.bottom.info.maxTitle = ctk.CTkLabel(
                self.rightFrame.bottom.info,
                text="Max",
                justify="left",
                font=("Segoe UI", 12,"underline"))
            self.rightFrame.bottom.info.maxTitle.pack(padx=5,
                                                      pady=5,
                                                      side=ctk.TOP)
            
            self.rightFrame.bottom.info.max7SurfTitle = ctk.CTkLabel(
                self.rightFrame.bottom.info,
                text="7 day surface: ")
            self.rightFrame.bottom.info.max7SurfTitle.pack(padx=5,
                                                       pady=5,
                                                       side=ctk.TOP)
            
            self.rightFrame.bottom.info.max720mmTitle = ctk.CTkLabel(
                self.rightFrame.bottom.info,
                text="7 day 20mm: ")
            self.rightFrame.bottom.info.max720mmTitle.pack(padx=5,
                                                       pady=5,
                                                       side=ctk.TOP)
            
            self.rightFrame.bottom.info.max3SurfTitle = ctk.CTkLabel(
                self.rightFrame.bottom.info,
                text="3 day Surface: ")
            self.rightFrame.bottom.info.max3SurfTitle.pack(padx=5,
                                                       pady=5,
                                                       side=ctk.TOP)
            
            self.rightFrame.bottom.info.max320mmTitle = ctk.CTkLabel(
                self.rightFrame.bottom.info,
                text="3 day 20mm: ")
            self.rightFrame.bottom.info.max320mmTitle.pack(padx=5,
                                                       pady=5,
                                                       side=ctk.TOP)
            
            self.rightFrame.bottom.info.max1SurfTitle = ctk.CTkLabel(
                self.rightFrame.bottom.info,
                text="1 day surface: ")
            self.rightFrame.bottom.info.max1SurfTitle.pack(padx=5,
                                                       pady=5,
                                                       side=ctk.TOP)
            
            self.rightFrame.bottom.info.max120mmTitle = ctk.CTkLabel(
                self.rightFrame.bottom.info,
                text="1 day 20mm: ")
            self.rightFrame.bottom.info.max120mmTitle.pack(padx=5,
                                                       pady=5,
                                                       side=ctk.TOP)
            
            self.rightFrame.bottom.info.minTitle = ctk.CTkLabel(
                self.rightFrame.bottom.info,
                text="Min",
                justify="left",
                font=("Segoe UI", 12,"underline"))
            self.rightFrame.bottom.info.minTitle.pack(padx=5,
                                                      pady=5,
                                                      side=ctk.TOP)
            
            self.rightFrame.bottom.info.min1Title = ctk.CTkLabel(
                self.rightFrame.bottom.info,
                text="1 day: ")
            self.rightFrame.bottom.info.min1Title.pack(padx=5,
                                                       pady=5,
                                                       side=ctk.TOP)
            
            for i in range(0, stclc.numYears):
                print("Creating frame for the year")
                frame = ctk.CTkFrame(self.rightFrame.bottom)
                self.rightFrame.bottom.frame.pack(relx=5, rely=5, side=ctk.LEFT)
                
                self.rightFrame.bottom.frame.title = ctk.CTkLabel(
                    self.rightFrame.bottom.frame, text="Year " + str(i + 1))
                self.rightFrame.bottom.frame.title.pack(relx=5,
                                                        rely=5,
                                                        side=ctk.TOP)
                
                self.rightFrame.bottom.frame.maxSurf7 = ctk.CTkLabel(
                    self.rightFrame.bottom.frame,
                    text=str(stclc.max7daySurf[i]))
                self.rightFrame.bottom.frame.max7.pack(relx=5,
                                                       rely=5,
                                                       side=ctk.TOP)
                self.rightFrame.bottom.frame.max20mm7 = ctk.CTkLabel(
                    self.rightFrame.bottom.frame,
                    text=str(stclc.max7day20mm[i]))
                self.rightFrame.bottom.frame.max20mm7.pack(relx=5,
                                                       rely=5,
                                                       side=ctk.TOP)
                
                self.rightFrame.bottom.frame.maxSurf3 = ctk.CTkLabel(
                    self.rightFrame.bottom.frame,
                    text=str(stclc.max3daySurf[i]))
                self.rightFrame.bottom.frame.maxSurf3.pack(relx=5,
                                                       rely=5,
                                                       side=ctk.TOP)
                self.rightFrame.bottom.frame.max20mm3 = ctk.CTkLabel(
                    self.rightFrame.bottom.frame,
                    text=str(stclc.max3day20mm[i]))
                self.rightFrame.bottom.frame.max20mm3.pack(relx=5,
                                                       rely=5,
                                                       side=ctk.TOP)
                
                self.rightFrame.bottom.frame.maxSurf1 = ctk.CTkLabel(
                    self.rightFrame.bottom.frame,
                    text=str(stclc.max1daySurf[i]))
                self.rightFrame.bottom.frame.maxSurf1.pack(relx=5,
                                                       rely=5,
                                                       side=ctk.TOP)
                self.rightFrame.bottom.frame.max20mm1 = ctk.CTkLabel(
                    self.rightFrame.bottom.frame,
                    text=str(stclc.max1day20mm[i]))
                self.rightFrame.bottom.frame.max20mm1.pack(relx=5,
                                                       rely=5,
                                                       side=ctk.TOP)
                
                self.rightFrame.bottom.frame.min = ctk.CTkLabel(
                    self.rightFrame.bottom.frame,
                    text=str(stclc.min1daySurf[i]))
                self.rightFrame.bottom.frame.min.pack(relx=5,
                                                       rely=5,
                                                       side=ctk.BOTTOM)
                
                # self.statFrames.append(frame)
            
            # for tempName in self.statFrames:
            #     tempName.pack(relx=5, rely=5, side=ctk.TOP)
            self.rightFrame.update()
        
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
    root.attributes('-fullscreen', False)
    root.resizable(False, False)
    root.geometry("1280x720")
    
    app = MainApp(root)
    app.pack(side="top", fill="both", expand=True)
    
    root.bind('<Return>', app.clearEntries)
    
    root.protocol("WM_DELETE_WINDOW", app._quit)
    
    main()
