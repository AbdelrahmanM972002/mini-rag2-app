<<<<<<< HEAD
from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypesEnums
import json


class NLPController(BaseController):

    def __init__(self, vectordb_client, embedding_client, generation_client, template_parser):
        super().__init__()
        self.generation_client = generation_client
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()

    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vetcor_db_collection_info(self, project: Project):

        collection_name = self.create_collection_name(project.project_id)

        if not self.vectordb_client.is_collection_existed(collection_name):
            return {
                "status": "empty",
                "message": "collection not created yet"
            }

        collection_info = self.vectordb_client.get_collection_info(collection_name)

        return json.loads(json.dumps(collection_info, default=lambda x: x.__dict__))

    # =========================================
    #  INDEXING
    # =========================================
    def index_into_vector_db(self, project, chunks, chunks_ids, do_reset=False):

        collection_name = self.create_collection_name(project.project_id)

        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]

        vectors = []

        for idx, text in enumerate(texts):

            vec = self.embedding_client.embed_text(
                text=text,
                document_type=DocumentTypesEnums.DOCUMENT.value
            )

            if vec is None:
                raise ValueError(f"Embedding failed at chunk {idx}")

            vectors.append(vec)

        if not vectors:
            raise ValueError("No vectors generated")

        embedding_size = len(vectors[0])

        self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=embedding_size,
            do_reset=do_reset
        )

        return self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadata=metadata,
            record_ids=chunks_ids
        )

    # =========================================
    #  SEARCH
    # =========================================
    def sreach_vector_db_collection(self, project: Project, text: str, limit: int = 4):

        collection_name = self.create_collection_name(project.project_id)

        if not self.vectordb_client.is_collection_existed(collection_name):
            return False

        vector = self.embedding_client.embed_text(
            text=text,
            document_type=DocumentTypesEnums.QUERY.value
        )

        if vector is None:
            raise ValueError("Query embedding failed")

        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        return results or False

    # =========================================
    #  RAG
    # =========================================
    def answer_rag_question(self, project: Project, query: str, limit: int = 5):

        answer, full_prompt, chat_history = None, None, None

        
        retrieved_documents = self.sreach_vector_db_collection(
            project=project,
            text=query,
            limit=limit * 2  
        )

        print("===== RETRIEVED CHUNKS =====")
        for r in retrieved_documents:
            print(r.score if hasattr(r, "score") else "NO SCORE")
            print(r.text)
            print("-----------")

        if not retrieved_documents:
            return answer, full_prompt, chat_history

        
        query_keywords = query.lower().split()

        filtered_documents = [
            doc for doc in retrieved_documents
            if any(keyword in doc.text.lower() for keyword in query_keywords)
        ]

        
        if not filtered_documents:
            filtered_documents = retrieved_documents

        
        sorted_documents = sorted(
            filtered_documents,
            key=lambda x: x.score if hasattr(x, "score") else 0,
            reverse=True
        )

        top_documents = sorted_documents[:limit]

        
        documents_prompt = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_num": idx + 1,
                "chunk_text": doc.text
            })
            for idx, doc in enumerate(top_documents)
        ])

        full_prompt = self.template_parser.get(
            "rag",
            "footer_prompt",
            {
                "documents": documents_prompt,
                "question": query
            }
        )

      
        answer = self.generation_client.generate_text(
            prompt=full_prompt
        )

        if not answer or not answer.strip():
            answer = "Sorry, I couldn't generate an answer based on the provided context."

=======
from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypesEnums
from typing import List
import json

class NLPController(BaseController):

    def __init__(self, vectordb_client, generation_client, 
                 embedding_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    
    def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                                   chunks_ids: List[int], 
                                   do_reset: bool = False):
        
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: manage items
        texts = [ c.chunk_text for c in chunks ]
        metadata = [ c.chunk_metadata for c in  chunks]
        vectors = [
            self.embedding_client.embed_text(text=text, 
                                             document_type=DocumentTypesEnums.DOCUMENT.value)
            for text in texts
        ]

        # step3: create collection if not exists
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # step4: insert into vector db
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids,
        )

        return True

    def search_vector_db_collection(self, project: Project, text: str, limit: int = 3):

        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: get text embedding vector
        vector = self.embedding_client.embed_text(text=text, 
                                                 document_type=DocumentTypesEnums.QUERY.value)

        if not vector or len(vector) == 0:
            return False

        # step3: do semantic search
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        if not results:
            return False

        return results
    
    def answer_rag_question(self, project: Project, query: str, limit: int = 2):

        answer, full_prompt, chat_history = None, None, None

        # step 1: retrieve
        retrieved_documents = self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit 
        )

        if not retrieved_documents:
            return answer, full_prompt, chat_history

        # step 2: sort by score (IMPORTANT FIX )
        retrieved_documents = sorted(
            retrieved_documents,
            key=lambda x: getattr(x, "score", 0),
            reverse=True
        )[:limit]

        # step 3: system prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")

        # step 4: documents
        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_num": idx + 1,
                "chunk_text": self.generation_client.process_text(doc.text),
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        # step 5: footer
        footer_prompt = self.template_parser.get("rag", "footer_prompt", {
            "query": query
        })

        # step 6: full prompt
        full_prompt = "\n\n".join([
            documents_prompts,
            footer_prompt
        ])

        # step 7: IMPORTANT FIX  system injection properly
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        # step 8: generate
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

>>>>>>> tut-012
        return answer, full_prompt, chat_history