"""Tests for transcript processing and chunking."""
import pytest
from src.services.transcript_processor import TranscriptProcessor, TranscriptChunker
from src.domain.models import Transcript


class TestTranscriptProcessor:
    """Tests for TranscriptProcessor."""
    
    def test_validate_supported_format(self):
        """Test validation accepts supported formats."""
        processor = TranscriptProcessor()
        content = b"Test content"
        
        errors = processor.validate_file("test.txt", content)
        assert len(errors) == 0
        
        errors = processor.validate_file("test.md", content)
        assert len(errors) == 0
    
    def test_validate_unsupported_format(self):
        """Test validation rejects unsupported formats."""
        processor = TranscriptProcessor()
        content = b"Test content"
        
        errors = processor.validate_file("test.exe", content)
        assert len(errors) > 0
        assert any("unsupported" in err.lower() for err in errors)
    
    def test_validate_file_size(self):
        """Test validation checks file size."""
        processor = TranscriptProcessor()
        # Create content larger than max size
        large_content = b"x" * (processor.MAX_FILE_SIZE + 1)
        
        errors = processor.validate_file("test.txt", large_content)
        assert len(errors) > 0
        assert any("size exceeds" in err.lower() for err in errors)
    
    def test_validate_empty_file(self):
        """Test validation rejects empty files."""
        processor = TranscriptProcessor()
        
        errors = processor.validate_file("test.txt", b"")
        assert len(errors) > 0
        assert any("empty" in err.lower() for err in errors)
    
    def test_extract_text_from_txt(self):
        """Test text extraction from TXT file."""
        processor = TranscriptProcessor()
        content = b"This is a test transcript."
        
        text = processor.extract_text("test.txt", content)
        assert text == "This is a test transcript."
    
    def test_create_transcript(self):
        """Test transcript creation."""
        processor = TranscriptProcessor()
        content = "This is a test transcript."
        
        transcript = processor.create_transcript(
            filename="test.txt",
            content=content,
            user_id="user123"
        )
        
        assert transcript.filename == "test.txt"
        assert transcript.content == content
        assert len(transcript.content_hash) == 64


class TestTranscriptChunker:
    """Tests for TranscriptChunker."""
    
    def test_chunk_small_transcript(self):
        """Test chunking returns single chunk for small transcript."""
        chunker = TranscriptChunker(chunk_size_words=100, overlap_words=10)
        
        # Create transcript with 50 words
        content = " ".join([f"word{i}" for i in range(50)])
        transcript = Transcript.create("test.txt", content, "user123")
        
        chunks = chunker.chunk_transcript(transcript)
        
        assert len(chunks) == 1
        assert chunks[0].metadata.total_chunks == 1
        assert chunks[0].metadata.word_count == 50
    
    def test_chunk_large_transcript(self):
        """Test chunking splits large transcript correctly."""
        chunker = TranscriptChunker(chunk_size_words=100, overlap_words=10)
        
        # Create transcript with 250 words
        content = " ".join([f"word{i}" for i in range(250)])
        transcript = Transcript.create("test.txt", content, "user123")
        
        chunks = chunker.chunk_transcript(transcript)
        
        # Should create multiple chunks
        assert len(chunks) > 1
        
        # Check first chunk
        assert chunks[0].metadata.position == 0
        assert chunks[0].metadata.word_count == 100
        assert chunks[0].metadata.overlap_start == 0
        assert chunks[0].metadata.overlap_end == 10
        
        # Check middle chunk has overlap on both sides
        if len(chunks) > 2:
            assert chunks[1].metadata.overlap_start == 10
            assert chunks[1].metadata.overlap_end == 10
        
        # Check last chunk
        last_chunk = chunks[-1]
        assert last_chunk.metadata.overlap_start == 10
        assert last_chunk.metadata.overlap_end == 0
    
    def test_chunk_overlap(self):
        """Test chunks have correct overlap."""
        chunker = TranscriptChunker(chunk_size_words=100, overlap_words=10)
        
        # Create transcript with 200 words
        words = [f"word{i}" for i in range(200)]
        content = " ".join(words)
        transcript = Transcript.create("test.txt", content, "user123")
        
        chunks = chunker.chunk_transcript(transcript)
        
        # Verify overlap between consecutive chunks
        if len(chunks) > 1:
            chunk0_words = chunks[0].content.split()
            chunk1_words = chunks[1].content.split()
            
            # Last 10 words of chunk 0 should match first 10 words of chunk 1
            overlap_words = 10
            assert chunk0_words[-overlap_words:] == chunk1_words[:overlap_words]
    
    def test_chunk_metadata(self):
        """Test chunk metadata is correct."""
        chunker = TranscriptChunker(chunk_size_words=100, overlap_words=10)
        
        content = " ".join([f"word{i}" for i in range(250)])
        transcript = Transcript.create("test.txt", content, "user123")
        
        chunks = chunker.chunk_transcript(transcript)
        
        # Verify all chunks have same total_chunks
        total_chunks = chunks[0].metadata.total_chunks
        for chunk in chunks:
            assert chunk.metadata.total_chunks == total_chunks
        
        # Verify positions are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.metadata.position == i
            assert chunk.metadata.chunk_id == f"{transcript.id}_chunk_{i}"
