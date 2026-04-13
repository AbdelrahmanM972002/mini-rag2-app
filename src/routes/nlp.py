from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from models.enums.ResponseEnum import ResponseSignal
import logging
from routes.schemes.nlp import PushRequest, SearchRequest
from models.PojectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers.NLPController import NLPController


logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"]
)


@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    if not project:

        return JSONResponse(
             status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}
        )
    
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        template_parser=request.app.template_parser
    )

    has_records = True
    pag_no = 1
    insert_itmes_count = 0
    idx = 0

    while has_records:
        pag_chunks = await chunk_model.get_poject_chunks(project_id=project.id, page_no=pag_no)
        if len(pag_chunks):
            pag_no += 1
        if not pag_chunks or len(pag_chunks) == 0:
            has_records = False
            break
        chunk_ids = list(range(idx, idx + len(pag_chunks)))
        idx += len(pag_chunks)
        is_insert = nlp_controller.index_into_vector_db(
            project=project, chunks=pag_chunks, do_reset=push_request.do_reset, chunks_ids=chunk_ids
        )

        if not is_insert:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value}
        )
        insert_itmes_count += 1
    
    return JSONResponse(
            content={"signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
                     "insert_itmes_count":insert_itmes_count})


@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )


    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        template_parser = request.app.template_parser
    )

    collection_info = nlp_controller.get_vetcor_db_collection_info(project=project)
    
    return JSONResponse(
               content={
                "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
                "collection info": collection_info
               }
        )


@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )


    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        template_parser=request.app.template_parser
    )
    results = nlp_controller.sreach_vector_db_collection(
        project=project, 
        text= search_request.text,
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
                "results": [result.dict() for result in results]
               }
        )

    


@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: str, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )


    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        template_parser = request.app.template_parser
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
    
    return JSONResponse(
        content = {
            "Signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "Answer": answer,
            "Chat history": full_prompt,
            "Chat history": chat_history
        }
    )


