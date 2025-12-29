from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig,TrainingPipelineConfig
import sys

if __name__=='__main__':
    try:
        training_pipeline_config=TrainingPipelineConfig()
        dataingestionconfig=DataIngestionConfig(training_pipeline_config)
        data_ingeston=DataIngestion(dataingestionconfig)
        logging.info("initiate the try block")
        x=data_ingeston.initialte_data_ingestion()
        print(x)

    except Exception as e:
        raise NetworkSecurityException(e,sys) 
    