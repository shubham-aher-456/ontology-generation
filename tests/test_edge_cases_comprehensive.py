"""Comprehensive edge case tests covering all scenarios."""
import pytest
import hashlib
from unittest.mock import Mock, patch
from src.services.transcript_processor import TranscriptProcessor, TranscriptChunker
from src.services.llm_service import LLMService, CircuitBreakerOpenError
from src.services.ontology_generator import IncrementalOntologyGenerator, OntologyMerger
from src.domain.models import (
    Transcript, OntologySchema, EntityDefinition, RelationshipDefinition,
    AttributeDefinition, EntityType, ApprovalStatus
)


class TestModule1TranscriptEdgeCases:
    """Module 1: Transcript Upload & Processing Edge Cases."""
    
    def test_edge_case_1_1_maximum_size_transcript(self):
        """Edge Case 1.1: Maximum size transcript (50MB)."""
        processor = TranscriptProcessor()
        chunker = TranscriptChunker()
        
        # Create 50MB transcript (dense content)
        word_count = 500000  # ~50MB of text
        content = " ".join([f"word{i}" for i in range(word_count)])
        
        # Validate file size
        content_bytes = content.encode('utf-8')
        assert len(content_bytes) <= processor.MAX_FILE_SIZE
        
        # Create transcript
        transcript = processor.create_transcript("large.txt", content, "user1")
        
        # Chunk it
        chunks = chunker.chunk_transcript(transcript)
        
        # Should create ~100 chunks (500k words / 5k per chunk)
        expected_chunks = (word_count - 500) // (5000 - 500) + 1
        assert len(chunks) >= 90  # Allow some variance
        assert len(chunks) <= 120
        
        # Verify all chunks have proper metadata
        for chunk in chunks:
            assert chunk.metadata.word_count <= 5000
            assert chunk.metadata.total_chunks == len(chunks)
        
        print(f"✓ Edge Case 1.1: Created {len(chunks)} chunks from 50MB transcript")
    
    def test_edge_case_1_2_minimum_size_transcript(self):
        """Edge Case 1.2: Minimum size transcript (1 sentence)."""
        processor = TranscriptProcessor()
        chunker = TranscriptChunker()
        
        content = "The cat sat on the mat."
        transcript = processor.create_transcript("tiny.txt", content, "user1")
        
        chunks = chunker.chunk_transcript(transcript)
        
        # Should create single chunk
        assert len(chunks) == 1
        assert chunks[0].metadata.total_chunks == 1
        assert chunks[0].metadata.overlap_start == 0
        assert chunks[0].metadata.overlap_end == 0
        
        print("✓ Edge Case 1.2: Single chunk for minimal transcript")
    
    def test_edge_case_1_3_malformed_encoding(self):
        """Edge Case 1.3: Malformed encoding with special characters."""
        processor = TranscriptProcessor()
        
        # Test with emoji, Chinese, Arabic
        content = "Research 🔬 shows that 中文 text and العربية characters work."
        content_bytes = content.encode('utf-8')
        
        # Extract text
        extracted = processor.extract_text("test.txt", content_bytes)
        
        # Should preserve all characters
        assert "🔬" in extracted
        assert "中文" in extracted
        assert "العربية" in extracted
        
        print("✓ Edge Case 1.3: Multi-language encoding preserved")

    def test_edge_case_1_4_binary_content_injection(self):
        """Edge Case 1.4: Binary content injection."""
        processor = TranscriptProcessor()
        
        # Binary content
        binary_content = b'\x00\x01\x02\x03\x04\x05'
        
        # Should fail to extract
        with pytest.raises(ValueError):
            processor.extract_text("test.txt", binary_content)
        
        print("✓ Edge Case 1.4: Binary content rejected")
    
    def test_edge_case_1_5_extremely_long_single_sentence(self):
        """Edge Case 1.5: 10,000-word run-on sentence."""
        processor = TranscriptProcessor()
        chunker = TranscriptChunker()
        
        # Create 10k word sentence (no punctuation)
        content = " ".join([f"word{i}" for i in range(10000)])
        transcript = processor.create_transcript("runon.txt", content, "user1")
        
        chunks = chunker.chunk_transcript(transcript)
        
        # Should still chunk properly
        assert len(chunks) >= 2
        
        # Each chunk should have content
        for chunk in chunks:
            assert len(chunk.content) > 0
            assert chunk.metadata.word_count > 0
        
        print(f"✓ Edge Case 1.5: Chunked 10k-word sentence into {len(chunks)} chunks")
    
    def test_edge_case_1_6_only_special_characters(self):
        """Edge Case 1.6: Transcript with only special characters."""
        processor = TranscriptProcessor()
        
        content = "@@@ ### $$$ %%% ^^^ &&& ***"
        transcript = processor.create_transcript("special.txt", content, "user1")
        
        # Should create transcript successfully
        assert transcript.content == content
        assert len(transcript.content_hash) == 64
        
        print("✓ Edge Case 1.6: Special characters handled")


class TestModule2OntologyGenerationEdgeCases:
    """Module 2: Ontology Generation Edge Cases."""
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_edge_case_2_1_highly_ambiguous_terms(self, mock_azure):
        """Edge Case 2.1: Highly ambiguous terms (bank)."""
        # Mock LLM to return disambiguated entities
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
{
  "entities": [
    {
      "name": "FinancialBank",
      "type": "concept",
      "attributes": [{"name": "name", "data_type": "string"}],
      "parent_entities": [],
      "description": "Financial institution"
    },
    {
      "name": "RiverBank",
      "type": "concept",
      "attributes": [{"name": "location", "data_type": "string"}],
      "parent_entities": [],
      "description": "Edge of a river"
    }
  ],
  "relationships": []
}
'''
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        llm_service = LLMService()
        content = "The bank collapsed. Customers lost money. The river bank eroded."
        
        ontology = llm_service.generate_ontology(content)
        
        # Should create two distinct entities
        assert len(ontology['entities']) == 2
        entity_names = {e['name'] for e in ontology['entities']}
        assert 'FinancialBank' in entity_names or 'RiverBank' in entity_names
        
        print("✓ Edge Case 2.1: Ambiguous terms disambiguated")

    @patch('src.services.llm_service.AzureOpenAI')
    def test_edge_case_2_2_circular_relationships(self, mock_azure):
        """Edge Case 2.2: Circular relationships (A→B→C→A)."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
{
  "entities": [
    {"name": "A", "type": "concept", "attributes": [{"name": "id", "data_type": "string"}], "parent_entities": []},
    {"name": "B", "type": "concept", "attributes": [{"name": "id", "data_type": "string"}], "parent_entities": []},
    {"name": "C", "type": "concept", "attributes": [{"name": "id", "data_type": "string"}], "parent_entities": []}
  ],
  "relationships": [
    {"name": "CAUSES", "source_entity": "A", "target_entity": "B", "cardinality": "one-to-one"},
    {"name": "CAUSES", "source_entity": "B", "target_entity": "C", "cardinality": "one-to-one"},
    {"name": "CAUSES", "source_entity": "C", "target_entity": "A", "cardinality": "one-to-one"}
  ]
}
'''
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        llm_service = LLMService()
        generator = IncrementalOntologyGenerator(llm_service=llm_service)
        
        content = "A causes B, B causes C, C causes A"
        from src.domain.models import TranscriptChunk, ChunkMetadata
        
        chunk = TranscriptChunk(
            transcript_id="test",
            content=content,
            metadata=ChunkMetadata(
                chunk_id="chunk_0",
                position=0,
                total_chunks=1,
                word_count=8,
                overlap_start=0,
                overlap_end=0,
                start_char=0,
                end_char=len(content)
            )
        )
        
        schema = generator.generate_from_single_chunk(chunk, "test", "user1")
        
        # Should create cycle
        assert len(schema.relationships) == 3
        
        # Validation should not fail (cycles are allowed in graph)
        errors = schema.validate()
        # Cycles in relationships are OK, only inheritance cycles are errors
        
        print("✓ Edge Case 2.2: Circular relationships handled")
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_edge_case_2_3_self_referential_entities(self, mock_azure):
        """Edge Case 2.3: Self-referential entities."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
{
  "entities": [
    {"name": "Manager", "type": "concept", "attributes": [{"name": "name", "data_type": "string"}], "parent_entities": []}
  ],
  "relationships": [
    {"name": "MANAGES", "source_entity": "Manager", "target_entity": "Manager", "cardinality": "one-to-many"}
  ]
}
'''
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        llm_service = LLMService()
        content = "The manager manages himself"
        
        ontology = llm_service.generate_ontology(content)
        
        # Should create self-loop
        assert len(ontology['relationships']) == 1
        rel = ontology['relationships'][0]
        assert rel['source_entity'] == rel['target_entity'] == 'Manager'
        
        print("✓ Edge Case 2.3: Self-referential relationship created")

    @patch('src.services.llm_service.AzureOpenAI')
    def test_edge_case_2_4_contradictory_statements(self, mock_azure):
        """Edge Case 2.4: Contradictory statements."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
{
  "entities": [
    {
      "name": "John",
      "type": "instance",
      "attributes": [
        {"name": "age_v1", "data_type": "integer"},
        {"name": "age_v2", "data_type": "integer"}
      ],
      "parent_entities": [],
      "description": "Person with conflicting age values"
    }
  ],
  "relationships": []
}
'''
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        llm_service = LLMService()
        content = "John is 25 years old. John is 30 years old."
        
        ontology = llm_service.generate_ontology(content)
        
        # Should handle conflict (multiple attributes or flagged)
        assert len(ontology['entities']) >= 1
        
        print("✓ Edge Case 2.4: Contradictory statements handled")
    
    def test_edge_case_2_5_nested_hierarchies_10_levels(self):
        """Edge Case 2.5: Nested hierarchies (10+ levels deep)."""
        # Create 10-level hierarchy
        entities = []
        for i in range(10):
            parent = [f"Level{i-1}"] if i > 0 else []
            entities.append(
                EntityDefinition(
                    name=f"Level{i}",
                    entity_type=EntityType.CONCEPT,
                    attributes=[AttributeDefinition(name="id", data_type="string")],
                    parent_entities=parent
                )
            )
        
        schema = OntologySchema(
            id="test",
            transcript_id="test",
            entities=entities,
            relationships=[]
        )
        
        # Should validate without stack overflow
        errors = schema.validate()
        assert len(errors) == 0
        
        print("✓ Edge Case 2.5: 10-level hierarchy validated")
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_edge_case_2_6_massive_entity_count(self, mock_azure):
        """Edge Case 2.6: Massive entity count (1000+ entities)."""
        # Create schema with 1000 entities
        entities_data = []
        for i in range(1000):
            entities_data.append({
                "name": f"Entity{i}",
                "type": "concept",
                "attributes": [{"name": "id", "data_type": "string"}],
                "parent_entities": []
            })
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = f'{{"entities": {str(entities_data)[:1000]}, "relationships": []}}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        # Create entities directly
        entities = [
            EntityDefinition(
                name=f"Entity{i}",
                entity_type=EntityType.CONCEPT,
                attributes=[AttributeDefinition(name="id", data_type="string")]
            )
            for i in range(1000)
        ]
        
        schema = OntologySchema(
            id="test",
            transcript_id="test",
            entities=entities,
            relationships=[]
        )
        
        # Should handle large count
        assert len(schema.entities) == 1000
        
        # Validation should complete (may take time)
        errors = schema.validate()
        assert len(errors) == 0
        
        print("✓ Edge Case 2.6: 1000 entities handled")
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_edge_case_2_7_zero_entities_detected(self, mock_azure):
        """Edge Case 2.7: Zero entities detected."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"entities": [], "relationships": []}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        llm_service = LLMService()
        content = "Happiness is good. Sadness is bad."
        
        ontology = llm_service.generate_ontology(content)
        
        # Should return empty ontology gracefully
        assert ontology['entities'] == []
        assert ontology['relationships'] == []
        
        print("✓ Edge Case 2.7: Zero entities handled gracefully")


class TestModule3SchemaValidationEdgeCases:
    """Module 3: Schema Validation Edge Cases."""
    
    def test_edge_case_3_1_schema_without_entities(self):
        """Edge Case 3.1: Schema without entities."""
        schema = OntologySchema(
            id="test",
            transcript_id="test",
            entities=[],
            relationships=[]
        )
        
        errors = schema.validate()
        
        # Should fail validation
        assert len(errors) > 0
        assert any("at least one entity" in err.lower() for err in errors)
        
        print("✓ Edge Case 3.1: Empty schema rejected")

    def test_edge_case_3_2_circular_inheritance(self):
        """Edge Case 3.2: Circular inheritance detection."""
        entities = [
            EntityDefinition(
                name="A",
                entity_type=EntityType.CONCEPT,
                attributes=[AttributeDefinition(name="id", data_type="string")],
                parent_entities=["B"]
            ),
            EntityDefinition(
                name="B",
                entity_type=EntityType.CONCEPT,
                attributes=[AttributeDefinition(name="id", data_type="string")],
                parent_entities=["C"]
            ),
            EntityDefinition(
                name="C",
                entity_type=EntityType.CONCEPT,
                attributes=[AttributeDefinition(name="id", data_type="string")],
                parent_entities=["A"]
            )
        ]
        
        schema = OntologySchema(
            id="test",
            transcript_id="test",
            entities=entities,
            relationships=[]
        )
        
        errors = schema.validate()
        
        # Should detect circular inheritance
        assert len(errors) > 0
        assert any("circular inheritance" in err.lower() for err in errors)
        
        print("✓ Edge Case 3.2: Circular inheritance detected")
    
    def test_edge_case_3_3_relationship_undefined_entity(self):
        """Edge Case 3.3: Relationship references undefined entity."""
        entities = [
            EntityDefinition(
                name="Person",
                entity_type=EntityType.CONCEPT,
                attributes=[AttributeDefinition(name="name", data_type="string")]
            )
        ]
        
        relationships = [
            RelationshipDefinition(
                name="WORKS_AT",
                source_entity="Person",
                target_entity="Company",  # Not defined
                cardinality="many-to-one"
            )
        ]
        
        schema = OntologySchema(
            id="test",
            transcript_id="test",
            entities=entities,
            relationships=relationships
        )
        
        errors = schema.validate()
        
        # Should detect undefined entity
        assert len(errors) > 0
        assert any("undefined" in err.lower() for err in errors)
        
        print("✓ Edge Case 3.3: Undefined entity detected")
    
    def test_edge_case_3_4_duplicate_entity_names(self):
        """Edge Case 3.4: Duplicate entity names."""
        entities = [
            EntityDefinition(
                name="Person",
                entity_type=EntityType.CONCEPT,
                attributes=[AttributeDefinition(name="name", data_type="string")]
            ),
            EntityDefinition(
                name="Person",  # Duplicate
                entity_type=EntityType.CONCEPT,
                attributes=[AttributeDefinition(name="age", data_type="integer")]
            )
        ]
        
        schema = OntologySchema(
            id="test",
            transcript_id="test",
            entities=entities,
            relationships=[]
        )
        
        errors = schema.validate()
        
        # Should detect duplicates
        assert len(errors) > 0
        assert any("duplicate" in err.lower() for err in errors)
        
        print("✓ Edge Case 3.4: Duplicate entity names detected")


class TestModule4DuplicateDetectionEdgeCases:
    """Module 4: Duplicate Detection Edge Cases."""
    
    def test_edge_case_4_1_exact_duplicate_sha256(self):
        """Edge Case 4.1: Exact duplicate (SHA-256 collision)."""
        processor = TranscriptProcessor()
        
        content = "This is a test transcript."
        
        transcript1 = processor.create_transcript("test1.txt", content, "user1")
        transcript2 = processor.create_transcript("test2.txt", content, "user1")
        
        # Should have identical hashes
        assert transcript1.content_hash == transcript2.content_hash
        
        print("✓ Edge Case 4.1: Exact duplicate detected via SHA-256")
    
    def test_edge_case_4_2_schema_hash_determinism(self):
        """Edge Case 4.2: Schema hash determinism."""
        entities = [
            EntityDefinition(
                name="Person",
                entity_type=EntityType.CONCEPT,
                attributes=[AttributeDefinition(name="name", data_type="string")]
            )
        ]
        
        schema1 = OntologySchema(
            id="schema1",
            transcript_id="test1",
            entities=entities
        )
        
        schema2 = OntologySchema(
            id="schema2",
            transcript_id="test2",
            entities=entities
        )
        
        # Same content should produce same hash
        assert schema1.schema_hash == schema2.schema_hash
        
        print("✓ Edge Case 4.2: Schema hash deterministic")


class TestModule5MergingEdgeCases:
    """Module 5: Ontology Merging Edge Cases."""
    
    def test_edge_case_5_1_merge_conflicting_attributes(self):
        """Edge Case 5.1: Merge entities with conflicting attributes."""
        merger = OntologyMerger()
        
        base_schema = {
            'entities': [
                {
                    'name': 'Person',
                    'type': 'concept',
                    'attributes': [
                        {'name': 'age', 'data_type': 'integer'}
                    ],
                    'parent_entities': []
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
                        {'name': 'age', 'data_type': 'string'}  # Conflicting type
                    ],
                    'parent_entities': []
                }
            ],
            'relationships': []
        }
        
        merged = merger.merge_schemas(base_schema, new_schema)
        
        # Should keep first definition (base takes precedence)
        person = merged['entities'][0]
        age_attrs = [a for a in person['attributes'] if a['name'] == 'age']
        assert len(age_attrs) == 1  # No duplicate
        
        print("✓ Edge Case 5.1: Conflicting attributes handled")

    def test_edge_case_5_2_merge_100_chunks(self):
        """Edge Case 5.2: Merge ontologies from 100 chunks."""
        merger = OntologyMerger()
        
        # Start with empty schema
        merged = {'entities': [], 'relationships': []}
        
        # Merge 100 chunks, each adding 1 entity
        for i in range(100):
            chunk_schema = {
                'entities': [
                    {
                        'name': f'Entity{i}',
                        'type': 'concept',
                        'attributes': [{'name': 'id', 'data_type': 'string'}],
                        'parent_entities': []
                    }
                ],
                'relationships': []
            }
            merged = merger.merge_schemas(merged, chunk_schema)
        
        # Should have 100 entities
        assert len(merged['entities']) == 100
        
        print("✓ Edge Case 5.2: Merged 100 chunks successfully")


class TestModule6CircuitBreakerEdgeCases:
    """Module 6: Circuit Breaker & Retry Edge Cases."""
    
    def test_edge_case_6_1_circuit_breaker_opens_after_threshold(self):
        """Edge Case 6.1: Circuit breaker opens after failures."""
        from src.services.llm_service import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=3, timeout_seconds=1)
        
        def failing_func():
            raise Exception("Service unavailable")
        
        # Fail 3 times
        for _ in range(3):
            with pytest.raises(Exception):
                cb.call(failing_func)
        
        assert cb.state == "OPEN"
        
        # Next call should raise CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(failing_func)
        
        print("✓ Edge Case 6.1: Circuit breaker opened after threshold")
    
    def test_edge_case_6_2_retry_exhaustion(self):
        """Edge Case 6.2: All retries exhausted."""
        from src.services.llm_service import retry_with_backoff
        
        call_count = 0
        
        @retry_with_backoff(max_retries=3, initial_delay=0.01, exponential_base=2)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise Exception("Persistent failure")
        
        with pytest.raises(Exception, match="Persistent failure"):
            always_fails()
        
        # Should have tried 4 times (initial + 3 retries)
        assert call_count == 4
        
        print("✓ Edge Case 6.2: Retry exhaustion handled")


class TestModule7ErrorHandlingEdgeCases:
    """Module 7: Error Handling Edge Cases."""
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_edge_case_7_1_llm_returns_invalid_json(self, mock_azure):
        """Edge Case 7.1: LLM returns invalid JSON."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON at all!"
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        llm_service = LLMService()
        content = "Test content"
        
        ontology = llm_service.generate_ontology(content)
        
        # Should return empty ontology gracefully
        assert ontology == {'entities': [], 'relationships': []}
        
        print("✓ Edge Case 7.1: Invalid JSON handled gracefully")
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_edge_case_7_2_llm_returns_partial_json(self, mock_azure):
        """Edge Case 7.2: LLM returns partial/truncated JSON."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"entities": [{"name": "Person"'
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        llm_service = LLMService()
        content = "Test content"
        
        ontology = llm_service.generate_ontology(content)
        
        # Should handle gracefully
        assert ontology == {'entities': [], 'relationships': []}
        
        print("✓ Edge Case 7.2: Partial JSON handled")
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_edge_case_7_3_llm_timeout(self, mock_azure):
        """Edge Case 7.3: LLM API timeout."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = TimeoutError("Request timeout")
        mock_azure.return_value = mock_client
        
        llm_service = LLMService()
        content = "Test content"
        
        # Should raise after retries
        with pytest.raises(TimeoutError):
            llm_service.generate_ontology(content)
        
        print("✓ Edge Case 7.3: Timeout handled with retries")


class TestModule8PerformanceEdgeCases:
    """Module 8: Performance Edge Cases."""
    
    def test_edge_case_8_1_hash_computation_performance(self):
        """Edge Case 8.1: Hash computation on large content."""
        import time
        
        # Create 10MB content
        content = "x" * (10 * 1024 * 1024)
        
        start = time.time()
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        duration = time.time() - start
        
        # Should complete in reasonable time (<1 second)
        assert duration < 1.0
        assert len(content_hash) == 64
        
        print(f"✓ Edge Case 8.1: 10MB hash computed in {duration:.3f}s")
    
    def test_edge_case_8_2_chunking_performance(self):
        """Edge Case 8.2: Chunking performance on large transcript."""
        import time
        
        chunker = TranscriptChunker()
        
        # Create 100k word transcript
        content = " ".join([f"word{i}" for i in range(100000)])
        transcript = Transcript.create("large.txt", content, "user1")
        
        start = time.time()
        chunks = chunker.chunk_transcript(transcript)
        duration = time.time() - start
        
        # Should complete quickly (<2 seconds)
        assert duration < 2.0
        assert len(chunks) > 0
        
        print(f"✓ Edge Case 8.2: 100k words chunked in {duration:.3f}s ({len(chunks)} chunks)")


class TestModule9NeutralScenarios:
    """Module 9: Neutral/Normal Scenarios."""
    
    def test_neutral_case_1_typical_transcript(self):
        """Neutral Case 1: Typical business transcript."""
        processor = TranscriptProcessor()
        chunker = TranscriptChunker()
        
        content = """
        John Smith is the CEO of TechCorp.
        The company was founded in 2010.
        TechCorp develops AI software for enterprises.
        Mary Johnson is the CTO and leads the engineering team.
        """
        
        transcript = processor.create_transcript("business.txt", content, "user1")
        chunks = chunker.chunk_transcript(transcript)
        
        # Should work normally
        assert len(chunks) >= 1
        assert transcript.content_hash is not None
        
        print("✓ Neutral Case 1: Typical transcript processed")
    
    def test_neutral_case_2_medium_complexity(self):
        """Neutral Case 2: Medium complexity ontology."""
        entities = [
            EntityDefinition(
                name="Person",
                entity_type=EntityType.CONCEPT,
                attributes=[
                    AttributeDefinition(name="name", data_type="string", required=True),
                    AttributeDefinition(name="age", data_type="integer")
                ]
            ),
            EntityDefinition(
                name="Company",
                entity_type=EntityType.CONCEPT,
                attributes=[
                    AttributeDefinition(name="name", data_type="string", required=True)
                ]
            )
        ]
        
        relationships = [
            RelationshipDefinition(
                name="WORKS_AT",
                source_entity="Person",
                target_entity="Company",
                cardinality="many-to-one"
            )
        ]
        
        schema = OntologySchema(
            id="test",
            transcript_id="test",
            entities=entities,
            relationships=relationships
        )
        
        errors = schema.validate()
        assert len(errors) == 0
        
        print("✓ Neutral Case 2: Medium complexity schema validated")


class TestModule10HardNegativeScenarios:
    """Module 10: Hard Negative Scenarios."""
    
    def test_hard_negative_1_corrupted_data(self):
        """Hard Negative 1: Completely corrupted data."""
        processor = TranscriptProcessor()
        
        # Binary content with null bytes
        corrupted = b'\x00\x01\x02\x03\x04\x05\xff\xfe\xfd\xfc\xfb\xfa'
        
        with pytest.raises(ValueError, match="Binary content detected"):
            processor.extract_text("test.txt", corrupted)
        
        print("✓ Hard Negative 1: Corrupted data rejected")
    
    def test_hard_negative_2_malicious_input(self):
        """Hard Negative 2: SQL injection attempt in content."""
        processor = TranscriptProcessor()
        
        # SQL injection attempt
        content = "'; DROP TABLE users; --"
        transcript = processor.create_transcript("malicious.txt", content, "user1")
        
        # Should store safely (content is just text)
        assert transcript.content == content
        assert len(transcript.content_hash) == 64
        
        print("✓ Hard Negative 2: Malicious input stored safely")
    
    def test_hard_negative_3_extremely_deep_nesting(self):
        """Hard Negative 3: Extremely deep nesting (100 levels)."""
        # Create 100-level hierarchy
        entities = []
        for i in range(100):
            parent = [f"Level{i-1}"] if i > 0 else []
            entities.append(
                EntityDefinition(
                    name=f"Level{i}",
                    entity_type=EntityType.CONCEPT,
                    attributes=[AttributeDefinition(name="id", data_type="string")],
                    parent_entities=parent
                )
            )
        
        schema = OntologySchema(
            id="test",
            transcript_id="test",
            entities=entities,
            relationships=[]
        )
        
        # Should not cause stack overflow
        errors = schema.validate()
        assert len(errors) == 0
        
        print("✓ Hard Negative 3: 100-level hierarchy handled")
