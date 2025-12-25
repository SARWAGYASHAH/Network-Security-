'''setup.py is the configuration file that makes your Python project installable as a package.
contains metadata ,dependencies and more'''

from setuptools import find_packages,setup
from typing import List

def get_requirements()->List[str]:
    '''This function will return Lists of requirements'''
    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt','r') as file:
            #read lines
            lines=file.readlines()
            for line in lines:
                requirement=line.strip()
                if requirement and requirement!='-e.':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file not found")
    
    return requirement_lst

setup(
    name="Network Security",
    version="0.0.2",
    author="Sarwagya Shah",
    author_email="sarwagyashahonline@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)