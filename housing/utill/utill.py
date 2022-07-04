import yaml
from housing.exception import HousingException
import sys

# to read yaml file we will create a function
def read_yaml_file(file_path:str)->dict:
    '''reads a yaml file and returns the content as dict'''
    try:
        with open(file_path,"rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise HousingException(e ,sys) from e
        