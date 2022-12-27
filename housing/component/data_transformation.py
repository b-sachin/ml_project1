from housing.exception import HousingException
from housing.logger import logging
from housing.entity.config_entity import DataTransformationConfig
from housing.entity.artifact_entity import  DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact
import sys
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import pandas as pd
import numpy as np

from housing.util.util import read_yaml_file, save_preprocessing_obj, save_numpy_array_data, load_data
from housing.constant import *


class FeatureGenerator(BaseEstimator, TransformerMixin):
    def __init__(self, add_bedrooms_per_room = True,
                 total_rooms_ix = 3,
                 population_ix = 5,
                 households_ix = 6,
                 total_bedrooms_ix = 4,
                 columns = None):
    
        """
        FeatureGenerator Initialization
        add_bedrooms_per_room: bool
        total_rooms_ix: int index number of total rooms columns
        population_ix: int index number of total population columns
        households_ix: int index number of total households columns
        total_bedrooms_ix: int index number of total bedrooms columns
        """
        try:
            self.columns = columns
            if self.columns is not None:
                total_rooms_ix = self.columns.index(COLUMN_TOTAL_ROOMS)
                population_ix = self.columns.index(COLUMN_POPULATION)
                households_ix = self.columns.index(COLUMN_HOUSEHOLDS)
                total_bedrooms_ix = self.columns.index(COLUMN_TOTAL_BEDROOM)

            self.add_bedrooms_per_room = add_bedrooms_per_room
            self.total_rooms_ix = total_rooms_ix
            self.population_ix = population_ix
            self.households_ix = households_ix
            self.total_bedrooms_ix = total_bedrooms_ix
        except Exception as e:
            raise HousingException(e,sys) from e

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        try:
            room_per_household = X[:, self.total_rooms_ix] / X[:, self.households_ix]
            population_per_household = X[:, self.population_ix] / X[:, self.households_ix]
            if self.add_bedrooms_per_room:
                bedroom_per_room = X[:, self.total_bedrooms_ix] / X[:, self.total_rooms_ix]

                generated_feature = np.c_[X,room_per_household,population_per_household,bedroom_per_room]
            else:
                generated_feature = np.c_[X,room_per_household,population_per_household]
            
            return generated_feature
        except Exception as e:
            raise HousingException(e,sys) from e                


class DataTransformation:
    def __init__(self,
                 data_transformation_config: DataTransformationConfig,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact) -> DataTransformationArtifact:
        try:
            logging.info(f"{'='*20}Data Transformation log started.{'='*20}")
            self.data_transformation_config = data_transformation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
        except Exception as e:
            raise HousingException(e,sys) from e


    def get_data_transformer_object(self) -> ColumnTransformer:
        try:
            schema_file_path = self.data_validation_artifact.schema_file_path
            dataset_schema = read_yaml_file(file_path=schema_file_path)

            numerical_column = dataset_schema[DATASET_SCHEMA_NUMERICAL_COLUMN]
            categorical_column = dataset_schema[DATASET_SCHEMA_CATEGORICAL_COLUMN]

            num_pipeline = Pipeline(steps=[
                                ('imputer', SimpleImputer(strategy="median")),
                                ('feature_generator',FeatureGenerator(
                                    add_bedrooms_per_room=self.data_transformation_config.add_bedroom_per_room,
                                    columns=numerical_column
                                )),
                                ('scaling',StandardScaler())
                            ])

            cat_pipeline = Pipeline(steps=[
                                ('imputer', SimpleImputer(strategy="most_frequent")),
                                ('encoder',OneHotEncoder()),
                                ('scaling',StandardScaler(with_mean=False))  
                            ])

            logging.info(f"categorical columns: {categorical_column} ")
            logging.info(f"numerical columns: {numerical_column} ")


            preprocessing = ColumnTransformer([
                ('num_pipeline',num_pipeline,numerical_column),
                ('cat_pipeline',cat_pipeline,categorical_column)
            ])
        
            return preprocessing

        except Exception as e:
            raise HousingException(e,sys) from e

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info(f"Obtaining preprocessing object.")
            preprocessing_obj = self.get_data_transformer_object()

            logging.info(f"Obtaining training and test file path.")
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path =  self.data_ingestion_artifact.test_file_path
            schema_file_path = self.data_validation_artifact.schema_file_path

            logging.info(f"Loading training and testing data as pandas dataframe.")
            train_df = load_data(file_path=train_file_path, schema_file_path=schema_file_path)
            test_df = load_data(file_path=test_file_path, schema_file_path=schema_file_path)

            schema = read_yaml_file(file_path=schema_file_path)

            target_column_name = schema[DATASET_SCHEMA_TARGET_COLUMN]


            logging.info(f"Splitting input and target feature from training and testing dataframe.")
            input_feature_train_df = train_df.drop(columns=[target_column_name], axis=1)
            target_feature_train_df = train_df[target_column_name]

            input_feature_test_df = test_df.drop(columns=[target_column_name], axis=1)
            target_feature_test_df = test_df[target_column_name]


            logging.info(f"Applying preprocessing object on training and testing dataframe")
            input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)

            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]

            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]
            

            transform_train_dir = self.data_transformation_config.transformed_train_dir
            transform_test_dir = self.data_transformation_config.transformed_test_dir

            train_file_name = os.path.basename(train_file_path).replace(".csv",".npz")
            test_file_name = os.path.basename(test_file_path).replace(".csv",".npz")

            transformed_train_file_path = os.path.join(transform_train_dir,train_file_name)
            transformed_test_file_path = os.path.join(transform_test_dir,test_file_name)
            

            logging.info(f"Saving transformed training and testign array.")
            save_numpy_array_data(file_path=transformed_train_file_path,array=train_arr)
            save_numpy_array_data(file_path=transformed_test_file_path, array=test_arr)

            preprocessing_obj_file_path = self.data_transformation_config.preprocessed_object_file_path


            logging.info(f"Saving preprocessing object.")
            save_preprocessing_obj(file_path=preprocessing_obj_file_path, obj=preprocessing_obj)

            data_transformation_artifact = DataTransformationArtifact(
                                                is_transformed=True,
                                                message="Data Transformation Successful",
                                                transformed_train_file_path=transformed_train_file_path,
                                                transformed_test_file_path=transformed_test_file_path,
                                                preprocessed_object_file_path=preprocessing_obj_file_path)

            logging.info(f"data_transformation_artifact: {data_transformation_artifact} ")

            return data_transformation_artifact
            
        except Exception as e:
            raise HousingException(e,sys) from e

    def __del__(self):
    logging.info(f"{'='*20}Data Transformation log Completed. {'='*20} \n\n")