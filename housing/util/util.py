import yaml
from housing.exception import HousingException
import sys,os
import numpy as np
import dill
from housing.constant import *
import pandas as pd

def read_yaml_file(file_path:str) -> dict:
    """
    Reads a YAML file and returns the contents as a dictinory .
    """

    try:
        with open(file_path,"rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise HousingException(e, sys) from e


def load_data(file_path:str, schema_file_path: str) -> pd.DataFrame:
        try:
            dataset_schema = read_yaml_file(schema_file_path) 
            schema = dataset_schema[DATASET_SCHEMA_COLUMNS] 

            dataframe = pd.read_csv(file_path)

            error_message = ""

            for i in dataframe.columns:
                if i in list(schema.keys()):
                    dataframe[i].astype(schema[i])
                else:
                    error_message = f"{error_message} \nColumn: [{i}] is not in the schema. "

            if len(error_message)>0:
                raise Exception(error_message)
            return dataframe

        except Exception as e:
            raise HousingException(e,sys) from e


def save_numpy_array_data(file_path:str, array:np.array):
    """
    Save numpy array data to file
    file_path: str location of file to save
    array: np.array data to save
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok = True)
        with open(file_path,"wb") as file_obj:
            np.save(file_obj,array)
    except Exception as e:
        raise HousingException(e,sys) from e

def load_numpy_array_data(file_path:str) -> np.array:
    """
    load numpy array data from file
    file_path: str location of file to load
    return: np.array data loaded
    """
    try:
        with open(file_path,"rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise HousingException(e,sys) from e

def save_preprocessing_obj(file_path:str, obj):
    """
    Save obj to pickle file
    file_path: str location of file to save
    obj: object to save
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok = True)
        with open(file_path,"wb") as file_obj:
            dill.dump(obj,file_obj)
    except Exception as e:
        raise HousingException(e,sys) from e


def load_preprocessing_obj(file_path:str):
    """
    load numpy array data from file
    file_path: str location of file to load
    return: np.array data loaded
    """
    try:
        with open(file_path,"rb") as file_obj:
            return dill.load(file_obj)
    except Exception as e:
        raise HousingException(e,sys) from e