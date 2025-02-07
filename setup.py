from setuptools import setup, find_packages

setup(
    name='mdss',
    version='0.1.0',
    description='A package for running a series Aerodynamic and Aerostructural simulations using ADflow, and TACS simulations with mphys and openMDAO',
    author='Sinaendhran Pujali Elilarasan',
    packages=find_packages(include=['mdss', 'mdss.*']),
    python_requires='>=3.9',
    include_package_data=True,
    package_data={'mdss': ['resources/*.yaml']},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],  
)