# Always prefer setuptools over distutils
from setuptools import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='rssa_analyzer',
    version='1.0.0',
    description='Tool to read, analyze and plot RSSA files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='EUL',
    url='https://github.com/Radiation-Transport/rssa_analyzer',
    author='Alvaro Cubi',
    keywords='MCNP, radiation, RSSA, SSW, SSR',

    packages=['rssa_analyzer'],  # Required
    python_requires='>=3.7',

    install_requires=['numpy',
                      'matplotlib'],
    extras_require={
        'test': ['unittest'],
    },

    entry_points={
        'console_scripts': [
            'rssa_analyzer = rssa_analyzer.__main__:main',
        ],
    },
)