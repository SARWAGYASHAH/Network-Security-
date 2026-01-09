from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation 
from networksecurity.components.data_transformation import DataTransformation 
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig,TrainingPipelineConfig,DataValidationConfig,DataTransformationConfig
import sys
from networksecurity.entity.artifact_entity import DataIngestionArtifact


if __name__=='__main__':
    try:
        training_pipeline_config=TrainingPipelineConfig()
        dataingestionconfig=DataIngestionConfig(training_pipeline_config)# store file path configuration for data ingestion
        data_ingeston=DataIngestion(dataingestionconfig)
        logging.info("initiate the try block")
        x=data_ingeston.initialte_data_ingestion()
        logging.info("Data ingestion completed")

        datavalidationconfig=DataValidationConfig(training_pipeline_config)
        data_validation=DataValidation(x,datavalidationconfig)
        data_validation_artifact=data_validation.initiate_data_validation()
        logging.info("Data validation completed")
        print(data_validation_artifact)

        logging.info("Data trnsformation started")
        data_transformation_config=DataTransformationConfig(training_pipeline_config)
        data_transformation=DataTransformation(data_validation_artifact,data_transformation_config)
        data_transformation_artifact=data_transformation.initiate_data_trnsformation()
        print(data_transformation_artifact)
        logging.info("Data trnsformation completed")

    except Exception as e:
        raise NetworkSecurityException(e,sys) 
    