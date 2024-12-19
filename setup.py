from setuptools import setup, find_packages

setup(
    name='simulateTestCases',
    version='0.1.0',
    description='A package for running a series of ADflow simulations using mphys and openMDAO',
    author='Sinaendhran Pujali Elilarasan',
    packages=find_packages(include=['simulateTestCases', 'simulateTestCases.*']),
    python_requires='>=3.9',
    include_package_data=True,
    package_data={'resources': ['simulateTestCases/resources/*.yaml']},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],  
)