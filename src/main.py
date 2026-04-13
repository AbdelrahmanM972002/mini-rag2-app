from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI
from routes import base 
from routes import data
from routes import nlp
from motor.motor_asyncio import AsyncIOMotorClient 
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
app = FastAPI()

async def startup_span():

    settings = get_settings()

    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    
    # vector db client
    app.vectordb_client = vectordb_provider_factory.create(
        providers=settings.VECTOR_DB_BACKEND
    )
    app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANGUAGE,
        default_language=settings.DEFAULT_LANGUAGE
    )


async def shutdown_span():
    app.mongo_conn.close()
    

    
app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)






# load_dotenv() 
# api_key = os.getenv("OPENAI_API_KEY")
# print(f"Key found: {api_key is not None}")


# from dotenv import load_dotenv
# import os
# from fastapi import FastAPI
# from motor.motor_asyncio import AsyncIOMotorClient 

# # استيراد المكونات الخاصة بمشروعك
# from routes import base, data, nlp
# from helpers.config import get_settings
# from stores.llm.LLMProviderFactory import LLMProviderFactory
# from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
# from stores.llm.templates.template_parser import TemplateParser


# load_dotenv()

# app = FastAPI()

# async def startup_span():

#     settings = get_settings()

#     print("\n" + "="*50)
#     print("🚀 NLP System Startup Debug Info:")
#     print(f"🔹 Generation Backend: [{settings.GENERATION_BACKEND}]")
#     print(f"🔹 Embedding Backend:  [{settings.EMBEDDING_BACKEND}]")
#     print(f"🔹 Generation Model:   [{settings.GENERATION_MODEL_ID}]")
#     print(f"🔹 Embedding Model:    [{settings.EMBEDDING_MODEL_ID}]")
#     print(f"🔹 Embedding Size:     [{settings.EMBEDDING_MODEL_SIZE}]")
#     print("="*50 + "\n")
#     # -------------------------------------------------------

#     # 2.MongoDB
#     app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
#     app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

#     # 3. Factories
#     llm_provider_factory = LLMProviderFactory(settings)
#     vectordb_provider_factory = VectorDBProviderFactory(settings)

#     # 4. Generation Client (Cohere)
#     app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
#     if app.generation_client:
#         app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
#     else:
#         print("❌ Error: Failed to create Generation Client!")

#     # 5. Embedding Client (Cohere)
#     app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
#     if app.embedding_client:
#         app.embedding_client.set_embedding_model(
#             model_id=settings.EMBEDDING_MODEL_ID,
#             embedding_size=settings.EMBEDDING_MODEL_SIZE
#         )
#     else:
#         print("❌ Error: Failed to create Embedding Client!")
    
#     # 6. Vector DB
#     app.vectordb_client = vectordb_provider_factory.create(
#         providers=settings.VECTOR_DB_BACKEND
#     )
#     app.vectordb_client.connect()

#     # 7.Template Parser
#     app.template_parser = TemplateParser(
#         language=settings.PRIMARY_LANGUAGE,
#         default_language=settings.DEFAULT_LANGUAGE
#     )

# async def shutdown_span():
#     app.mongo_conn.close()

# # (Startup/Shutdown)
# app.on_event("startup")(startup_span)
# app.on_event("shutdown")(shutdown_span)

# # إضافة المسارات (Routes)
# app.include_router(base.base_router)
# app.include_router(data.data_router)
# app.include_router(nlp.nlp_router)