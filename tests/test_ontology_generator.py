"""Tests for ontology generator."""
import pytest
from unittest.mock import Mock, patch
from src.services.ontology_generator import OntologyMerger, IncrementalOntologyGenerator
from src.domain.models import TranscriptChunk, ChunkMetadata, Transcript


class TestOntologyMerger:
    """Tests for OntologyMerger."""
    
    def test_merge_new_entity(self):
        """Test merging adds new entity."""
        merger = OntologyMerger()
        
        base_schema = {
            'entities': [
                {'name': 'Person', 'type': 'concept', 'attributes': []}
            ],
            'relationships': []
        }
        
        new_schema = {
            'entities': [
                {'name': 'Company', 'type': 'concept', 'attributes': []}
            ],
            'relationships': []
        }
        
        merged = merger.merge_schemas(base_schema, new_schema)
        
        assert len(merged['entities']) == 2
        entity_names = {e['name'] for e in merged['entities']}
        assert 'Person' in entity_names
        assert 'Company' in entity_names
    
    def test_merge_existing_entity_attributes(self):
        """Test merging adds attributes to existing entity."""
        merger = OntologyMerger()
        
        base_schema = {
            'entities': [
                {
                    'name': 'Person',
                    'type': 'concept',
                    'attributes': [
                        {'name': 'name', 'data_type': 'string'}
                    ]
                }
            ],
            'relationships': []
        }
        
        new_schema = {
            'entities': [
                {
                    'name': 'Person',
                    'type': 'concept',
                    'attributes': [
                        {'name': 'age', 'data_type': 'integer'}
                    ]
                }
            ],
            'relationships': []
        }
        
        merged = merger.merge_schemas(base_schema, new_schema)
        
        assert len(merged['entities']) == 1
        person = merged['entities'][0]
        assert len(person['attributes']) == 2
        attr_names = {a['name'] for a in person['attributes']}
        assert 'name' in attr_names
        assert 'age' in attr_names
    
    def test_merge_relationships(self):
        """Test merging adds new relationships."""
        merger = OntologyMerger()
        
        base_schema = {
            'entities': [],
            'relationships': [
                {
                    'name': 'KNOWS',
                    'source_entity': 'Person',
                    'target_entity': 'Person',
                    'cardinality': 'many-to-many'
                }
            ]
        }
        
        new_schema = {
            'entities': [],
            'relationships': [
                {
                    'name': 'WORKS_AT',
                    'source_entity': 'Person',
                    'target_entity': 'Company',
                    'cardinality': 'many-to-one'
                }
            ]
        }
        
        merged = merger.merge_schemas(base_schema, new_schema)
        
        assert len(merged['relationships']) == 2
        rel_names = {r['name'] for r in merged['relationships']}
        assert 'KNOWS' in rel_names
        assert 'WORKS_AT' in rel_names
    
    def test_merge_duplicate_relationship(self):
        """Test merging doesn't duplicate existing relationships."""
        merger = OntologyMerger()
        
        base_schema = {
            'entities': [],
            'relationships': [
                {
                    'name': 'KNOWS',
                    'source_entity': 'Person',
                    'target_entity': 'Person',
                    'cardinality': 'many-to-many',
                    'properties': []
                }
            ]
        }
        
        new_schema = {
            'entities': [],
            'relationships': [
                {
                    'name': 'KNOWS',
                    'source_entity': 'Person',
                    'target_entity': 'Person',
                    'cardinality': 'many-to-many',
                    'properties': []
                }
            ]
        }
        
        merged = merger.merge_schemas(base_schema, new_schema)
        
        # Should not duplicate
        assert len(merged['relationships']) == 1


class TestIncrementalOntologyGenerator:
    """Tests for IncrementalOntologyGenerator."""
    
    def test_generate_from_single_chunk(self):
        """Test generation from single chunk."""
        # Mock LLM service
        mock_llm = Mock()
        mock_llm.generate_ontology.return_value = {
            'entities': [
                {
                    'name': 'Person',
                    'type': 'concept',
                    'attributes': [
                        {'name': 'name', 'data_type': 'string', 'required': True}
                    ],
                    'parent_entities': [],
                    'description': 'A person'
                }
            ],
            'relationships': []
        }
        
        generator = IncrementalOntologyGenerator(llm_service=mock_llm)
        
        # Create chunk
        chunk = TranscriptChunk(
            transcript_id='transcript_1',
            content='John is a person.',
            metadata=ChunkMetadata(
                chunk_id='chunk_0',
                position=0,
                total_chunks=1,
                word_count=4,
                overlap_start=0,
                overlap_end=0,
                start_char=0,
                end_char=17
            )
        )
        
        schema = generator.generate_from_single_chunk(chunk, 'transcript_1', 'user_1')
        
        assert schema.transcript_id == 'transcript_1'
        assert schema.user_id == 'user_1'
        assert len(schema.entities) == 1
        assert schema.entities[0].name == 'Person'
        mock_llm.generate_ontology.assert_called_once()
    
    def test_generate_from_multiple_chunks(self):
        """Test incremental generation from multiple chunks."""
        # Mock LLM service
        mock_llm = Mock()
        mock_llm.generate_ontology.side_effect = [
            {
                'entities': [
                    {
                        'name': 'Person',
                        'type': 'concept',
                        'attributes': [{'name': 'name', 'data_type': 'string'}],
                        'parent_entities': []
                    }
                ],
                'relationships': []
            },
            {
                'entities': [
                    {
                        'name': 'Company',
                        'type': 'concept',
                        'attributes': [{'name': 'name', 'data_type': 'string'}],
                        'parent_entities': []
                    }
                ],
                'relationships': [
                    {
                        'name': 'WORKS_AT',
                        'source_entity': 'Person',
                        'target_entity': 'Company',
                        'cardinality': 'many-to-one'
                    }
                ]
            }
        ]
        
        generator = IncrementalOntologyGenerator(llm_service=mock_llm)
        
        # Create chunks
        chunks = [
            TranscriptChunk(
                transcript_id='transcript_1',
                content='John is a person.',
                metadata=ChunkMetadata(
                    chunk_id='chunk_0',
                    position=0,
                    total_chunks=2,
                    word_count=4,
                    overlap_start=0,
                    overlap_end=1,
                    start_char=0,
                    end_char=17
                )
            ),
            TranscriptChunk(
                transcript_id='transcript_1',
                content='John works at Apple.',
                metadata=ChunkMetadata(
                    chunk_id='chunk_1',
                    position=1,
                    total_chunks=2,
                    word_count=4,
                    overlap_start=1,
                    overlap_end=0,
                    start_char=16,
                    end_char=36
                )
            )
        ]
        
        schema = generator.generate_from_chunks(chunks, 'transcript_1', 'user_1')
        
        assert len(schema.entities) == 2
        assert len(schema.relationships) == 1
        
        entity_names = {e.name for e in schema.entities}
        assert 'Person' in entity_names
        assert 'Company' in entity_names
        
        assert schema.relationships[0].name == 'WORKS_AT'
        
        # Verify LLM was called twice with context
        assert mock_llm.generate_ontology.call_count == 2
        
        # Second call should have context
        second_call_kwargs = mock_llm.generate_ontology.call_args_list[1][1]
        assert second_call_kwargs['previous_context'] is not None
        assert 'Person' in second_call_kwargs['previous_context']['entity_names']
    
    def test_convert_to_domain_model(self):
        """Test conversion from dict to domain model."""
        generator = IncrementalOntologyGenerator(llm_service=Mock())
        
        schema_dict = {
            'entities': [
                {
                    'name': 'Person',
                    'type': 'concept',
                    'attributes': [
                        {
                            'name': 'name',
                            'data_type': 'string',
                            'required': True
                        }
                    ],
                    'parent_entities': [],
                    'description': 'A person'
                }
            ],
            'relationships': [
                {
                    'name': 'KNOWS',
                    'source_entity': 'Person',
                    'target_entity': 'Person',
                    'cardinality': 'many-to-many',
                    'properties': []
                }
            ]
        }
        
        schema = generator._convert_to_domain_model(schema_dict, 'transcript_1', 'user_1')
        
        assert schema.id == 'schema_transcript_1'
        assert schema.transcript_id == 'transcript_1'
        assert schema.user_id == 'user_1'
        assert len(schema.entities) == 1
        assert len(schema.relationships) == 1
        
        # Validate entity
        entity = schema.entities[0]
        assert entity.name == 'Person'
        assert len(entity.attributes) == 1
        assert entity.attributes[0].name == 'name'
        assert entity.attributes[0].required is True
        
        # Validate relationship
        rel = schema.relationships[0]
        assert rel.name == 'KNOWS'
        assert rel.source_entity == 'Person'
        assert rel.target_entity == 'Person'
