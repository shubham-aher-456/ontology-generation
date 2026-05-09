"""LLM service for ontology generation with structured outputs."""
import logging
import time
import json
from typing import Dict, Any, List, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
from openai import AzureOpenAI
from pydantic import BaseModel, Field
from config.settings import settings

logger = logging.getLogger(__name__)


# Pydantic models for structured output
class AttributeSchema(BaseModel):
    """Schema for entity attributes."""
    name: str = Field(description="Attribute name")
    data_type: str = Field(description="Data type: string, integer, float, boolean, or date")
    required: bool = Field(default=False, description="Whether the attribute is required")
    description: str = Field(default="", description="Brief description of the attribute")


class EntitySchema(BaseModel):
    """Schema for entities."""
    name: str = Field(description="Entity name")
    type: str = Field(description="Entity type: concept, instance, or abstract")
    attributes: List[AttributeSchema] = Field(default_factory=list, description="List of attributes")
    parent_entities: List[str] = Field(default_factory=list, description="Parent entities for inheritance")
    description: str = Field(description="Brief description of the entity")


class RelationshipSchema(BaseModel):
    """Schema for relationships."""
    name: str = Field(description="Relationship name")
    source_entity: str = Field(description="Source entity name")
    target_entity: str = Field(description="Target entity name")
    cardinality: str = Field(description="Cardinality: one-to-one, one-to-many, many-to-one, or many-to-many")
    properties: List[AttributeSchema] = Field(default_factory=list, description="Relationship properties")
    description: str = Field(description="Brief description of the relationship")


class OntologyResponse(BaseModel):
    """Complete ontology response schema."""
    entities: List[EntitySchema] = Field(description="List of entities")
    relationships: List[RelationshipSchema] = Field(description="List of relationships")


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(
        self,
        failure_threshold: int = settings.circuit_breaker_failure_threshold,
        timeout_seconds: int = settings.circuit_breaker_timeout_seconds
    ):
        """Initialize circuit breaker."""
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.logger = logging.getLogger(__name__)
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            # Check if timeout has elapsed
            if self.last_failure_time and \
               datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.timeout_seconds):
                self.logger.info("Circuit breaker transitioning to HALF_OPEN")
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. Service unavailable. "
                    f"Retry after {self.timeout_seconds} seconds."
                )
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset if in HALF_OPEN
            if self.state == "HALF_OPEN":
                self.logger.info("Circuit breaker transitioning to CLOSED")
                self.state = "CLOSED"
                self.failure_count = 0
            
            return result
        
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            self.logger.warning(
                f"Circuit breaker failure {self.failure_count}/{self.failure_threshold}",
                extra={'error': str(e)}
            )
            
            if self.failure_count >= self.failure_threshold:
                self.logger.error("Circuit breaker transitioning to OPEN")
                self.state = "OPEN"
            
            raise


def retry_with_backoff(
    max_retries: int = settings.max_retries,
    initial_delay: int = settings.retry_initial_delay,
    exponential_base: int = settings.retry_exponential_base
):
    """Decorator for retry logic with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        delay = initial_delay * (exponential_base ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed. "
                            f"Retrying in {delay}s...",
                            extra={'error': str(e), 'delay': delay}
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed",
                            extra={'error': str(e)}
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


class LLMService:
    """Service for LLM-based ontology generation."""
    
    def __init__(self):
        """Initialize LLM service with Azure OpenAI."""
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.deployment_name = settings.azure_openai_deployment_name
        self.embedding_deployment = settings.azure_openai_embedding_deployment
        self.circuit_breaker = CircuitBreaker()
        self.logger = logging.getLogger(__name__)

    @retry_with_backoff()
    def _call_llm(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> OntologyResponse:
        """Call LLM with structured output using JSON schema."""
        # Use JSON mode with schema in prompt
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            temperature=temperature,
            max_tokens=8000,
            response_format={"type": "json_object"}
        )
        response_text = response.choices[0].message.content
        
        # Parse and validate with Pydantic
        try:
            data = json.loads(response_text)
            return OntologyResponse(**data)
        except Exception as e:
            self.logger.error(f"Failed to validate response with Pydantic: {str(e)}")
            # Return empty ontology if validation fails
            return OntologyResponse(entities=[], relationships=[])
    
    def generate_ontology(
        self,
        chunk_content: str,
        previous_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate ontology from transcript chunk with structured output."""
        self.logger.info("Generating ontology from chunk", extra={'chunk_length': len(chunk_content)})
        
        # Build prompt
        prompt = self._build_ontology_prompt(chunk_content, previous_context)
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert ontology engineer. Extract entities, relationships, and attributes from text to create structured ontologies. Always return valid JSON matching the specified schema."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # Call LLM with circuit breaker protection
        try:
            ontology_response = self.circuit_breaker.call(self._call_llm, messages, temperature=0.3)
            
            # Convert Pydantic model to dict
            ontology = {
                'entities': [
                    {
                        'name': entity.name,
                        'type': entity.type,
                        'attributes': [
                            {
                                'name': attr.name,
                                'data_type': attr.data_type,
                                'required': attr.required,
                                'description': attr.description
                            }
                            for attr in entity.attributes
                        ],
                        'parent_entities': entity.parent_entities,
                        'description': entity.description
                    }
                    for entity in ontology_response.entities
                ],
                'relationships': [
                    {
                        'name': rel.name,
                        'source_entity': rel.source_entity,
                        'target_entity': rel.target_entity,
                        'cardinality': rel.cardinality,
                        'properties': [
                            {
                                'name': prop.name,
                                'data_type': prop.data_type,
                                'required': prop.required,
                                'description': prop.description
                            }
                            for prop in rel.properties
                        ],
                        'description': rel.description
                    }
                    for rel in ontology_response.relationships
                ]
            }
            
            self.logger.info(
                "Ontology generated successfully with structured output",
                extra={
                    'entities_count': len(ontology['entities']),
                    'relationships_count': len(ontology['relationships'])
                }
            )
            
            return ontology
        
        except CircuitBreakerOpenError as e:
            self.logger.error("Circuit breaker open, service unavailable")
            raise
        except Exception as e:
            self.logger.error(f"Failed to generate ontology: {str(e)}")
            raise
    
    def _build_ontology_prompt(
        self,
        chunk_content: str,
        previous_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for ontology generation."""
        prompt = f"""Extract a structured ontology from the following text. 

TEXT:
{chunk_content}

"""
        
        if previous_context:
            prompt += f"""
PREVIOUS CONTEXT:
The following entities and relationships were extracted from previous chunks:
- Entities: {', '.join(previous_context.get('entity_names', [])[:20])}
- Relationships: {', '.join(previous_context.get('relationship_names', [])[:10])}

Please ensure consistency with these existing elements and identify any new connections.

"""
        
        prompt += """
INSTRUCTIONS:
1. Identify all entities (people, organizations, concepts, objects, events)
2. For each entity, extract attributes with proper data types
3. Identify all relationships between entities
4. Return ONLY valid JSON matching this exact schema

JSON SCHEMA:
{
  "entities": [
    {
      "name": "string (entity name)",
      "type": "string (concept|instance|abstract)",
      "attributes": [
        {
          "name": "string",
          "data_type": "string (string|integer|float|boolean|date)",
          "required": boolean,
          "description": "string"
        }
      ],
      "parent_entities": ["string (parent names)"],
      "description": "string"
    }
  ],
  "relationships": [
    {
      "name": "string (relationship name)",
      "source_entity": "string (source entity name)",
      "target_entity": "string (target entity name)",
      "cardinality": "string (one-to-one|one-to-many|many-to-one|many-to-many)",
      "properties": [],
      "description": "string"
    }
  ]
}

CRITICAL RULES:
- Return ONLY the JSON object
- No markdown, no code blocks, no explanations
- All fields must be present (use empty arrays/strings if no data)
- Entity and relationship names must match exactly in relationships
- Start response with { and end with }

Return the JSON now:
  ]
}

Return ONLY valid JSON, no additional text.
"""
        
        return prompt

    def _parse_ontology_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured ontology."""
        try:
            # Extract JSON from response (handle markdown code blocks)
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            ontology = json.loads(response_text)
            
            # Validate structure
            if 'entities' not in ontology:
                ontology['entities'] = []
            if 'relationships' not in ontology:
                ontology['relationships'] = []
            
            return ontology
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            self.logger.debug(f"Response text preview: {response_text[:500]}...")
            
            # Try to extract JSON from markdown code blocks
            try:
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    ontology = json.loads(json_str)
                    self.logger.info("Successfully extracted JSON from markdown code block")
                    
                    if 'entities' not in ontology:
                        ontology['entities'] = []
                    if 'relationships' not in ontology:
                        ontology['relationships'] = []
                    
                    return ontology
            except Exception as extract_error:
                self.logger.error(f"Failed to extract JSON from markdown: {str(extract_error)}")
            
            # Return empty ontology on parse failure
            return {'entities': [], 'relationships': []}
    
    def refine_schema(
        self,
        current_schema: Dict[str, Any],
        feedback: str,
        original_text: str
    ) -> Dict[str, Any]:
        """Refine schema based on user feedback."""
        self.logger.info("Refining schema based on feedback")
        
        prompt = f"""You are refining an ontology schema based on user feedback.

CURRENT SCHEMA:
{json.dumps(current_schema, indent=2)}

ORIGINAL TEXT:
{original_text[:2000]}...

USER FEEDBACK:
{feedback}

INSTRUCTIONS:
1. Analyze the user feedback carefully
2. Modify the schema according to the feedback
3. Maintain consistency with the original text
4. Preserve entities and relationships not mentioned in feedback
5. Return the complete updated schema in the same JSON format

Return ONLY valid JSON, no additional text.
"""
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert ontology engineer refining schemas based on user feedback."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response_text = self.circuit_breaker.call(self._call_llm, messages, temperature=0.3)
            refined_schema = self._parse_ontology_response(response_text)
            
            self.logger.info("Schema refined successfully")
            return refined_schema
        
        except Exception as e:
            self.logger.error(f"Failed to refine schema: {str(e)}")
            raise
    
    @retry_with_backoff()
    def compute_embedding(self, text: str) -> List[float]:
        """Compute embedding vector for text."""
        response = self.client.embeddings.create(
            model=self.embedding_deployment,
            input=text
        )
        return response.data[0].embedding
    
    def compute_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings for multiple texts."""
        self.logger.info(f"Computing embeddings for {len(texts)} texts")
        
        try:
            embeddings = []
            # Process in batches to avoid rate limits
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = self.circuit_breaker.call(
                    lambda: self.client.embeddings.create(
                        model=self.embedding_deployment,
                        input=batch
                    )
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            
            self.logger.info(f"Computed {len(embeddings)} embeddings")
            return embeddings
        
        except Exception as e:
            self.logger.error(f"Failed to compute embeddings: {str(e)}")
            raise
