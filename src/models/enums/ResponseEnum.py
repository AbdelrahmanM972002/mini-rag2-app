from enum import Enum 

class ResponseSignal(Enum):

    FILE_VALIDATE_SUCCESSFULLY = "File validate successfully"
    FILE_TYPES_NOT_SUPPORTED = "File type not supported"
    FILE_SIZE_EXCEEDED = "File size exceeded"
    FILE_UPLOAD_SUCCESS = "File upload success"
    FILE_UPLOAD_FAILED  = "File upload failed" 
    PROCESSING_FAILED = "Processing failed"
    PROCESSING_SUCCESS = "Processing Success"
    NO_FILES_ERROR = "not found files"
    FILE_ID_ERROR = "No file found with this id"
    PROJECT_NOT_FOUND_ERROR = "Project not nound nrror"
    INSERT_INTO_VECTORDB_ERROR = "Insert into vectordb error"
    INSERT_INTO_VECTORDB_SUCCESS = "Insert into vectordb success"
    VECTORDB_COLLECTION_RETRIEVED = "vectordb collection retrieved"
    VECTORDB_SEARCH_SUCCES = "vectordb search success"
    VECTORDB_SEARCH_ERROR = "vectordb search error"
    RAG_ANSWER_ERROR = "rAG answer error"
    RAG_ANSWER_SUCCESS = "rag answer success"
    