from housing.logger import logging
from housing.exception import HousingException
from housing.entity.config_entity import DataValidationConfig
from housing.entity.artifact_entity import DataIngestionArtifact
from housing.constant import DATASET_SCHEMA_COLUMNS, DATASET_SCHEMA_DOMAIN_VALUE
from housing.util.util import read_yaml_file
import os, sys
import pandas as pd
import numpy as np

class DataValidation:

    def __init__(self, 
                 data_validation_config: DataValidationConfig,
                 data_ingestion_artifact:DataIngestionArtifact) -> None:
        try:
            self.data_validation_config=data_validation_config,
            self.data_ingestion_artifact=data_ingestion_artifact
        except Exception as e:
            raise HousingException(e,sys) from e

    def is_train_test_file_exists(self):
        try:
            logging.info("Checking if training and testing file exists?")
            is_train_file_exist = False
            is_test_file_exist = False

            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            is_train_file_exist = os.path.exists(train_file_path)
            is_test_file_exist = os.path.exists(test_file_path)

            is_available = is_train_file_exist and is_test_file_exist

            if not is_available:
                training_file = self.data_ingestion_artifact.train_file_path
                testing_file = self.data_ingestion_artifact.test_file_path
                raise Exception(f"Training file: {training_file} or Testing file: {testing_file} is not present")

            logging.info(f"is train and test file exists -> {is_available}")
            return is_available

        except Exception as e:
            raise HousingException(e,sys) from e

    def validate_dataset_schema(self) -> bool:
        try:
            validation_status = False

            logging.info("validating dataset schema")
            
            schema_file_path = self.data_validation_config.schema_file_path
            schema_info = read_yaml_file(file_path = schema_file_path )

            # 1. Cheking column count
            logging.info("Checking if column count in training and testing set matches to column count specified in schema")
            is_column_count_match = False

            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_data_frame = pd.read_csv(train_file_path)
            test_data_frame = pd.read_csv(test_file_path)

            train_column_count = len(train_data_frame.columns)
            test_column_count = len(test_data_frame.columns)

            schema_column_count = len(schema_info[DATASET_SCHEMA_COLUMNS])

            if (train_column_count == schema_column_count) and (test_column_count == schema_column_count):
                is_column_count_match = True
                logging.info(f"is column count of schema matches with taining and testing set column count -> {is_column_count_match}")
            else:
                raise Exception(f"Training Dataset Column count: {train_column_count} or Testing Dataset Column count: {test_column_count} does not match to Schema Column count: {schema_column_count}")

            # 2. Checking Values of Categorical columns
            logging.info(f"checking the values of 'ocean proximity' column of Schema Dataset with Training and Testing Dataset")
            
            domain_values_match = False
            
            schema_column_domain_values = list(schema_info[DATASET_SCHEMA_DOMAIN_VALUE].values())[0]

            train_column_domain_values = list(set(train_data_frame[DATASET_SCHEMA_DOMAIN_VALUE]))
            test_column_domain_values = list(set(test_data_frame[DATASET_SCHEMA_DOMAIN_VALUE]))

            if (train_column_domain_values.sort() == schema_column_domain_values.sort()) and (test_column_domain_values.sort() == schema_column_domain_values.sort()):
                domain_values_match = True
                logging.info(f"domain values of schema column matches with taining and testing set domain value column -> {domain_values_match}")
            else:
                raise Exception(f"Domain values of Training Dataset: {train_column_domain_values.sort()} or Domain values of Testing Dataset: {test_column_domain_values.sort()} does not match with Domain values of Schema Column: {schema_column_domain_values.sort()}")

            # 3. Checking all column names

            logging.info(f"checking all column names of Schema Dataset with Training and Testing Dataset")
            
            all_column_names_match = False
            
            schema_columns = schema_info[DATASET_SCHEMA_COLUMNS]
            schema_columns_list = list(schema_columns.keys())

            train_column_list = list(train_data_frame.columns)
            test_column_list = list(test_data_frame.columns)

            if (train_column_list.sort() == schema_columns_list.sort()) and (test_column_list.sort() == schema_columns_list.sort()):
                all_column_names_match = True
                logging.info(f"all column names of schema matches with taining and testing set column names -> {all_column_names_match}")
            else:
                raise Exception(f"Training Dataset Column names: {train_column_list.sort()} or Testing Dataset Column names: {test_column_list.sort()} does not match with Schema Column names: {schema_columns_list.sort()}")


            validation_status = all(is_column_count_match, domain_values_match, all_column_names_match)
            
            logging.info(f"is dataset schema validation successful -> {validation_status}")
            return validation_status
        except Exception as e:
            raise HousingException(e,sys) from e


    def initiate_data_validation(self):
        try:
            self.is_train_test_file_exists()
            self.validate_dataset_schema()

        except Exception as e:
            raise HousingException(e,sys) from e
