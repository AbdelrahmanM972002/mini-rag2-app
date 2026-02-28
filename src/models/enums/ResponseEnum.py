from enum import Enum 

class ResponseSignal(Enum):

    FILE_VALIDATE_SUCCESSFULLY = "File validate successfully"
    FILE_TYPES_NOT_SUPPORTED = "File type not supported"
    FILE_SIZE_EXCEEDED = "File size exceeded"
    FILE_UPLOAD_SUCCESS = "File upload success"
    FILE_UPLOAD_FAILED  = "File upload failed" 
    
    