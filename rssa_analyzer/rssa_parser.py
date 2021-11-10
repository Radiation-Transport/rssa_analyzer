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

This file is used to read the RSSA binary files. I have based this parser on the implementation found at the
PyNE project and in the document la-ur-16-20109.pdf.

I had the need to write this parser myself as the one of PyNE was reading the tracks one by one and it proved too slow
for the RSSA files of over 5 Gbs we are working with (15 minutes of loading time reduced to 10-20 seconds).

The PyNE reader is more complete as it reads more information on the headers and it is able to read files produced
with different versions of MCNP. The current reader of this file has been tested only with RSSA files produced with
D1SUNED3.1.4.

This reader loads into memory the entirety of the RSSA binary file, for very heavy RSSAs we can encounter RAM
problems. This problem can be mitigated in future versions of the software.

TODO: Mitigate the RAM limitation problems
TODO: Add the ability to read the headers of more MCNP versions
"""
from typing import BinaryIO, Dict

import numpy as np

FILE_NAME = '../tests/data/E-Lite_IVVS_v5.5.w'
BYTE = np.byte
CHAR = np.char
INT = np.int32
FLOAT = np.float64
LONG = np.int64


def read_fortran_record(file: BinaryIO):
    count_1 = np.fromfile(file, INT, 1)[0]
    data = np.fromfile(file, np.byte, count_1)
    count_2 = np.fromfile(file, INT, 1)[0]
    if count_1 != count_2:
        raise ValueError("The integers that go before and after the Fortran record are not equal...")
    return data


def read_header(file: BinaryIO) -> Dict:
    # First record
    data = read_fortran_record(file)
    # The first line of the file with information like the code version, date and title
    format_record_id = data.tobytes().decode('UTF-8')
    if 'd1suned' in format_record_id:
        # TODO: we could parse and store information like datetime and title
        _last_dump = np.frombuffer(data[-4:], INT)
        pass
    else:
        raise NotImplementedError(f'The code that generated this RSSA file has not been implemented'
                                  f' in this parser, see the code here: {format_record_id}...')

    # Second record
    data = read_fortran_record(file)
    np1 = np.frombuffer(data, LONG, 1, 0)[0]
    nrss = np.frombuffer(data, LONG, 1, 8)[0]
    nrcd = np.frombuffer(data, INT, 1, 16)[0]
    njsw = np.frombuffer(data, INT, 1, 20)[0]
    niss = np.frombuffer(data, LONG, 1, 24)[0]
    if nrcd != 11:
        raise NotImplementedError(f"The amount of values recorded for each particle should be 11 instead of {nrcd}...")

    # Third record
    if np1 < 0:
        data = read_fortran_record(file)
        niwr, mipts, kjaq = np.frombuffer(data, INT, 3)
    else:
        raise NotImplementedError("The np1 value is not negative, as far as we understand it should be negative...")

    # Fourth record
    surfaces = []
    for i in range(njsw):
        data = read_fortran_record(file)
        surface = {'id': np.frombuffer(data, INT, 1, 0)[0]}
        if kjaq == 1:
            surface['info'] = np.frombuffer(data, INT, 1, 4)[0]
        else:
            surface['info'] = -1
        surface['type'] = np.frombuffer(data, INT, 1, 8)[0]
        surface['num_params'] = np.frombuffer(data, INT, 1, 12)[0]
        surface['params'] = np.frombuffer(data, INT, offset=16)
        surfaces.append(surface)

    # we read any extra records as determined by njsw+niwr...
    # no known case of their actual utility is known currently
    for j in range(njsw, njsw + niwr):
        _data = read_fortran_record(file)
        raise NotImplementedError('njsw + niwr values are bigger than njsw, behavior not explained')

    # Summary record
    _data = read_fortran_record(file)
    # Summary record not processed, its information does not interest us for now

    parameters = {'np1': np1,  # Number of histories of the simulation, given as a negative number
                  'nrss': nrss,  # Number of tracks recorded
                  'nrcd': nrcd,  # Number of values recorded for each particle, it should be 11
                  'njsw': njsw,  # Number of surfaces in JASW
                  'niss': niss,  # Number of different histories that reached the SSW surfaces
                  'niwr': niwr,  # Number of cells in RSSA file
                  'mipts': mipts,  # Source particle type
                  'kjaq': kjaq,  # Flag for macrobodies surfaces
                  'surfaces': surfaces}
    return parameters


def read_tracks(file: BinaryIO) -> np.ndarray:
    # Particle records
    # Read the whole remaining of the file at once, store all the bytes as a 1D numpy array
    data = np.fromfile(file, BYTE)
    # Reshape the array so each index holds the information of a single particle, we can do this because we
    #  know that the particle records have always the same length, 96 bytes
    data = data.reshape(-1, 96)
    # Remove the first and last 4 bytes, these are two integers that tell the record is 88 bytes long
    data = data[:, 4:-4]
    # Convert the array into a 1D array of float numbers instead of simply bytes
    data = np.frombuffer(data.flatten(), FLOAT)
    # Reshape the array so each index holds the information of a single particle, all the data is already converted
    #  from bytes to floats
    data = data.reshape(-1, 11)
    return data


def read_rssa(filename: str):
    with open(filename, 'rb') as infile:
        # This parameters hold information like the amount of histories or the amount of tracks recorded
        parameters = read_header(infile)

        tracks = read_tracks(infile)

    return parameters, tracks


if __name__ == '__main__':
    _parameters, _tracks = read_rssa(FILE_NAME)
    print(_tracks.shape)
