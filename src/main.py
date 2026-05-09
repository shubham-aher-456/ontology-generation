"""Main FastAPI application entry point."""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
import logging
from datetime import datetime
import json

from config.settings import settings
from config.logging_config import setup_logging
from src.services.transcript_processor import TranscriptProcessor, TranscriptChunker
from src.services.ontology_generator import IncrementalOntologyGenerator
from src.services.llm_service import LLMService
from src.services.knowledge_graph_service import KnowledgeGraphService
from src.domain.models import Transcript, TranscriptChunk

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    yield
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Ontology Knowledge Base API for processing transcripts and generating ontologies",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
transcript_processor = TranscriptProcessor()
transcript_chunker = TranscriptChunker()
llm_service = LLMService()
ontology_generator = IncrementalOntologyGenerator(llm_service)
knowledge_graph_service = KnowledgeGraphService()

# In-memory storage for demo (replace with database in production)
transcripts_store = {}
chunks_store = {}
ontologies_store = {}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


@app.get("/config")
async def get_config():
    """Get application configuration (non-sensitive)."""
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "max_file_size_mb": settings.max_file_size_mb,
        "chunk_size_words": settings.chunk_size_words,
        "llm_provider": settings.llm_provider
    }


@app.post("/transcripts/upload")
async def upload_transcript(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Upload and process a transcript file."""
    try:
        # Validate file type
        if not file.filename.endswith(('.txt', '.md', '.json')):
            raise HTTPException(
                status_code=400, 
                detail="Only .txt, .md, and .json files are supported"
            )
        
        # Read file content
        content_bytes = await file.read()
        
        # Validate file
        validation_errors = transcript_processor.validate_file(file.filename, content_bytes)
        if validation_errors:
            raise HTTPException(status_code=400, detail=f"Validation errors: {'; '.join(validation_errors)}")
        
        # Extract text content
        text_content = transcript_processor.extract_text(file.filename, content_bytes)
        
        # Create transcript object using the correct model
        transcript = transcript_processor.create_transcript(
            filename=file.filename,
            content=text_content,
            user_id="default_user"
        )
        
        # Add optional metadata
        if title:
            transcript.metadata['title'] = title
        if description:
            transcript.metadata['description'] = description
        
        # Store in memory (replace with database in production)
        transcript_id = transcript.id
        transcripts_store[transcript_id] = transcript
        
        logger.info(f"Successfully processed transcript: {transcript_id}")
        
        return {
            "message": "Transcript uploaded and processed successfully",
            "transcript_id": transcript_id,
            "filename": transcript.filename,
            "word_count": len(transcript.content.split()),
            "upload_timestamp": transcript.upload_timestamp
        }
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")
    except Exception as e:
        logger.error(f"Error processing transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing transcript: {str(e)}")


@app.get("/transcripts")
async def list_transcripts():
    """List all uploaded transcripts."""
    return {
        "transcripts": [
            {
                "id": transcript.id,
                "filename": transcript.filename,
                "title": transcript.metadata.get('title', transcript.filename),
                "word_count": len(transcript.content.split()),
                "upload_timestamp": transcript.upload_timestamp
            }
            for transcript in transcripts_store.values()
        ]
    }


@app.get("/transcripts/{transcript_id}")
async def get_transcript(transcript_id: str):
    """Get a specific transcript by ID."""
    if transcript_id not in transcripts_store:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    transcript = transcripts_store[transcript_id]
    return {
        "id": transcript.id,
        "filename": transcript.filename,
        "title": transcript.metadata.get('title', transcript.filename),
        "content": transcript.content,
        "description": transcript.metadata.get('description'),
        "upload_timestamp": transcript.upload_timestamp,
        "word_count": len(transcript.content.split())
    }


@app.post("/transcripts/{transcript_id}/generate-ontology")
async def generate_ontology(transcript_id: str, user_id: str = "default_user"):
    """Generate ontology from a transcript."""
    if transcript_id not in transcripts_store:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    try:
        transcript = transcripts_store[transcript_id]
        
        # Create chunks from transcript
        chunks = transcript_chunker.chunk_transcript(transcript)
        chunks_store[transcript_id] = chunks
        
        logger.info(f"Created {len(chunks)} chunks for transcript {transcript_id}")
        
        # Generate ontology
        ontology_schema = ontology_generator.generate_from_chunks(
            chunks=chunks,
            transcript_id=transcript_id,
            user_id=user_id
        )
        
        # Store ontology
        ontologies_store[transcript_id] = ontology_schema
        
        logger.info(f"Generated ontology for transcript {transcript_id}")
        
        return {
            "message": "Ontology generated successfully",
            "transcript_id": transcript_id,
            "ontology_id": ontology_schema.id,
            "entities_count": len(ontology_schema.entities),
            "relationships_count": len(ontology_schema.relationships),
            "chunks_processed": len(chunks)
        }
        
    except Exception as e:
        logger.error(f"Error generating ontology: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating ontology: {str(e)}")


@app.get("/transcripts/{transcript_id}/ontology")
async def get_ontology(transcript_id: str):
    """Get the generated ontology for a transcript."""
    if transcript_id not in ontologies_store:
        raise HTTPException(status_code=404, detail="Ontology not found for this transcript")
    
    ontology = ontologies_store[transcript_id]
    return {
        "id": ontology.id,
        "transcript_id": ontology.transcript_id,
        "user_id": ontology.user_id,
        "created_at": ontology.created_at,
        "entities": [
            {
                "name": entity.name,
                "type": entity.entity_type.value,
                "description": entity.description,
                "properties": [
                    {
                        "name": attr.name,
                        "data_type": attr.data_type,
                        "required": attr.required,
                        "description": attr.description
                    }
                    for attr in entity.attributes
                ]
            }
            for entity in ontology.entities
        ],
        "relationships": [
            {
                "name": rel.name,
                "source": rel.source_entity,
                "target": rel.target_entity,
                "type": rel.cardinality,
                "description": rel.description,
                "properties": [
                    {
                        "name": prop.name,
                        "data_type": prop.data_type,
                        "required": prop.required,
                        "description": prop.description
                    }
                    for prop in rel.properties
                ]
            }
            for rel in ontology.relationships
        ]
    }


# ============= CHUNK ENDPOINTS =============

@app.get("/transcripts/{transcript_id}/chunks")
async def get_transcript_chunks(transcript_id: str):
    """Get chunks for a specific transcript."""
    if transcript_id not in chunks_store:
        raise HTTPException(status_code=404, detail="Chunks not found for this transcript")
    
    chunks = chunks_store[transcript_id]
    return {
        "transcript_id": transcript_id,
        "total_chunks": len(chunks),
        "chunks": [
            {
                "chunk_id": chunk.metadata.chunk_id,
                "position": chunk.metadata.position,
                "word_count": chunk.metadata.word_count,
                "content_preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
            }
            for chunk in chunks
        ]
    }


@app.get("/transcripts/{transcript_id}/chunks/{chunk_id}")
async def get_chunk_detail(transcript_id: str, chunk_id: str):
    """Get detailed content of a specific chunk."""
    if transcript_id not in chunks_store:
        raise HTTPException(status_code=404, detail="Chunks not found for this transcript")
    
    chunks = chunks_store[transcript_id]
    chunk = next((c for c in chunks if c.metadata.chunk_id == chunk_id), None)
    
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    return {
        "chunk_id": chunk.metadata.chunk_id,
        "transcript_id": transcript_id,
        "position": chunk.metadata.position,
        "word_count": chunk.metadata.word_count,
        "content": chunk.content,
        "created_at": chunk.metadata.created_at
    }


# ============= KNOWLEDGE GRAPH ENDPOINTS =============

@app.post("/transcripts/{transcript_id}/load-to-graph")
async def load_ontology_to_graph(transcript_id: str):
    """Load ontology into knowledge graph database."""
    if transcript_id not in ontologies_store:
        raise HTTPException(status_code=404, detail="Ontology not found for this transcript")
    
    try:
        ontology = ontologies_store[transcript_id]
        
        # Connect to knowledge graph
        knowledge_graph_service.connect()
        
        # Load ontology into graph
        stats = knowledge_graph_service.load_ontology(ontology)
        
        logger.info(f"Loaded ontology {transcript_id} to knowledge graph")
        
        return {
            "message": "Ontology loaded to knowledge graph successfully",
            "transcript_id": transcript_id,
            "ontology_id": ontology.id,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error loading ontology to graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading to graph: {str(e)}")
    finally:
        knowledge_graph_service.close()


@app.get("/knowledge-graph/statistics")
async def get_graph_statistics():
    """Get knowledge graph statistics."""
    try:
        knowledge_graph_service.connect()
        stats = knowledge_graph_service.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting graph statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")
    finally:
        knowledge_graph_service.close()


@app.get("/knowledge-graph/entity/{entity_name}")
async def find_entity(entity_name: str):
    """Find a specific entity in the knowledge graph."""
    try:
        knowledge_graph_service.connect()
        entity = knowledge_graph_service.find_entity(entity_name)
        
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return entity
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding entity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error finding entity: {str(e)}")
    finally:
        knowledge_graph_service.close()


@app.get("/knowledge-graph/entity/{entity_name}/relationships")
async def get_entity_relationships(entity_name: str, relationship_type: Optional[str] = None):
    """Get relationships for a specific entity."""
    try:
        knowledge_graph_service.connect()
        relationships = knowledge_graph_service.find_relationships(entity_name, relationship_type)
        
        return {
            "entity": entity_name,
            "relationship_type": relationship_type,
            "relationships": relationships
        }
    except Exception as e:
        logger.error(f"Error getting relationships: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting relationships: {str(e)}")
    finally:
        knowledge_graph_service.close()


@app.get("/knowledge-graph/entity/{entity_name}/neighbors")
async def get_entity_neighbors(entity_name: str, depth: int = 1):
    """Get neighboring entities."""
    try:
        knowledge_graph_service.connect()
        neighbors = knowledge_graph_service.get_entity_neighbors(entity_name, depth)
        
        return {
            "entity": entity_name,
            "depth": depth,
            "neighbors": neighbors
        }
    except Exception as e:
        logger.error(f"Error getting neighbors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting neighbors: {str(e)}")
    finally:
        knowledge_graph_service.close()


@app.get("/knowledge-graph/path/{start_entity}/{end_entity}")
async def find_path_between_entities(start_entity: str, end_entity: str, max_depth: int = 5):
    """Find path between two entities."""
    try:
        knowledge_graph_service.connect()
        path = knowledge_graph_service.find_path(start_entity, end_entity, max_depth)
        
        return {
            "start_entity": start_entity,
            "end_entity": end_entity,
            "max_depth": max_depth,
            "path": path
        }
    except Exception as e:
        logger.error(f"Error finding path: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error finding path: {str(e)}")
    finally:
        knowledge_graph_service.close()


@app.post("/knowledge-graph/query")
async def execute_cypher_query(query_request: dict):
    """Execute custom Cypher query."""
    try:
        cypher_query = query_request.get("query")
        parameters = query_request.get("parameters", {})
        
        if not cypher_query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        knowledge_graph_service.connect()
        results = knowledge_graph_service.query_graph(cypher_query, parameters)
        
        return {
            "query": cypher_query,
            "parameters": parameters,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")
    finally:
        knowledge_graph_service.close()


@app.post("/knowledge-graph/complex-query")
async def execute_complex_query(query_request: dict):
    """Execute complex natural language query."""
    try:
        question = query_request.get("question")
        
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        knowledge_graph_service.connect()
        result = knowledge_graph_service.complex_query(question)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing complex query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error executing complex query: {str(e)}")
    finally:
        knowledge_graph_service.close()


@app.delete("/knowledge-graph/clear")
async def clear_knowledge_graph():
    """Clear all data from knowledge graph."""
    try:
        knowledge_graph_service.connect()
        knowledge_graph_service.clear_database()
        
        return {"message": "Knowledge graph cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing graph: {str(e)}")
    finally:
        knowledge_graph_service.close()


# ============= LLM SERVICE ENDPOINTS =============

@app.post("/llm/generate-ontology")
async def generate_ontology_from_text(request: dict):
    """Generate ontology from raw text using LLM."""
    try:
        text_content = request.get("content")
        previous_context = request.get("previous_context")
        
        if not text_content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        ontology_data = llm_service.generate_ontology(text_content, previous_context)
        
        return {
            "message": "Ontology generated successfully",
            "ontology": ontology_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating ontology: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating ontology: {str(e)}")


# ============= UTILITY ENDPOINTS =============

@app.get("/ontologies")
async def list_all_ontologies():
    """List all generated ontologies."""
    return {
        "ontologies": [
            {
                "ontology_id": ontology.id,
                "transcript_id": ontology.transcript_id,
                "user_id": ontology.user_id,
                "entities_count": len(ontology.entities),
                "relationships_count": len(ontology.relationships),
                "created_at": ontology.created_at
            }
            for ontology in ontologies_store.values()
        ]
    }


@app.delete("/transcripts/{transcript_id}")
async def delete_transcript(transcript_id: str):
    """Delete a transcript and its associated data."""
    if transcript_id not in transcripts_store:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    # Remove from all stores
    del transcripts_store[transcript_id]
    if transcript_id in chunks_store:
        del chunks_store[transcript_id]
    if transcript_id in ontologies_store:
        del ontologies_store[transcript_id]
    
    return {"message": f"Transcript {transcript_id} deleted successfully"}


@app.get("/system/status")
async def get_system_status():
    """Get comprehensive system status."""
    try:
        # Try to connect to knowledge graph
        kg_status = "connected"
        try:
            knowledge_graph_service.connect()
            knowledge_graph_service.close()
        except:
            kg_status = "disconnected"
        
        return {
            "api_status": "running",
            "knowledge_graph_status": kg_status,
            "llm_service_status": "active",
            "transcripts_count": len(transcripts_store),
            "ontologies_count": len(ontologies_store),
            "chunks_count": sum(len(chunks) for chunks in chunks_store.values()),
            "version": settings.app_version,
            "environment": settings.environment
        }
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )