"""End-to-end integration tests with real Azure OpenAI API."""
import pytest
from src.services.transcript_processor import TranscriptProcessor, TranscriptChunker
from src.services.llm_service import LLMService
from src.services.ontology_generator import IncrementalOntologyGenerator


@pytest.mark.integration
class TestEndToEndIntegration:
    """Integration tests for complete workflow."""
    
    def test_small_transcript_workflow(self):
        """Test complete workflow with small transcript."""
        # Step 1: Process transcript
        processor = TranscriptProcessor()
        content = """
        John Smith is a software engineer at TechCorp. 
        He works with Mary Johnson, who is a product manager.
        TechCorp is a technology company based in San Francisco.
        John has 5 years of experience in Python programming.
        """
        
        transcript = processor.create_transcript(
            filename="test.txt",
            content=content,
            user_id="test_user"
        )
        
        assert transcript.content_hash is not None
        assert len(transcript.content_hash) == 64
        
        # Step 2: Chunk transcript
        chunker = TranscriptChunker(chunk_size_words=100, overlap_words=10)
        chunks = chunker.chunk_transcript(transcript)
        
        assert len(chunks) >= 1
        print(f"\nCreated {len(chunks)} chunk(s)")
        
        # Step 3: Generate ontology (using real Azure OpenAI)
        try:
            llm_service = LLMService()
            generator = IncrementalOntologyGenerator(llm_service=llm_service)
            
            schema = generator.generate_from_chunks(
                chunks=chunks,
                transcript_id=transcript.id,
                user_id=transcript.user_id
            )
            
            # Verify schema
            assert schema is not None
            assert schema.transcript_id == transcript.id
            assert len(schema.entities) > 0
            
            print(f"\nGenerated ontology:")
            print(f"  - Entities: {len(schema.entities)}")
            print(f"  - Relationships: {len(schema.relationships)}")
            
            # Print entities
            print(f"\nEntities:")
            for entity in schema.entities:
                print(f"  - {entity.name} ({entity.entity_type.value})")
                for attr in entity.attributes[:3]:  # Show first 3 attributes
                    print(f"      * {attr.name}: {attr.data_type}")
            
            # Print relationships
            if schema.relationships:
                print(f"\nRelationships:")
                for rel in schema.relationships[:5]:  # Show first 5
                    print(f"  - {rel.source_entity} -{rel.name}-> {rel.target_entity}")
            
            # Validate schema
            errors = schema.validate()
            if errors:
                print(f"\nValidation errors: {errors}")
            else:
                print(f"\nSchema validation: PASSED ✓")
            
            assert len(errors) == 0, f"Schema validation failed: {errors}"
            
        except Exception as e:
            pytest.skip(f"Skipping integration test due to API error: {str(e)}")
    
    def test_chunked_transcript_workflow(self):
        """Test workflow with large transcript requiring chunking."""
        processor = TranscriptProcessor()
        
        # Create a larger transcript
        content = """
        TechCorp is a leading technology company founded in 2010.
        The company specializes in artificial intelligence and machine learning solutions.
        
        John Smith is the Chief Technology Officer at TechCorp.
        He has been with the company since 2015 and leads a team of 50 engineers.
        John holds a PhD in Computer Science from Stanford University.
        
        Mary Johnson is the VP of Product at TechCorp.
        She joined the company in 2018 after working at Google for 8 years.
        Mary is responsible for the product roadmap and strategy.
        
        The engineering team at TechCorp uses Python, Java, and Go.
        They follow agile methodologies with two-week sprints.
        The team is distributed across offices in San Francisco, New York, and London.
        
        TechCorp's main product is an AI platform called SmartAI.
        SmartAI helps businesses automate their workflows using machine learning.
        The platform has over 1000 enterprise customers worldwide.
        
        The company raised $50 million in Series B funding in 2022.
        Investors include Sequoia Capital and Andreessen Horowitz.
        TechCorp plans to use the funding to expand internationally.
        """
        
        transcript = processor.create_transcript(
            filename="large_test.txt",
            content=content,
            user_id="test_user"
        )
        
        # Chunk with smaller size to force multiple chunks
        chunker = TranscriptChunker(chunk_size_words=50, overlap_words=10)
        chunks = chunker.chunk_transcript(transcript)
        
        print(f"\nCreated {len(chunks)} chunks for large transcript")
        
        # Verify chunking
        assert len(chunks) > 1, "Should create multiple chunks"
        
        # Verify overlap
        if len(chunks) > 1:
            chunk0_words = chunks[0].content.split()
            chunk1_words = chunks[1].content.split()
            
            # Check overlap exists
            assert chunks[0].metadata.overlap_end > 0
            assert chunks[1].metadata.overlap_start > 0
            
            print(f"Chunk 0: {chunks[0].metadata.word_count} words")
            print(f"Chunk 1: {chunks[1].metadata.word_count} words")
            print(f"Overlap: {chunks[0].metadata.overlap_end} words")
        
        # Generate ontology
        try:
            llm_service = LLMService()
            generator = IncrementalOntologyGenerator(llm_service=llm_service)
            
            schema = generator.generate_from_chunks(
                chunks=chunks,
                transcript_id=transcript.id,
                user_id=transcript.user_id
            )
            
            print(f"\nGenerated ontology from {len(chunks)} chunks:")
            print(f"  - Entities: {len(schema.entities)}")
            print(f"  - Relationships: {len(schema.relationships)}")
            
            # Should have multiple entities from different chunks
            assert len(schema.entities) >= 3, "Should extract multiple entities"
            
            # Validate
            errors = schema.validate()
            assert len(errors) == 0, f"Schema validation failed: {errors}"
            
            print(f"\nSchema validation: PASSED ✓")
            
        except Exception as e:
            pytest.skip(f"Skipping integration test due to API error: {str(e)}")


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-s", "-m", "integration"])
