from enum import Enum

class LLMEnums(Enum):
    
    OPENAI = "OPENAI"
    COHERE = "COHERE"
    
    
class OpenAIEnums(Enum):
    
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    
class CoHereEnums(Enum):
    # Fixed: Use lowercase for roles to match Cohere V2 requirements
    SYSTEM = "system" 
    USER = "user"
    ASSISTANT = "chatbot" # Cohere uses 'chatbot' as the assistant role
    
    DOCUMENT = "search_document"
    QUERY = "search_query"
    
class DocumentTypesEnums(Enum):
    
    DOCUMENT = "document"
    QUERY = "query"
    