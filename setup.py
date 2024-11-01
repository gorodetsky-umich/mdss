from setuptools import setup, find_packages

setup(
    name='simulateTestCases',
    version='0.1.0',
    description='A package for running a series of ADflow simulations using mphys and openMDAO',
    author='Sinaendhran Pujali Elilarasan',
    # url='https://github.com/yourusername/my_simulation_package',
    packages=find_packages(include=['simulateTestCases', 'simulateTestCases.*']),
    install_requires=[
        'numpy', 
        'scipy', 
        'pyyaml', 
        'matplotlib', 
        'pandas', 
        'mpi4py', 
        'petsc4py',
        'openmdao',
        'adflow', # Requires custom installation
        'mphys', # Requires custom installation
    ],

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)