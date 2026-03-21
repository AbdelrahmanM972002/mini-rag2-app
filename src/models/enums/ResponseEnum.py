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
    
   
    
    