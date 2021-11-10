"""
########################################################################################################
# Copyright 2019 F4E | European Joint Undertaking for ITER and the Development                         #
# of Fusion Energy (‘Fusion for Energy’). Licensed under the EUPL, Version 1.2                         #
# or - as soon they will be approved by the European Commission - subsequent versions                  #
# of the EUPL (the “Licence”). You may not use this work except in compliance                          #
# with the Licence. You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl.html       #
# Unless required by applicable law or agreed to in writing, software distributed                      #
# under the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES                             #
# OR CONDITIONS OF ANY KIND, either express or implied. See the Licence permissions                    #
# and limitations under the Licence.                                                                   #
########################################################################################################
Author: Alvaro Cubi

This file implements a basic CLI to use the tool.

Due to the specific nature of the work with RSSA the recommended use of this tool involves using it as a package
in custom python scripts or within a Jupyter notebook for example. This allows a great degree of customization of the
plots and analyses.

This CLI interface however provides an easy entry point to use the tool without much hustle to do the most basic
(and maybe the most useful) operations like plotting the RSSA file for quick inspection.
"""

import os
from enum import Enum
from typing import List

from rssa_analyzer.rssa import RSSA

MAIN_MENU = """
 ***********************************************
                RSSA analyzer
 ***********************************************
 * Open RSSA file                       (open)   
 * Display RSSA information             (info)   
 * Plot                                 (plot)
 * Plot with many customization options (custom)
 * Exit                                 (end)    
"""


class Command(Enum):
    RUN = 'run'
    OPEN = 'open'
    INFO = 'info'
    PLOT = 'plot'
    CUSTOM_PLOT = 'custom'
    END = 'end'


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


class Menu:
    def __init__(self):
        self.rssa_list: List[RSSA] = []
        self.command: Command = Command.RUN
        self.subtext = ''
        self.loop()
        return

    @property
    def rssa_filenames(self):
        return [rssa.filename for rssa in self.rssa_list]

    def loop(self):
        while True:
            if self.command == Command.RUN:
                self.command_run()
            elif self.command == Command.OPEN:
                self.command_open()
            elif self.command == Command.INFO:
                self.command_info()
            elif self.command == Command.PLOT:
                self.command_plot()
            elif self.command == Command.CUSTOM_PLOT:
                self.command_custom_plot()
            elif self.command == Command.END:
                self.command_end()
                break
        return

    def select_rssa_index(self):
        # In case there is only 1 file loaded there is no need to ask
        if len(self.rssa_list) == 1:
            return 0

        for i in range(len(self.rssa_list)):
            print(f"[{i}]: {self.rssa_list[i].filename}")
        inp = input(" select the rssa by index: ")
        try:
            idx = int(inp)
            if idx not in [x for x in range(len(self.rssa_list))]:
                print("Index not among possible options...")
                return self.select_rssa_index()
            return idx
        except ValueError:
            print("Not a valid index...")
            return self.select_rssa_index()

    def go_main_menu(self, subtext: str = None):
        self.command = Command.RUN
        if subtext:
            self.subtext = subtext
        return

    def get_command(self):
        command_str = input(" enter action: ")
        try:
            self.command = Command(command_str)
        except ValueError:
            self.command = Command.RUN
            self.subtext = 'Invalid action...'
        return

    # Commands Main Menu ##############################################

    def command_run(self):
        clear_screen()
        print(MAIN_MENU)
        if self.subtext:
            print(self.subtext)
        self.subtext = ''
        self.get_command()
        return

    def command_open(self):
        filename = input(" enter rssa file name: ")
        if filename in self.rssa_filenames:
            return self.go_main_menu('RSSA filename already loaded...')
        try:
            rssa = RSSA(filename)
            self.rssa_list.append(rssa)
            return self.go_main_menu('RSSA file loaded!')
        except FileNotFoundError:
            return self.go_main_menu("File not found for this path or filename...")

    def command_info(self):
        if len(self.rssa_list) == 0:
            return self.go_main_menu("No RSSA files loaded...")
        idx = self.select_rssa_index()
        rssa = self.rssa_list[idx]
        return self.go_main_menu(rssa.get_info())

    def command_plot(self):
        if len(self.rssa_list) == 0:
            return self.go_main_menu("No RSSA files loaded...")
        idx = self.select_rssa_index()
        rssa = self.rssa_list[idx]
        surf_type = rssa.type
        if surf_type == 'cyl':
            particle = input('Enter the particle type (n, p): ')
            z_int = input('Enter amount of z ints: ')
            theta_int = input('Enter amount of theta ints: ')
            source_intensity = input('Enter source intensity: ')
            try:
                rssa.plotter.plot_current_cyl(particle=particle,
                                              z_int=int(z_int),
                                              theta_int=int(theta_int),
                                              source_intensity=float(source_intensity),
                                              save_as=rssa.filename + 'PLOT')
            except ValueError:
                self.go_main_menu("Some parameter introduced was incorrect...")
            self.go_main_menu()
        else:
            self.go_main_menu("The RSSA contains a non cylindrical surface, not implemented yet...")
            return

    def command_custom_plot(self):
        if len(self.rssa_list) == 0:
            return self.go_main_menu("No RSSA files loaded...")
        idx = self.select_rssa_index()
        rssa = self.rssa_list[idx]
        surf_type = rssa.type
        if surf_type == 'cyl':
            particle = input('Enter the particle type (n, p): ')
            z_int = input('Enter amount of z ints: ')
            theta_int = input('Enter amount of theta ints: ')
            source_intensity = input('Enter source intensity: ')
            try:
                value_range = input('[Optional - leave blank] Enter value range (e.g.: 1e2, 1e8): ')
                value_range = float(value_range.split(',')[0]), float(value_range.split(',')[1])
            except (ValueError, IndexError):
                value_range = None
                print("No value range selected")
            try:
                x_range = input('[Optional - leave blank] Enter X axis range (e.g.: -200, 600): ')
                x_range = float(x_range.split(',')[0]), float(x_range.split(',')[1])
            except (ValueError, IndexError):
                x_range = None
                print("No x range selected")
            try:
                z_range = input('[Optional - leave blank] Enter Z axis range (e.g.: -200, 600): ')
                z_range = float(z_range.split(',')[0]), float(z_range.split(',')[1])
            except (ValueError, IndexError):
                z_range = None
                print("No z range selected")
            try:
                rssa.plotter.plot_current_cyl(particle=particle,
                                              z_int=int(z_int),
                                              theta_int=int(theta_int),
                                              source_intensity=float(source_intensity),
                                              value_range=value_range,
                                              x_range=x_range,
                                              z_range=z_range,
                                              save_as=rssa.filename + 'PLOT')
            except ValueError:
                self.go_main_menu("Some parameter introduced was incorrect...")
            self.go_main_menu()
        else:
            self.go_main_menu("The RSSA contains a non cylindrical surface, not implemented yet...")
            return
        self.go_main_menu()
        return

    @staticmethod
    def command_end():
        print("Thanks for using rssa_analyzer, see you soon!")
        return


if __name__ == '__main__':
    Menu()
