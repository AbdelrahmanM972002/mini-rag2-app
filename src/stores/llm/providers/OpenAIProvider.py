from ..LLMinterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI
import logging

class OpenAIProvider(LLMInterface):

    def __init__(self, api_key: str, base_url: str=None,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        
        self.api_key = api_key
        self.base_url = base_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = OpenAI(
            api_key = self.api_key,
            base_url = self.base_url if self.base_url and len(self.base_url) else None
        )
       

        self.enums = OpenAIEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        if not text:
            return ""

        return str(text)[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):
        
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value)
        )

        response = self.client.chat.completions.create(
            model = self.generation_model_id,
            messages = chat_history,
            max_tokens = max_output_tokens,
            temperature = temperature
        )
        # print("RAW RESPONSE:")
        # print(response)
        # print("CHOICES:", response.choices)
        # print("MESSAGE:", response.choices[0].message)
        # print("CONTENT:", response.choices[0].message.content)

        if not response or not response.choices:
            self.logger.error("Empty response")
            return None

        message = response.choices[0].message

        answer = message.content if message.content and message.content.strip() else getattr(message, "reasoning", None)

        if not answer:
            self.logger.error("No valid output")
            return None

        return answer


    def embed_text(self, text: str, document_type: str = None):

        if not self.client:
            return None

        if not self.embedding_model_id:
            return None

        if not text or not text.strip():
            return None

        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input=text
        )

        return response.data[0].embedding
        
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": prompt
        }
    


    