from abc import ABC, abstractmethed

class LLMInterface(ABC):
    
    
    @abstractmethed
    def set_generation_model(self, model_id: str):
        pass
    
    
    @abstractmethed
    def set_embedding_model(self, model_id: str, embedding_size:int):
        pass
    
    @abstractmethed
    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int =None, temperature: float=None):
        pass 
    
    
    @abstractmethed
    def embed_text(self, text:str, document_type: str = None):
        pass
    
    @abstractmethed
    def construct_prompt(self, prompt: str, role: str):
        pass
    
    