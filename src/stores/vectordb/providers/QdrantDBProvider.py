from ..VectoreDBInterface import VectorDBIterface
from logging import getLogger
from ..VectoreDBEnums import DistanceMethodEnums
from qdrant_client import models, QdrantClient
from typing import List
import uuid
from models.db_schemes import RetrievedDocument
class QdrantDBProvider(VectorDBIterface):
    
    def __init__(self, db_path: str, distance_method:str):
        
        self.client = None
        self.db_path = db_path
        self.distance_method = None
        
        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
            
        self.logger = getLogger(__name__)
        
    
    def connect(self):
        self.client = QdrantClient(path=self.db_path)
    
    def disconnect(self):
        self.client = None
        
    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        
    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):

        if do_reset:
            self.delete_collection(collection_name)

        if not self.is_collection_existed(collection_name):

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )
            return True

        return False
    
    def insert_one(self, collection_name:str, text:str, vector: list, metadata: dict =None, record_id: str =None):
        
        if not self.list_all_collections(collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        try:
            _= self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        vector = vector,
                        payload={
                            "text": text, "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting batch {e}")
            return False
        return True
    
    def insert_many(self, collection_name: str, texts: list, vectors: list, 
                metadata: list = None, record_ids: list = None,
                batch_size: int = 50):

        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        # 🧠 DEBUG 1: check lengths
        print(f"[DEBUG] texts={len(texts)}, vectors={len(vectors)}, metadata={len(metadata)}")

        # 🧠 DEBUG 2: detect None vectors BEFORE batching
        none_vectors = [i for i, v in enumerate(vectors) if v is None]
        if none_vectors:
            print(f"[ERROR] Found None embeddings at indexes: {none_vectors}")
            raise ValueError(f"❌ {len(none_vectors)} None vectors detected before insert")

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i: batch_end]
            batch_metadata = metadata[i: batch_end]
            batch_vectors = vectors[i: batch_end]
            batch_record_ids = record_ids[i: batch_end]

            # 🧠 DEBUG 3: batch inspection
            print(f"\n[DEBUG] Processing batch {i}-{batch_end}")
            print(f"[DEBUG] batch size = {len(batch_texts)}")

            # 🧠 DEBUG 4: check inside batch
            for x in range(len(batch_texts)):
                if batch_vectors[x] is None:
                    print(f"[ERROR] None vector in batch at index {x}")
                    print(f"[TEXT] {batch_texts[x][:100]}")
                    raise ValueError("❌ None vector found inside batch")

            batch_points = [
                models.PointStruct(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        "metadata": batch_metadata[x] or {}
                    }
                )
                for x in range(len(batch_texts))
            ]

            try:
                print(f"[DEBUG] Uploading batch to Qdrant...")

                self.client.upload_points(
                    collection_name=collection_name,
                    points=batch_points 
                )

                print(f"[SUCCESS] Batch {i}-{batch_end} inserted")

            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                print(f"[FATAL] Qdrant insert failed at batch {i}-{batch_end}")
                return False

        return True
        
    def search_by_vector(self, collection_name: str, vector: list, limit: int = 6):
        # if self.client is None:
        #     self.connect()

        # try:
            
        #     response = self.client.query_points(
        #         collection_name=collection_name,
        #         query=vector,
        #         limit=limit
        #     )
        #     return response.points
        # except Exception as e:
        #     self.logger.warning(f"Fallback to traditional search due to: {e}")
        #     return self.client.search(
        #         collection_name=collection_name,
        #         query_vector=vector,
        #         limit=limit
        #     )
        
        results = self.client.query_points(
            collection_name=collection_name,
             query=vector,
             limit=limit
        )
        if not results or not results.points:
            return None

        return [
            RetrievedDocument(
                id_document=str(result.id),
                score=result.score,
                text=result.payload.get("text", "")
            )
            for result in results.points
        ]
            