from .providers import QdrantDBProvider, PGVectorProvider
from controllers.BaseController import BaseController
from sqlalchemy.orm import sessionmaker

from .VectoreDBEnums import VectorDBEnums

class VectorDBProviderFactory:

    def __init__(self, config, db_client: sessionmaker=None):
        self.config = config
        self.base_controller = BaseController()
        self.db_client = db_client


    def create(self, providers: str):
        if providers == VectorDBEnums.QDRANT.value:
            qdrant_db_client =  self.base_controller.get_database_path(db_name=self.config.VECTOR_db_client)
            
            return QdrantDBProvider(
                db_client= qdrant_db_client,
                distance_method= self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vecotr_size=self.config.EMBEDDING_MODEL_ID,
                index_threshhold=self.config.VECTOR_DB_PGVEC_INDEX_THERSHHOLD
                )


        if providers == VectorDBEnums.PGVECTOR.value:
            return PGVectorProvider(
                db_client=self.db_client,
                default_vecotr_size=self.config.EMBEDDING_MODEL_ID,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THERSHHOLD
            )
            
        return None