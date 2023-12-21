This module has been updated and integrated into [F4Enix](https://github.com/Fusion4Energy/F4Enix) as a submodule. Please check [F4Enix](https://github.com/Fusion4Energy/F4Enix) and its documentation. All future developments will be done at the F4Enix project. This repository will no longer be maintained.

# rssa_analyzer: Tool to read, analyze and plot RSSA files

The tool is a Python 3.7 based package that can load, analyze and plot RSSA files.

The tool can be used by means of a command line interface or by importing the RSSA class in 
custom user scripts or Jupyter Notebooks.

# Installation
The user can download this project from the main folder that contains the setup.py file the 
package can be installed via pip:
> pip install .

This should install all the dependencies and make the tool ready to use in the environment 
where it was installed.

# How to use
Once installed the tool can be started by executing the command:
> python -m rssa_analyzer

Then the command line interface will start-up and prompt the user with several commands like
reading a RSSA file, analyze it and plot it.

# Alternative use
This tool is built as a package that the user can import in her own Python scripts or 
programs. Inside a new Python script the user may write:
> from rssa_analyzer import RSSA\
> my_rssa = RSSA('path/to/ww_filename')

Now the user has access to the main functionality of the tool. The RSSA class has many 
interesting public methods and attributes, writing help(RSSA) will provide information on them.

# LICENSE
Copyright 2019 F4E | European Joint Undertaking for ITER and the Development of Fusion 
Energy (‘Fusion for Energy’). Licensed under the EUPL, Version 1.2 or - as soon they will
be approved by the European Commission - subsequent versions of the EUPL (the “Licence”).
You may not use this work except in compliance with the Licence. You may obtain a copy of
the Licence at: http://ec.europa.eu/idabc/eupl.html   
Unless required by applicable law or agreed to in writing, software distributed under
the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the Licence permissions and limitations under the Licence.

[src]: https://github.com/Radiation-Transport/rssa_analyzer
