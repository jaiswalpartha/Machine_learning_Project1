
from datetime import datetime
from housing.config.configuration import Configuration
from housing.constant import EXPERIMENT_DIR_NAME, EXPERIMENT_FILE_NAME
from housing.exception import HousingException
from housing.logger import logging
import os,sys
from housing.entity.artifact_entity import ModelPusherArtifact, DataIngestionArtifact, ModelEvaluationArtifact
from housing.entity.artifact_entity import DataValidationArtifact, DataTransformationArtifact, ModelTrainerArtifact
from housing.entity.config_entity import DataIngestionConfig, ModelEvaluationConfig
from housing.component.data_ingestion import DataIngestion
from housing.component.data_validation import DataValidation
from housing.component.data_transformation import DataTransformation
from housing.component.model_trainer import ModelTrainer
from housing.component.model_evaluation import ModelEvaluation
from housing.component.model_pusher import ModelPusher
from collections import namedtuple
from typing import List
from threading import Thread
import uuid

Experiment = namedtuple("Experiment", ["experiment_id","initiliation_timestamp","artifact_timestamp",
                                    "running_status","start_time","stop_time","execution_time","messages",
                                    "experiment_file_path","accuracy","is_model_accepted"])

config = Configuration()
class Pipeline(Thread):
    experiment = Experiment(*([None] * 11))

    experiment_file_path = os.path.join(config.training_pipeline_config.artifact_dir,
                                EXPERIMENT_DIR_NAME,EXPERIMENT_FILE_NAME)

    def __init__(self, config:Configuration =config) -> None:
        try:
            self.config = config
        except Exception as e:
            raise HousingException(e,sys) from e

    def start_data_ingestion(self)->DataIngestionArtifact:
        try:
            data_ingestion = DataIngestion(data_ingestion_config=self.config.get_data_ingestion_config())

            return data_ingestion.initiate_data_ingestion()
        except Exception as e:
            raise HousingException(e,sys) from e
    
    def start_data_validation(self,data_ingestion_artifact:DataIngestion)->DataIngestionArtifact:
        try:
            data_validation =DataValidation(data_validation_config=self.config.get_validation_config(),
                    data_ingestion_artifact=data_ingestion_artifact)

            return data_validation.initiate_data_validation()

        except Exception as e:
            raise HousingException(e,sys) from e

    def start_data_transformation(self,
                                    data_ingestion_artifact:DataIngestionArtifact,
                                    data_validation_artifact:DataValidationArtifact
                                    )->DataTransformationArtifact:
        try:
            data_transformation = DataTransformation(
                    data_transformation_config=self.config.get_transformation_config(),
                    data_ingestion_artifact=data_ingestion_artifact,
                    data_validation_artifact=data_validation_artifact)
            return data_transformation.initiate_data_transformation()
        except Exception as e:
            raise HousingException(e,sys) from e
    
    def start_model_trainer(self,data_transformation_artifact:DataTransformationArtifact)->ModelTrainerArtifact:

        try:
            model_trainer = ModelTrainer(model_trainer_config=self.config.get_model_trainer_config(),
                                         data_transformation_artifact=data_transformation_artifact
                                         )
            return model_trainer.initiate_model_trainer()
        except Exception as e:
            raise HousingException(e, sys) from e

    def start_model_evaluation(self, data_ingestion_artifact: DataIngestionArtifact,
                               data_validation_artifact: DataValidationArtifact,
                               model_trainer_artifact: ModelTrainerArtifact) -> ModelEvaluationArtifact:
        try:
            model_eval = ModelEvaluation(
                model_evaluation_config=self.config.get_model_evaluation_config(),
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact,
                model_trainer_artifact=model_trainer_artifact)
        except Exception as e:
            raise HousingException(e, sys) from e

    def start_model_pusher(self,model_eval_artifact: ModelEvaluationArtifact)->ModelPusherArtifact:
        try:
            model_pusher = ModelPusher(
                model_pusher_config=self.config.get_model_pusher_config(),
                model_evaluation_artifact=model_eval_artifact
            )
            return model_pusher.initiate_model_pusher()
        
        except Exception as e:
            raise HousingException(e, sys) from e

    
    
    def run_pipeline(self):
        try:
            if Pipeline.experiment.running_status:
                logging.info(f"Pipeline is already started")
                return Pipeline.experiment
            experiment_id = str(uuid.uuid4())

            Pipeline.experiment = Experiment(experiment_id=experiment_id,
                                            initiliation_timestamp=self.config.time_stamp,
                                            artifact_timestamp=self.config.time_stamp,
                                            running_status=True,
                                            start_time= datetime.now(),
                                            stop_time = None,
                                            execution_time = None,
                                            experiment_file_path= Pipeline.experiment_file_path,
                                            is_model_accepted=None,
                                            messages="Pipeline has been started",
                                            accuracy=None,)

            logging.info(f"Pipeline experiment: {Pipeline.experiment}")
             


            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact =self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact =self.start_data_transformation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact= data_validation_artifact
                )
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)

            model_evaluation_artifact = self.start_model_evaluation(data_ingestion_artifact=data_ingestion_artifact,
                                data_validation_artifact=data_validation_artifact,
                                model_trainer_artifact=model_trainer_artifact)
            if model_evaluation_artifact.is_model_accepted:
                model_pusher_artifact = self.start_model_pusher(model_eval_artifact=model_evaluation_artifact)
                logging.info(f'Model pusher artifact: {model_pusher_artifact}')
            else:
                logging.info("Trained model rejected.")
            logging.info("Pipeline completed.")

            stop_time = datetime.now()

            Pipeline.experiment = Experiment(experiment_id=Pipeline.experiment.experiment_id,
                                            initiliation_timestamp=self.config.time_stamp,
                                            artifact_timestamp=self.config.time_stamp,
                                            running_status=False,
                                            start_time=Pipeline.experiment.start_time,
                                            stop_time = stop_time,
                                            execution_time=stop_time - Pipeline.experiment.start_time,
                                            messages= "Pipeline has been completed",
                                            experiment_file_path=Pipeline.experiment_file_path,
                                            accuracy=model_trainer_artifact.model_accuracy,
                                            is_model_accepted=model_evaluation_artifact.is_model_accepted
                                            )
            logging.info(f"Pipeline Experiment: {Pipeline.experiment}")
            self.save_experiment()


        except Exception as e:
            raise HousingException(e,sys) from e


   # def save_experiment(self)::
    #    try:
     #       pass
      #  except Exception as e:
       #     raise HousingException(e,sys) from e