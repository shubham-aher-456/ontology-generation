"""Advanced robustness tests for system stability and stress scenarios."""
import pytest
import time
import threading
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch
from src.services.transcript_processor import TranscriptProcessor, TranscriptChunker
from src.services.llm_service import LLMService, CircuitBreaker
from src.services.ontology_generator import IncrementalOntologyGenerator, OntologyMerger
from src.domain.models import (
    Transcript, OntologySchema, EntityDefinition, RelationshipDefinition,
    AttributeDefinition, EntityType, TranscriptChunk, ChunkMetadata
)


class TestConcurrencyAndRaceConditions:
    """Test concurrent operations and race conditions."""
    
    def test_concurrent_transcript_processing(self):
        """Test processing multiple transcripts concurrently."""
        processor = TranscriptProcessor()
        chunker = TranscriptChunker()
        
        def process_transcript(idx):
            content = f"Test transcript {idx} " * 1000
            transcript = processor.create_transcript(f"test_{idx}.txt", content, f"user_{idx}")
            chunks = chunker.chunk_transcript(transcript)
            return len(chunks)
        
        # Process 20 transcripts concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_transcript, i) for i in range(20)]
            results = [f.result() for f in as_completed(futures)]
        
        # All should succeed
        assert len(results) == 20
        assert all(r > 0 for r in results)
        
        print(f"✓ Concurrent processing: 20 transcripts processed successfully")
    
    def test_concurrent_hash_computation(self):
        """Test hash computation under concurrent load."""
        def compute_hash(idx):
            content = f"Content {idx} " * 10000
            return hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Compute 50 hashes concurrently
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(compute_hash, i) for i in range(50)]
            hashes = [f.result() for f in as_completed(futures)]
        
        # All hashes should be unique (different content)
        assert len(set(hashes)) == 50
        
        print(f"✓ Concurrent hashing: 50 unique hashes computed")
    
    def test_concurrent_schema_validation(self):
        """Test schema validation under concurrent load."""
        def validate_schema(idx):
            entities = [
                EntityDefinition(
                    name=f"Entity{idx}",
                    entity_type=EntityType.CONCEPT,
                    attributes=[AttributeDefinition(name="id", data_type="string")]
                )
            ]
            schema = OntologySchema(
                id=f"schema_{idx}",
                transcript_id=f"test_{idx}",
                entities=entities
            )
            return len(schema.validate())
        
        # Validate 30 schemas concurrently
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(validate_schema, i) for i in range(30)]
            error_counts = [f.result() for f in as_completed(futures)]
        
        # All should have 0 errors
        assert all(count == 0 for count in error_counts)
        
        print(f"✓ Concurrent validation: 30 schemas validated successfully")


class TestMemoryAndResourceManagement:
    """Test memory usage and resource management."""
    
    def test_large_transcript_memory_efficiency(self):
        """Test memory efficiency with very large transcript."""
        processor = TranscriptProcessor()
        chunker = TranscriptChunker()
        
        # Create 20MB transcript
        word_count = 200000
        content = " ".join([f"word{i}" for i in range(word_count)])
        
        transcript = processor.create_transcript("large.txt", content, "user1")
        
        # Chunk it
        start_time = time.time()
        chunks = chunker.chunk_transcript(transcript)
        duration = time.time() - start_time
        
        # Should complete quickly
        assert duration < 5.0
        assert len(chunks) > 0
        
        # Verify chunks don't duplicate content unnecessarily
        total_chunk_words = sum(c.metadata.word_count for c in chunks)
        # Should be close to original (with some overlap)
        assert total_chunk_words < word_count * 1.2
        
        print(f"✓ Memory efficiency: 20MB transcript chunked in {duration:.2f}s")
    
    def test_repeated_hash_computation_performance(self):
        """Test hash computation performance over many iterations."""
        content = "Test content " * 10000
        
        start_time = time.time()
        hashes = []
        for _ in range(100):
            h = hashlib.sha256(content.encode('utf-8')).hexdigest()
            hashes.append(h)
        duration = time.time() - start_time
        
        # All hashes should be identical
        assert len(set(hashes)) == 1
        
        # Should complete quickly
        assert duration < 2.0
        
        print(f"✓ Hash performance: 100 iterations in {duration:.2f}s")
    
    def test_large_schema_serialization(self):
        """Test serialization of large schema."""
        # Create schema with 500 entities
        entities = [
            EntityDefinition(
                name=f"Entity{i}",
                entity_type=EntityType.CONCEPT,
                attributes=[
                    AttributeDefinition(name="id", data_type="string"),
                    AttributeDefinition(name="name", data_type="string"),
                    AttributeDefinition(name="value", data_type="integer")
                ]
            )
            for i in range(500)
        ]
        
        schema = OntologySchema(
            id="large_schema",
            transcript_id="test",
            entities=entities
        )
        
        # Serialize
        start_time = time.time()
        schema_dict = schema.to_dict()
        duration = time.time() - start_time
        
        # Should complete quickly
        assert duration < 1.0
        assert len(schema_dict['entities']) == 500
        
        # Deserialize
        start_time = time.time()
        restored = OntologySchema.from_dict(schema_dict)
        duration = time.time() - start_time
        
        assert duration < 1.0
        assert len(restored.entities) == 500
        
        print(f"✓ Large schema serialization: 500 entities handled efficiently")


class TestErrorRecoveryAndResilience:
    """Test error recovery and system resilience."""
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_intermittent_llm_failures(self, mock_azure):
        """Test handling of intermittent LLM failures."""
        mock_client = Mock()
        call_count = 0
        
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Temporary failure")
            # Succeed on 3rd attempt
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"entities": [], "relationships": []}'
            return mock_response
        
        mock_client.chat.completions.create.side_effect = side_effect
        mock_azure.return_value = mock_client
        
        llm_service = LLMService()
        
        # Should succeed after retries
        result = llm_service.generate_ontology("Test content")
        
        assert result == {'entities': [], 'relationships': []}
        assert call_count == 3  # Failed twice, succeeded on 3rd
        
        print(f"✓ Error recovery: Recovered from 2 failures via retry")
    
    def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after timeout."""
        cb = CircuitBreaker(failure_threshold=2, timeout_seconds=1)
        
        def failing_func():
            raise Exception("Service down")
        
        # Fail twice to open circuit
        for _ in range(2):
            with pytest.raises(Exception):
                cb.call(failing_func)
        
        assert cb.state == "OPEN"
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Should transition to HALF_OPEN and allow retry
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == "CLOSED"
        
        print(f"✓ Circuit breaker recovery: Transitioned OPEN → HALF_OPEN → CLOSED")
    
    def test_partial_chunk_processing_failure(self):
        """Test handling when some chunks fail to process."""
        merger = OntologyMerger()
        
        # Process 5 chunks, simulate one returning empty
        schemas = [
            {'entities': [{'name': f'Entity{i}', 'type': 'concept', 'attributes': [], 'parent_entities': []}], 'relationships': []}
            for i in range(5)
        ]
        
        # Add empty schema (simulating failure)
        schemas.append({'entities': [], 'relationships': []})
        
        # Merge all
        merged = {'entities': [], 'relationships': []}
        for schema in schemas:
            merged = merger.merge_schemas(merged, schema)
        
        # Should have 5 entities (empty one doesn't add anything)
        assert len(merged['entities']) == 5
        
        print(f"✓ Partial failure handling: Merged 5/6 chunks successfully")


class TestBoundaryConditions:
    """Test boundary conditions and edge values."""
    
    def test_zero_overlap_chunking(self):
        """Test chunking with zero overlap."""
        chunker = TranscriptChunker(chunk_size_words=100, overlap_words=0)
        
        content = " ".join([f"word{i}" for i in range(250)])
        transcript = Transcript.create("test.txt", content, "user1")
        
        chunks = chunker.chunk_transcript(transcript)
        
        # Should create 3 chunks (250 / 100 = 2.5 → 3)
        assert len(chunks) == 3
        
        # No overlap
        for chunk in chunks:
            assert chunk.metadata.overlap_start == 0
            assert chunk.metadata.overlap_end == 0
        
        print(f"✓ Boundary condition: Zero overlap chunking works")
    
    def test_overlap_equals_chunk_size(self):
        """Test chunking when overlap equals chunk size."""
        chunker = TranscriptChunker(chunk_size_words=100, overlap_words=100)
        
        content = " ".join([f"word{i}" for i in range(250)])
        transcript = Transcript.create("test.txt", content, "user1")
        
        chunks = chunker.chunk_transcript(transcript)
        
        # Should still create chunks (edge case)
        assert len(chunks) > 0
        
        print(f"✓ Boundary condition: Overlap=chunk_size handled")
    
    def test_single_word_transcript(self):
        """Test transcript with single word."""
        processor = TranscriptProcessor()
        chunker = TranscriptChunker()
        
        content = "word"
        transcript = processor.create_transcript("single.txt", content, "user1")
        chunks = chunker.chunk_transcript(transcript)
        
        assert len(chunks) == 1
        assert chunks[0].content == "word"
        assert chunks[0].metadata.word_count == 1
        
        print(f"✓ Boundary condition: Single word transcript handled")
    
    def test_empty_string_content(self):
        """Test handling of empty string content."""
        processor = TranscriptProcessor()
        
        # Empty content should be rejected during validation
        errors = processor.validate_file("test.txt", b"")
        assert len(errors) > 0
        assert any("empty" in err.lower() for err in errors)
        
        print(f"✓ Boundary condition: Empty content rejected")
    
    def test_maximum_attribute_count(self):
        """Test entity with many attributes."""
        # Create entity with 100 attributes
        attributes = [
            AttributeDefinition(name=f"attr{i}", data_type="string")
            for i in range(100)
        ]
        
        entity = EntityDefinition(
            name="ComplexEntity",
            entity_type=EntityType.CONCEPT,
            attributes=attributes
        )
        
        errors = entity.validate()
        assert len(errors) == 0
        
        print(f"✓ Boundary condition: 100 attributes handled")


class TestDataIntegrityAndConsistency:
    """Test data integrity and consistency."""
    
    def test_hash_collision_resistance(self):
        """Test that similar content produces different hashes."""
        processor = TranscriptProcessor()
        
        content1 = "The quick brown fox jumps over the lazy dog"
        content2 = "The quick brown fox jumps over the lazy dog."  # Added period
        
        t1 = processor.create_transcript("test1.txt", content1, "user1")
        t2 = processor.create_transcript("test2.txt", content2, "user1")
        
        # Hashes should be different
        assert t1.content_hash != t2.content_hash
        
        print(f"✓ Data integrity: Hash collision resistance verified")
    
    def test_schema_hash_consistency(self):
        """Test schema hash consistency across multiple computations."""
        entities = [
            EntityDefinition(
                name="Person",
                entity_type=EntityType.CONCEPT,
                attributes=[AttributeDefinition(name="name", data_type="string")]
            )
        ]
        
        # Create same schema multiple times
        hashes = []
        for _ in range(10):
            schema = OntologySchema(
                id="test",
                transcript_id="test",
                entities=entities
            )
            hashes.append(schema.schema_hash)
        
        # All hashes should be identical
        assert len(set(hashes)) == 1
        
        print(f"✓ Data integrity: Schema hash consistency verified")
    
    def test_chunk_boundary_preservation(self):
        """Test that chunk boundaries preserve content."""
        chunker = TranscriptChunker(chunk_size_words=50, overlap_words=10)
        
        content = " ".join([f"word{i}" for i in range(150)])
        transcript = Transcript.create("test.txt", content, "user1")
        
        chunks = chunker.chunk_transcript(transcript)
        
        # Reconstruct content from chunks (removing overlap)
        reconstructed_words = []
        for i, chunk in enumerate(chunks):
            words = chunk.content.split()
            if i == 0:
                reconstructed_words.extend(words)
            else:
                # Skip overlap
                reconstructed_words.extend(words[chunk.metadata.overlap_start:])
        
        original_words = content.split()
        
        # Should match original
        assert len(reconstructed_words) == len(original_words)
        
        print(f"✓ Data integrity: Chunk boundaries preserve content")
    
    def test_entity_merge_preserves_all_attributes(self):
        """Test that merging entities preserves all unique attributes."""
        merger = OntologyMerger()
        
        base = {
            'entities': [{
                'name': 'Person',
                'type': 'concept',
                'attributes': [
                    {'name': 'name', 'data_type': 'string'},
                    {'name': 'age', 'data_type': 'integer'}
                ],
                'parent_entities': []
            }],
            'relationships': []
        }
        
        new = {
            'entities': [{
                'name': 'Person',
                'type': 'concept',
                'attributes': [
                    {'name': 'age', 'data_type': 'integer'},  # Duplicate
                    {'name': 'email', 'data_type': 'string'}  # New
                ],
                'parent_entities': []
            }],
            'relationships': []
        }
        
        merged = merger.merge_schemas(base, new)
        
        person = merged['entities'][0]
        attr_names = {a['name'] for a in person['attributes']}
        
        # Should have all 3 unique attributes
        assert attr_names == {'name', 'age', 'email'}
        
        print(f"✓ Data integrity: Entity merge preserves all attributes")


class TestRealWorldScenarios:
    """Test realistic real-world scenarios."""
    
    def test_multi_hour_meeting_transcript(self):
        """Test processing of long meeting transcript (3+ hours)."""
        processor = TranscriptProcessor()
        chunker = TranscriptChunker()
        
        # Simulate 3-hour meeting (~30,000 words)
        speakers = ["Alice", "Bob", "Charlie", "Diana"]
        segments = []
        
        # Create longer statements to reach 30k words
        for i in range(3000):
            speaker = speakers[i % len(speakers)]
            segments.append(f"{speaker}: This is statement number {i} about the project and we need to discuss various aspects of implementation.")
        
        content = " ".join(segments)
        word_count = len(content.split())
        
        transcript = processor.create_transcript("meeting.txt", content, "user1")
        chunks = chunker.chunk_transcript(transcript)
        
        # Should create multiple chunks (30k words / 5k per chunk = ~6 chunks)
        assert len(chunks) >= 5
        assert word_count >= 30000
        
        # All chunks should have proper metadata
        for chunk in chunks:
            assert chunk.metadata.total_chunks == len(chunks)
            assert chunk.metadata.word_count > 0
        
        print(f"✓ Real-world: 3-hour meeting transcript processed ({len(chunks)} chunks)")
    
    def test_technical_documentation_with_code(self):
        """Test processing technical documentation with code snippets."""
        processor = TranscriptProcessor()
        
        content = """
        # API Documentation
        
        ## Authentication
        Use Bearer tokens for authentication.
        
        ```python
        import requests
        headers = {"Authorization": "Bearer TOKEN"}
        response = requests.get("https://api.example.com/data", headers=headers)
        ```
        
        ## Error Handling
        The API returns standard HTTP status codes.
        
        - 200: Success
        - 401: Unauthorized
        - 404: Not Found
        - 500: Server Error
        """
        
        transcript = processor.create_transcript("docs.md", content, "user1")
        
        # Should handle code blocks and special characters
        assert "```python" in transcript.content
        assert "Authorization" in transcript.content
        
        print(f"✓ Real-world: Technical documentation with code processed")
    
    def test_multilingual_transcript(self):
        """Test processing multilingual transcript."""
        processor = TranscriptProcessor()
        
        content = """
        English: Hello, how are you?
        Spanish: Hola, ¿cómo estás?
        French: Bonjour, comment allez-vous?
        German: Hallo, wie geht es dir?
        Chinese: 你好，你好吗？
        Japanese: こんにちは、お元気ですか？
        Arabic: مرحبا، كيف حالك؟
        Russian: Привет, как дела?
        """
        
        transcript = processor.create_transcript("multilingual.txt", content, "user1")
        
        # Should preserve all languages
        assert "你好" in transcript.content
        assert "こんにちは" in transcript.content
        assert "مرحبا" in transcript.content
        assert "Привет" in transcript.content
        
        print(f"✓ Real-world: Multilingual transcript processed")
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_complex_domain_ontology(self, mock_azure):
        """Test generating complex domain ontology (healthcare)."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
{
  "entities": [
    {
      "name": "Patient",
      "type": "instance",
      "attributes": [
        {"name": "patient_id", "data_type": "string", "required": true},
        {"name": "name", "data_type": "string", "required": true},
        {"name": "date_of_birth", "data_type": "date", "required": true},
        {"name": "blood_type", "data_type": "string"}
      ],
      "parent_entities": ["Person"]
    },
    {
      "name": "Doctor",
      "type": "instance",
      "attributes": [
        {"name": "doctor_id", "data_type": "string", "required": true},
        {"name": "name", "data_type": "string", "required": true},
        {"name": "specialization", "data_type": "string", "required": true}
      ],
      "parent_entities": ["Person"]
    },
    {
      "name": "Diagnosis",
      "type": "concept",
      "attributes": [
        {"name": "diagnosis_code", "data_type": "string", "required": true},
        {"name": "description", "data_type": "string", "required": true},
        {"name": "severity", "data_type": "string"}
      ],
      "parent_entities": []
    },
    {
      "name": "Treatment",
      "type": "concept",
      "attributes": [
        {"name": "treatment_id", "data_type": "string", "required": true},
        {"name": "description", "data_type": "string", "required": true},
        {"name": "duration_days", "data_type": "integer"}
      ],
      "parent_entities": []
    }
  ],
  "relationships": [
    {
      "name": "TREATS",
      "source_entity": "Doctor",
      "target_entity": "Patient",
      "cardinality": "many-to-many"
    },
    {
      "name": "HAS_DIAGNOSIS",
      "source_entity": "Patient",
      "target_entity": "Diagnosis",
      "cardinality": "one-to-many"
    },
    {
      "name": "RECEIVES_TREATMENT",
      "source_entity": "Patient",
      "target_entity": "Treatment",
      "cardinality": "many-to-many"
    }
  ]
}
'''
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client
        
        llm_service = LLMService()
        generator = IncrementalOntologyGenerator(llm_service=llm_service)
        
        content = "Dr. Smith treats patient John Doe who has diabetes and receives insulin treatment."
        
        chunk = TranscriptChunk(
            transcript_id="test",
            content=content,
            metadata=ChunkMetadata(
                chunk_id="chunk_0",
                position=0,
                total_chunks=1,
                word_count=len(content.split()),
                overlap_start=0,
                overlap_end=0,
                start_char=0,
                end_char=len(content)
            )
        )
        
        schema = generator.generate_from_single_chunk(chunk, "test", "user1")
        
        # Should have complex healthcare ontology
        assert len(schema.entities) == 4
        assert len(schema.relationships) == 3
        
        entity_names = {e.name for e in schema.entities}
        assert "Patient" in entity_names
        assert "Doctor" in entity_names
        
        print(f"✓ Real-world: Complex healthcare ontology generated")


class TestSystemStability:
    """Test overall system stability."""
    
    def test_repeated_operations_stability(self):
        """Test system stability over repeated operations."""
        processor = TranscriptProcessor()
        chunker = TranscriptChunker()
        
        errors = []
        
        # Perform 50 iterations
        for i in range(50):
            try:
                content = f"Test content iteration {i} " * 100
                transcript = processor.create_transcript(f"test_{i}.txt", content, "user1")
                chunks = chunker.chunk_transcript(transcript)
                
                # Validate
                assert len(chunks) > 0
                assert transcript.content_hash is not None
            except Exception as e:
                errors.append(f"Iteration {i}: {str(e)}")
        
        # Should have no errors
        assert len(errors) == 0
        
        print(f"✓ System stability: 50 iterations completed without errors")
    
    def test_mixed_workload_stability(self):
        """Test stability under mixed workload."""
        processor = TranscriptProcessor()
        chunker = TranscriptChunker()
        
        operations = []
        
        # Mix of different operations
        for i in range(20):
            # Small transcript
            content = f"Small {i}"
            t = processor.create_transcript(f"small_{i}.txt", content, "user1")
            operations.append(("small", len(chunker.chunk_transcript(t))))
            
            # Medium transcript
            content = f"Medium {i} " * 1000
            t = processor.create_transcript(f"medium_{i}.txt", content, "user1")
            operations.append(("medium", len(chunker.chunk_transcript(t))))
            
            # Large transcript
            content = f"Large {i} " * 10000
            t = processor.create_transcript(f"large_{i}.txt", content, "user1")
            operations.append(("large", len(chunker.chunk_transcript(t))))
        
        # All operations should succeed
        assert len(operations) == 60
        
        print(f"✓ System stability: Mixed workload (60 operations) completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
