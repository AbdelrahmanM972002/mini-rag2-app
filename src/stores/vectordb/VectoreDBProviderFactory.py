from .providers import QdrantDBProviders
from controllers.BaseController import BaseController
from .VectoreDBEnums import VectorDBEnums
class VectoreDBProviderFactory:
    def __init__(self, config):
        self.config = config
        self.base_controller = BaseController()
        
    def create(self, providers: str):
        if providers == VectorDBEnums.QDRANT.value:
            db_path =  self.base_controller.get_database_path(db_name=self.config.VECTOR_DB_PATH)
            
            return QdrantDBProviders(
                db_path= db_path,
                distance_methon= self.config.VECTOR_DB_DISTANCE_METHOD
                    
                
            )
        return None