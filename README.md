# rheology

## Description:
In the DeForest lab, we are making user-tunable, injectable hydrogels. The tunability of these gels can be assessed by rheology. Unfortunately, the user interface for our rheometer does not allow for easy automation of data analysis and comparison between gels.

This package was designed to automate data analysis from a CSV collected on the AntonPaar rheometer in the Bindra Lab at the University of Washington. Features include:

- Graph average curves from up to 4 gel types on the same graph.
- Calculate strain crossover, angular frequency crossover, and recovery time.
- Segment and graph tests from "Overall_Test_Jenny" which includes: time sweep, strain sweep, frequency sweep, cyclic strain sweep, and rotational shear step test.

![cyclic strain](https://github.com/jennybennett/rheology/blob/main/pictures/cyclic_strain_sweep.PNG=100x)

## Prerequisites:
Python is the primary software for the 'rheology' package. Python 3.7 or higher version is recommended here. Meanwhile, serval python packages are also required in advance. They are pandas, numpy, and matplotlib, and can be easily installed by using conda, a package and environment control system. Refer to [here](https://docs.enthought.com/mayavi/mayavi/installation.html) for details on proper installation as well as other prerequisite packages.

## Installation:
Jump to a directory or create a new one where you want to save 'rheology' and then type the following command: git clone https://github.com/jennybennett/rheology.git

## License:
[MIT](https://opensource.org/licenses/MIT)
