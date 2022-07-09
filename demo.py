from housing.pipeline.pipeline import Pipeline
from housing.exception import HousingException
from housing.logger import logging
from housing.config.configuration import Configuration
def main():
    try:
        pipeline = Pipeline()
        pipeline.run_pipeline()
        #data_validation_config =Configuration().get_validation_config()
        #print(data_validation_config)

    except Exception as e:
        logging.info(f"{e}")
        print(e)

if __name__=="__main__":
    main()  

 