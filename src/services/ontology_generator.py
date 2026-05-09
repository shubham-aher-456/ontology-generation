"""Ontology generation service with incremental processing."""
import logging
from typing import List, Dict, Any, Optional
from src.domain.models import (
    TranscriptChunk, OntologySchema, EntityDefinition,
    RelationshipDefinition, AttributeDefinition, EntityType, ApprovalStatus
)
from src.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class OntologyMerger:
    """Merges partial ontologies from multiple chunks."""
    
    def __init__(self, similarity_threshold: float = 0.9):
        """Initialize merger with similarity threshold."""
        self.similarity_threshold = similarity_threshold
        self.logger = logging.getLogger(__name__)
    
    def merge_schemas(
        self,
        base_schema: Dict[str, Any],
        new_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge new schema into base schema."""
        self.logger.info("Merging schemas")
        
        merged = {
            'entities': list(base_schema.get('entities', [])),
            'relationships': list(base_schema.get('relationships', []))
        }
        
        # Merge entities
        base_entity_names = {e['name']: i for i, e in enumerate(merged['entities'])}
        
        for new_entity in new_schema.get('entities', []):
            entity_name = new_entity['name']
            
            if entity_name in base_entity_names:
                # Entity exists - merge attributes
                idx = base_entity_names[entity_name]
                merged['entities'][idx] = self._merge_entities(
                    merged['entities'][idx],
                    new_entity
                )
                self.logger.debug(f"Merged entity: {entity_name}")
            else:
                # New entity - add it
                merged['entities'].append(new_entity)
                base_entity_names[entity_name] = len(merged['entities']) - 1
                self.logger.debug(f"Added new entity: {entity_name}")
        
        # Merge relationships
        base_relationships = {
            (r['name'], r['source_entity'], r['target_entity']): r
            for r in merged['relationships']
        }
        
        for new_rel in new_schema.get('relationships', []):
            rel_key = (new_rel['name'], new_rel['source_entity'], new_rel['target_entity'])
            
            if rel_key not in base_relationships:
                # New relationship - add it
                merged['relationships'].append(new_rel)
                self.logger.debug(f"Added new relationship: {new_rel['name']}")
            else:
                # Relationship exists - merge properties if needed
                existing_rel = base_relationships[rel_key]
                merged_rel = self._merge_relationships(existing_rel, new_rel)
                # Update in list
                for i, r in enumerate(merged['relationships']):
                    if (r['name'], r['source_entity'], r['target_entity']) == rel_key:
                        merged['relationships'][i] = merged_rel
                        break
        
        self.logger.info(
            f"Merge complete: {len(merged['entities'])} entities, "
            f"{len(merged['relationships'])} relationships"
        )
        
        return merged

    def _merge_entities(
        self,
        base_entity: Dict[str, Any],
        new_entity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two entity definitions."""
        merged = dict(base_entity)
        
        # Merge attributes
        base_attr_names = {a['name'] for a in merged.get('attributes', [])}
        for new_attr in new_entity.get('attributes', []):
            if new_attr['name'] not in base_attr_names:
                merged.setdefault('attributes', []).append(new_attr)
        
        # Merge parent entities
        base_parents = set(merged.get('parent_entities', []))
        for parent in new_entity.get('parent_entities', []):
            if parent not in base_parents:
                merged.setdefault('parent_entities', []).append(parent)
        
        # Update description if new one is more detailed
        if len(new_entity.get('description', '')) > len(merged.get('description', '')):
            merged['description'] = new_entity['description']
        
        return merged
    
    def _merge_relationships(
        self,
        base_rel: Dict[str, Any],
        new_rel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two relationship definitions."""
        merged = dict(base_rel)
        
        # Merge properties
        base_prop_names = {p['name'] for p in merged.get('properties', [])}
        for new_prop in new_rel.get('properties', []):
            if new_prop['name'] not in base_prop_names:
                merged.setdefault('properties', []).append(new_prop)
        
        # Update description if new one is more detailed
        if len(new_rel.get('description', '')) > len(merged.get('description', '')):
            merged['description'] = new_rel['description']
        
        return merged


class IncrementalOntologyGenerator:
    """Orchestrates incremental ontology generation across chunks."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize generator with LLM service."""
        self.llm_service = llm_service or LLMService()
        self.merger = OntologyMerger()
        self.logger = logging.getLogger(__name__)
    
    def generate_from_chunks(
        self,
        chunks: List[TranscriptChunk],
        transcript_id: str,
        user_id: str
    ) -> OntologySchema:
        """Generate ontology from multiple chunks incrementally."""
        self.logger.info(
            f"Starting incremental ontology generation for {len(chunks)} chunks",
            extra={'transcript_id': transcript_id}
        )
        
        merged_schema = {'entities': [], 'relationships': []}
        previous_context = None
        
        for i, chunk in enumerate(chunks):
            self.logger.info(
                f"Processing chunk {i+1}/{len(chunks)}",
                extra={
                    'chunk_id': chunk.metadata.chunk_id,
                    'word_count': chunk.metadata.word_count
                }
            )
            
            # Generate ontology for this chunk
            chunk_schema = self.llm_service.generate_ontology(
                chunk_content=chunk.content,
                previous_context=previous_context
            )
            
            # Merge with accumulated schema
            merged_schema = self.merger.merge_schemas(merged_schema, chunk_schema)
            
            # Update context for next chunk
            previous_context = {
                'entity_names': [e['name'] for e in merged_schema['entities']],
                'relationship_names': [r['name'] for r in merged_schema['relationships']]
            }
            
            self.logger.info(
                f"Chunk {i+1} processed. Total: {len(merged_schema['entities'])} entities, "
                f"{len(merged_schema['relationships'])} relationships"
            )
        
        # Convert to OntologySchema domain model
        ontology_schema = self._convert_to_domain_model(
            merged_schema,
            transcript_id,
            user_id
        )
        
        self.logger.info(
            "Incremental generation complete",
            extra={
                'total_entities': len(ontology_schema.entities),
                'total_relationships': len(ontology_schema.relationships)
            }
        )
        
        return ontology_schema

    def _convert_to_domain_model(
        self,
        schema_dict: Dict[str, Any],
        transcript_id: str,
        user_id: str
    ) -> OntologySchema:
        """Convert dictionary schema to domain model."""
        # Convert entities
        entities = []
        for entity_dict in schema_dict.get('entities', []):
            attributes = [
                AttributeDefinition(
                    name=attr['name'],
                    data_type=attr.get('data_type', 'string'),
                    required=attr.get('required', False),
                    default_value=attr.get('default_value'),
                    constraints=attr.get('constraints', {}),
                    description=attr.get('description')
                )
                for attr in entity_dict.get('attributes', [])
            ]
            
            # Validate and convert entity type
            entity_type_str = entity_dict.get('type', 'concept').lower()
            try:
                entity_type = EntityType(entity_type_str)
            except ValueError:
                # Fallback to concept for invalid types
                self.logger.warning(f"Invalid entity type '{entity_type_str}' for entity '{entity_dict['name']}', using 'concept'")
                entity_type = EntityType.CONCEPT
            
            entity = EntityDefinition(
                name=entity_dict['name'],
                entity_type=entity_type,
                attributes=attributes,
                parent_entities=entity_dict.get('parent_entities', []),
                description=entity_dict.get('description'),
                constraints=entity_dict.get('constraints', {}),
                metadata=entity_dict.get('metadata', {})
            )
            entities.append(entity)
        
        # Convert relationships
        relationships = []
        for rel_dict in schema_dict.get('relationships', []):
            properties = [
                AttributeDefinition(
                    name=prop['name'],
                    data_type=prop.get('data_type', 'string'),
                    required=prop.get('required', False),
                    default_value=prop.get('default_value'),
                    constraints=prop.get('constraints', {}),
                    description=prop.get('description')
                )
                for prop in rel_dict.get('properties', [])
            ]
            
            relationship = RelationshipDefinition(
                name=rel_dict['name'],
                source_entity=rel_dict['source_entity'],
                target_entity=rel_dict['target_entity'],
                cardinality=rel_dict.get('cardinality', 'many-to-many'),
                properties=properties,
                is_symmetric=rel_dict.get('is_symmetric', False),
                inverse_relationship=rel_dict.get('inverse_relationship'),
                description=rel_dict.get('description'),
                constraints=rel_dict.get('constraints', {}),
                metadata=rel_dict.get('metadata', {})
            )
            relationships.append(relationship)
        
        # Create schema
        schema = OntologySchema(
            id=f"schema_{transcript_id}",
            transcript_id=transcript_id,
            entities=entities,
            relationships=relationships,
            version=1,
            status=ApprovalStatus.PENDING,
            user_id=user_id,
            feedback_count=0
        )
        
        return schema
    
    def generate_from_single_chunk(
        self,
        chunk: TranscriptChunk,
        transcript_id: str,
        user_id: str
    ) -> OntologySchema:
        """Generate ontology from a single chunk (for small transcripts)."""
        self.logger.info("Generating ontology from single chunk")
        
        chunk_schema = self.llm_service.generate_ontology(
            chunk_content=chunk.content,
            previous_context=None
        )
        
        return self._convert_to_domain_model(chunk_schema, transcript_id, user_id)
