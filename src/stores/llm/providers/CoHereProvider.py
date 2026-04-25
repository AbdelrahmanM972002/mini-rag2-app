from stores.llm.LLMinterface import LLMInterface
import logging
from ..LLMEnums import CoHereEnums, DocumentTypesEnums
import cohere 

class CoHereProvider(LLMInterface):
    
    def __init__(self, api_key: str, default_input_max_characters: int=10000, 
                 default_generation_max_output_tokens: int=1000,
                 default_generation_temperature: float=0.1):
        
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = cohere.ClientV2(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        self.enums = CoHereEnums
        
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
                
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
            
    def process_text(self, text: str):
        return text[: self.default_input_max_characters].strip()
        
    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None, temperature: float = None):
        if not self.client or not self.generation_model_id:
            self.logger.error("Client or Generation Model ID not set")
            return None
            
        max_output_tokens = max_output_tokens or self.default_generation_max_output_tokens
        temperature = temperature or self.default_generation_temperature
            
        try:
            messages = chat_history + [self.construct_prompt(prompt, role="user")]
            
            # Debug: Check the outgoing prompt
            print(f"\n--- DEBUG START: Outgoing Messages ---\n{messages}\n--- DEBUG END ---\n")

            response = self.client.chat(
                model=self.generation_model_id,
                messages=messages,
                max_tokens=max_output_tokens,
                temperature=temperature
            )
            
            # Debug: Check the raw response object
            print(f"\n--- DEBUG START: Raw Cohere Response ---\n{response}\n--- DEBUG END ---\n")

            if not response or not response.message:
                self.logger.error("Empty response from Cohere")
                return None
            
            content = response.message.content
            
            if isinstance(content, list):
                result = "".join([block.text for block in content if hasattr(block, 'text')])
            else:
                result = content.text if hasattr(content, 'text') else str(content)

            # Debug: Check final extracted text
            print(f"\n--- DEBUG START: Extracted Text ---\n{result}\n--- DEBUG END ---\n")
            
            return result
            
        except Exception as e:
            self.logger.error(f"CoHere Generation Error: {str(e)}")
            print(f"Exception details: {e}")
            return None
        
    def embed_text(self, text: str, document_type: str = None):
        if not self.client or not self.embedding_model_id:
            return None
            
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
                return None
                
            return response.embeddings.float[0]
            
        except Exception as e:
            self.logger.error(f"CoHere Embedding Error: {str(e)}")
            return None
                
    def construct_prompt(self, prompt: str, role: str):
        return {
             "role": role,
             "content": prompt 
        }