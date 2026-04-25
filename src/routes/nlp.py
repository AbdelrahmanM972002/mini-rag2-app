from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest, SearchRequest
from models.PojectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers.NLPController import NLPController
from models import ResponseSignal
import logging
import json

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)

# =====================================
#  PUSH / INDEX
# =====================================
@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    collection_name = nlp_controller.create_collection_name(project.project_id)

    page_no = 1
    idx = 0
    inserted_items_count = 0
    collection_created = False

    while True:

        page_chunks = await chunk_model.get_poject_chunks(
            project_id=project.id,
            page_no=page_no
        )

        if not page_chunks:
            break

        page_no += 1

        texts = [c.chunk_text for c in page_chunks]

        vectors = []
        for i, text in enumerate(texts):

            vec = nlp_controller.embedding_client.embed_text(
                text=text,
                document_type="document"
            )

            #  FIX: None check
            if vec is None:
                raise ValueError(f" Embedding failed at chunk {i}")

            vectors.append(vec)

        #  create collection ONCE
        if not collection_created:
            embedding_size = len(vectors[0])

            nlp_controller.vectordb_client.create_collection(
                collection_name=collection_name,
                embedding_size=embedding_size,
                do_reset=push_request.do_reset
            )

            collection_created = True

        chunks_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        ok = nlp_controller.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadata=[c.chunk_metadata for c in page_chunks],
            record_ids=chunks_ids
        )

        if not ok:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value}
            )

        inserted_items_count += len(page_chunks)

    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )


# =====================================
#  INDEX INFO
# =====================================
@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    collection_name = nlp_controller.create_collection_name(project.project_id)

    if not nlp_controller.vectordb_client.is_collection_existed(collection_name):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": "COLLECTION_NOT_FOUND",
                "collection_info": None
            }
        )

    try:
        collection_info = nlp_controller.vectordb_client.get_collection_info(
            collection_name=collection_name
        )

        collection_info = json.loads(
            json.dumps(collection_info, default=lambda o: o.__dict__)
        )

    except Exception as e:
        logger.error(f"COLLECTION INFO ERROR: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": "COLLECTION_NOT_FOUND",
                "collection_info": None
            }
        )

    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )


# =====================================
#  SEARCH
# =====================================
@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    #  FIX: return [] instead of False
    results = nlp_controller.sreach_vector_db_collection(
        project=project,
        text=search_request.text,
        limit=search_request.limit
    )

    if not results:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value}
        )

    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_SEARCH_SUCCES.value,
            "results": [r.dict() for r in results]
        }
    )


# =====================================
#  RAG ANSWER
# =====================================
@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: str, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    answer, full_prompt, chat_history = nlp_controller.answer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit
    )

    if not answer:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.RAG_ANSWER_ERROR.value}
        )

    
    if hasattr(answer, "choices"):
        final_answer = answer.choices[0].message.content
    else:
        final_answer = answer

   
    if isinstance(final_answer, str):
        final_answer = final_answer.strip().strip('"').strip("'")

    return JSONResponse(
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": final_answer,
            # "full_prompt": full_prompt,
            "chat_history": chat_history
        }
    )