from setuptools import setup, find_packages
from typing import List


#declaring variables for setup function


PROJECT_NAME="housing-predictor"
VERSION = "0.0.1"
AUTHOR = "Partha Jaiswal"
DESCRIPTION = "this is first ML project"

REQUIREMENT_FILE_NAME = "requirements.txt"


def  get_requirements_list()->List[str]:
    '''
    this function is going to return a list of all requirements
    retturn :list[all_libraries]
    '''
    with open(REQUIREMENT_FILE_NAME) as requirement_file:
        return requirement_file.readlines().remove("-e .")
    

setup(
    name = PROJECT_NAME,
    version = VERSION,
    author= AUTHOR,
    description=DESCRIPTION,
    packages= find_packages(),
    install_requires = get_requirements_list())


