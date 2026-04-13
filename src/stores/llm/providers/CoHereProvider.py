from stores.llm.LLMinterface import LLMInterface
import logging
from ..LLMEnums import CoHereEnums, DocumentTypesEnums
import cohere 

class CoHereProvider(LLMInterface):
    
    def __init__(self, api_key: str, default_input_max_characters: int=1000, 
                 default_generation_max_output_tokens: int=1000,
                 default_generation_temperature: float=0.1):
        
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        # Initialize Cohere Client V2
        self.client = cohere.ClientV2(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        self.enums = CoHereEnums
        
    def set_generation_model(self, model_id: str):
        """Sets the model ID for text generation."""
        self.generation_model_id = model_id
                
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Sets the model ID and vector size for embeddings."""
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
            
    def process_text(self, text: str):
        """Cleans and truncates input text based on character limits."""
        return text[: self.default_input_max_characters].strip()
        
    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None, temperature: float = None):
        """Generates a response using the Cohere Chat API."""
        if not self.client:
            self.logger.error("Cohere client was not set")
            return None
            
        # Check for generation model instead of embedding model
        if not self.generation_model_id:
            self.logger.error("Generation model for Cohere was not set")
            return None
            
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature
            
        try:
            # Construct the messages list for V2 Chat API
            # chat_history should be a list of dicts: [{"role": "...", "content": "..."}]
            messages = chat_history + [self.construct_prompt(prompt, role="user")]
            
            response = self.client.chat(
                model=self.generation_model_id,
                messages=messages,
                max_tokens=max_output_tokens,
                temperature=temperature
            )
            
            if not response or not response.message:
                self.logger.error('Error while generating text with CoHere: Empty response')
                return None
            
            # Extract text from the first content block
            return response.message.content[0].text
            
        except Exception as e:
            self.logger.error(f"CoHere Generation Error: {str(e)}")
            return None
        
    def embed_text(self, text: str, document_type: str = None):
        """Generates embeddings for a given text."""
        if not self.client:
            self.logger.error("Cohere Client was not set")
            return None
            
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None
            
        # Determine input type (search_query vs search_document)
        input_type = CoHereEnums.DOCUMENT.value
        if document_type == DocumentTypesEnums.QUERY.value:
            input_type = CoHereEnums.QUERY.value 

        processed_text = self.process_text(text)   
        
        try:
            response = self.client.embed(
                model=self.embedding_model_id,
                texts=[processed_text],
                input_type=input_type,
                embedding_types=['float']
            )
            
            if not response or not response.embeddings or not response.embeddings.float:
                self.logger.error("Error while embedding text with CoHere")
                return None
                
            return response.embeddings.float[0]
            
        except Exception as e:
            self.logger.error(f"CoHere Embedding Error: {str(e)}")
            return None
                
    def construct_prompt(self, prompt: str, role: str):
        """Constructs a message dictionary in the format expected by Cohere V2."""
        return {
             "role": role,
             "content": self.process_text(prompt)
        }