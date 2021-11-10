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

This plotter is attached to the RSSA instances and allows to display and save 2D plots of the RSSA.

The 2D plotting of a cylindrical RSSA and a planar one follow very different logics. For now only the cylindrical
plotting is considered.

TODO: Add the capability to plot planar RSSA files
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from rssa_analyzer.rssa import RSSA

import numpy as np

import matplotlib.colors as colors
import matplotlib.pyplot as plt


def closest(axis, values):
    """
    Given an axis (list of ordered equidistant values) and a value list, returns the indexes of the axis that are
     closest to the values.
    E.g. axis = [1, 2, 3, 4] value=[2.23, 4.98] result=[1, 2]
    """
    l0 = axis[0]
    lm = axis[1] - axis[0]
    idx = np.array((values - l0) / float(lm))
    idx = idx.astype(int)
    idx[idx == len(axis) - 1] = len(axis) - 2  # Limit case where the value lies at the end of the axis
    return idx


class Plotter:
    def __init__(self, rssa: RSSA):
        self.rssa = rssa
        return

    def calculate_grid_axes_cyl(self, z_int: int, theta_int: int, mask: np.ndarray = None):
        """The axes are calculated without taking into account the type of particle"""
        if mask is None:
            mask = np.where(self.rssa.x)[0]

        z_min = self.rssa.z[mask].min()
        z_max = self.rssa.z[mask].max()

        thetas = np.angle(self.rssa.x[mask] + 1j * self.rssa.y[mask])  # in radians
        theta_min = np.min(thetas)
        theta_max = np.max(thetas)

        z_axis = np.linspace(z_min, z_max, z_int + 1)
        theta_axis = np.linspace(theta_min, theta_max, theta_int + 1)
        return z_axis, theta_axis

    def generate_figures_current_cyl(self,
                                     particle: str = 'n',
                                     z_int: int = 10,
                                     theta_int: int = 10,
                                     source_intensity: float = 1.7757e20,
                                     value_range: Tuple[float, float] = None,
                                     mask: np.ndarray = None) -> Tuple[plt.Figure, plt.Figure]:
        particle_mask = self.rssa.get_particle_mask(particle)
        if mask is not None:  # Apply to the mask a geometry filter done earlier
            particle_mask = np.intersect1d(particle_mask, mask)

        # Create the empty grid
        z_axis, theta_axis = self.calculate_grid_axes_cyl(z_int, theta_int, particle_mask)
        grid_values = np.zeros((z_int, theta_int))
        error_grid = np.zeros((z_int, theta_int))

        # Calculate the indices at both axis of the grids for each track
        z_idx = closest(z_axis, self.rssa.z[particle_mask])
        thetas = np.angle(self.rssa.x[particle_mask] + 1j * self.rssa.y[particle_mask])  # in radians
        theta_idx = closest(theta_axis, thetas)
        del thetas  # To relax a bit memory constraints

        # Populate both grids
        np.add.at(grid_values, (z_idx, theta_idx), self.rssa.wgt[particle_mask])
        np.add.at(error_grid, (z_idx, theta_idx), 1)

        # Normalize values
        radius = np.linalg.norm([self.rssa.x[0], self.rssa.y[0]])  # radius of the cylinder
        extent = [radius * theta_axis[0], radius * theta_axis[-1], z_axis[0], z_axis[-1]]  # used in the plotting
        area = abs(radius * (theta_axis[1] - theta_axis[0]) * (z_axis[1] - z_axis[0]))
        grid_values /= area
        grid_values /= abs(self.rssa.parameters['np1'])  # grid /= nps
        grid_values *= source_intensity
        error_grid[np.where(error_grid == 0)] = 1  # Give a relative error of 1 to empty voxels
        error_grid = 1 / np.sqrt(error_grid)

        # Generate the figure values
        figure_values: plt.Figure = plt.figure()
        ax_values: plt.Axes = figure_values.add_subplot()
        ax_values.set_xlabel("Perimeter of the cylinder (cm)")
        ax_values.set_ylabel("Z (cm)")
        ax_values.set_title("Neutron current through the surface [n/cm2/s]")
        ax_values.imshow(grid_values, origin='lower', extent=extent)
        # Set the colors to log range
        if value_range is not None:
            log_max = int(np.log10(value_range[1]))
            log_min = int(np.log10(value_range[0]))
        else:
            log_max = int(np.log10(grid_values.max())) + 1  # The +1 is needed so max=1234 => 10.000
            log_min = log_max - 10
        decades = log_max - log_min
        image_values = ax_values.images[0]
        image_values.cmap = plt.get_cmap('jet', decades)  # set the colormap and number of bins
        image_values.norm = colors.LogNorm(np.power(10., log_min), np.power(10., log_max))  # set the scale as log
        _color_bar = figure_values.colorbar(image_values, orientation='horizontal')

        # Generate the errors figure
        figure_errors: plt.Figure = plt.figure()
        ax_errors: plt.Axes = figure_errors.add_subplot()
        ax_errors.set_xlabel("Perimeter of the cylinder (cm)")
        ax_errors.set_ylabel("Z (cm)")
        ax_errors.set_title("Relative error as 1/sqrt(N)")
        norm = colors.Normalize(0, 1)
        color_map = plt.get_cmap('jet', 10)
        ax_errors.imshow(error_grid, cmap=color_map, norm=norm, origin='lower', extent=extent)
        image_errors = ax_errors.images[0]
        figure_errors.colorbar(image_errors, orientation='horizontal')

        # Print information about the grid
        print(f"The area of a cell is {area:.2f}cm2")
        print(f"The resolution is {radius * (theta_axis[1] - theta_axis[0]):.2f}cm x {z_axis[1] - z_axis[0]:.2f}cm")

        return figure_values, figure_errors

    def plot_current_cyl(self,
                         particle: str = 'n',
                         z_int: int = 10,
                         theta_int: int = 10,
                         source_intensity: float = 1.7757e20,
                         value_range: Tuple[float, float] = None,
                         x_range: Tuple[float, float] = None,
                         z_range: Tuple[float, float] = None,
                         save_as: str = None):
        # Filter tracks location if necessary
        mask = None
        if z_range is not None:
            mask1 = np.where(self.rssa.z > z_range[0])
            mask2 = np.where(self.rssa.z < z_range[1])
            mask = np.intersect1d(mask1, mask2)
            del mask1, mask2
        if x_range is not None:
            thetas = np.angle(self.rssa.x + 1j * self.rssa.y)  # in radians
            radius = np.linalg.norm([self.rssa.x[0], self.rssa.y[0]])  # radius of the cylinder
            x_values = radius*thetas  # Perimeter of the cylinder values, x values in the plot x-axis
            mask1 = np.where(x_values > x_range[0])
            mask2 = np.where(x_values < x_range[1])
            mask = np.intersect1d(mask, mask1)
            mask = np.intersect1d(mask, mask2)
            del mask1, mask2, thetas, radius, x_values

        figure_values, figure_errors = self.generate_figures_current_cyl(particle=particle,
                                                                         z_int=z_int,
                                                                         theta_int=theta_int,
                                                                         source_intensity=source_intensity,
                                                                         value_range=value_range,
                                                                         mask=mask)
        if save_as is not None:
            figure_values.savefig(save_as+'.jpeg', format='jpeg', dpi=1200)
            figure_errors.savefig(save_as + '_errors.jpeg', format='jpeg', dpi=1200)
        plt.show()
        return


if __name__ == '__main__':
    from rssa import RSSA
    _rssa = RSSA('../tests/data/small_cyl.w')
    _rssa.plotter.plot_current_cyl('n', 100, 360,)
