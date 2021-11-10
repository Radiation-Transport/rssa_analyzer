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

This file contains the main class of this tool, RSSA which represents an RSSA file. It has many public properties
that allow for an easy access to information on the tracks to develop further  plotting and data analysis capabilities.

The size of a python RSSA instance is around the same as the RSSA binary file itself. When dealing with RSSA files
that weight many Gbs the RAM limitations may become a problem. This kind of problem can be mitigated both in the
reader and in the RSSA class in the future if deemed necessary.

TODO: Take into account the RAM limitation due to very heavy files
TODO: Implement tests
"""
import numpy as np

from rssa_analyzer.plotter import Plotter
from rssa_analyzer.rssa_parser import read_rssa


class RSSA:
    """
    Representation of a RSSA file.

    Attributes
    __________
    self.parameters: Dict
        {np1,  # Number of histories of the simulation, given as a negative number
         nrss,  # Number of tracks recorded
         nrcd,  # Number of values recorded for each particle, it should be 11
         njsw,  # Number of surfaces in JASW
         niss,  # Number of different histories that reached the SSW surfaces
         niwr,  # Number of cells in RSSA file
         mipts,  # Source particle type
         kjaq,  # Flag for macrobodies surfaces
         surfaces}
    self.tracks: np.ndarray
        each index of the array has 11 values
       0 a,  # History number of the particle, negative if uncollided
       1 b,  # Packed variable, the sign is the sign of the third direction cosine, starts with 8 = neutron, 16 = photon
       2 wgt,
       3 erg,
       4 tme,
       5 x,
       6 y,
       7 z,
       8 u,  # Particle direction cosine with X-axis
       9 v,  # Particle direction cosine with Y-axis, to calculate w (Z-axis) use the sign from b
      10 c  # Surface id
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.parameters, self.tracks = read_rssa(filename)
        self.plotter = Plotter(self)
        return

    def __repr__(self):
        return self.get_info()

    def get_info(self) -> str:
        info = f'RSSA file {self.filename} was recorded using the following surfaces:\n'
        for surface in self.parameters['surfaces']:
            info += f'  Surface id: {surface["id"]}\n'

        sur_type = self.type
        if sur_type == 'cyl':
            info += f'The surface type is a cylinder with a radius of {np.linalg.norm([self.x[0], self.y[0]]):.2f}\n'
        elif sur_type == 'plane':
            info += f'The surface type is a plane...\n'

        n_tracks = self.tracks[self.mask_neutron_tracks].shape[0]
        p_tracks = self.tracks[self.mask_photon_tracks].shape[0]
        info += f'The total amount of tracks recorded is {self.parameters["nrss"]}, of which {n_tracks} were neutrons' \
                f' and {p_tracks} were photons.\n'

        info += f'The simulation that produced this RSSA run {np.abs(self.parameters["np1"])} histories\n' \
                f'The amount of independent histories that reached the RSSA surfaces was {self.parameters["niss"]}.\n'
        return info

    @property
    def mask_neutron_tracks(self) -> np.ndarray:
        bitarrays = np.abs(self.tracks[:, 1])  # Get all the bitarrays and don't pay attention to the sign
        n_tracks = np.where(bitarrays < 9e8)[0]  # Neutrons start with 8 and photons with 16 followed by 1e8
        return n_tracks

    @property
    def mask_photon_tracks(self):
        bitarrays = np.abs(self.tracks[:, 1])  # Get all the bitarrays and don't pay attention to the sign
        p_tracks = np.where(bitarrays >= 9e8)[0]  # Neutrons start with 8 and photons with 16 followed by 1e8
        return p_tracks

    def get_particle_mask(self, particle: str):
        if particle == 'n':
            return self.mask_neutron_tracks
        elif particle == 'p':
            return self.mask_photon_tracks
        else:
            raise ValueError(f"Particle was {particle}, not n or p...")

    @property
    def x(self) -> np.ndarray:
        return self.tracks[:, 5]

    @property
    def y(self) -> np.ndarray:
        return self.tracks[:, 6]

    @property
    def z(self) -> np.ndarray:
        return self.tracks[:, 7]

    @property
    def wgt(self) -> np.ndarray:
        return self.tracks[:, 2]

    @property
    def energies(self) -> np.ndarray:
        return self.tracks[:, 3]

    @property
    def histories(self) -> np.ndarray:
        return np.abs(self.tracks[:, 0])

    @property
    def type(self):
        # If there are more than 1 surface we cannot say if it is a cyl or a plane
        if len(self.parameters['surfaces']) > 1:
            return 'multiple'
        # Assume it is a cyl and calculate the radius of its tracks, if they are different it is a plane
        radius = np.sqrt(self.x ** 2 + self.y ** 2)
        if np.std(radius) < 1e-4:
            return 'cyl'
        else:
            return 'plane'


if __name__ == '__main__':
    rssa = RSSA('../tests/data/small_cyl.w')
    print(rssa)
