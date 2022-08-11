from housing.pipeline.pipeline import Pipeline
from housing.exception import HousingException
from housing.logger import logging
from housing.config.configuration import Configuration
import os
def main():
    try:
        config_path = os.path.join('config',"config.yaml")
        pipeline = Pipeline(Configuration(config_file_path=config_path))
        pipeline.run_pipeline()
        #pipeline.start()
        logging.info("main function execution completed")
        #data_transformation_config =Configuration().get_transformation_config()
        #print(data_transformation_config)

    except Exception as e:
        logging.info(f"{e}")
        print(e)

if __name__=="__main__":
    main()  

 