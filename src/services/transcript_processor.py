"""Transcript processing and chunking service."""
import hashlib
import logging
from typing import List, Optional
from pathlib import Path
import PyPDF2
import docx
from src.domain.models import Transcript, TranscriptChunk, ChunkMetadata
from config.settings import settings

logger = logging.getLogger(__name__)


class TranscriptProcessor:
    """Handles transcript file upload and processing."""
    
    SUPPORTED_FORMATS = {'.txt', '.pdf', '.docx', '.md'}
    MAX_FILE_SIZE = settings.max_file_size_mb * 1024 * 1024  # Convert to bytes
    
    def validate_file(self, filename: str, content_bytes: bytes) -> List[str]:
        """Validate uploaded file."""
        errors = []
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            errors.append(f"Unsupported file format: {file_ext}. Supported: {', '.join(self.SUPPORTED_FORMATS)}")
        
        # Check file size
        if len(content_bytes) > self.MAX_FILE_SIZE:
            errors.append(f"File size exceeds maximum of {settings.max_file_size_mb}MB")
        
        # Check if file is empty
        if len(content_bytes) == 0:
            errors.append("File is empty")
        
        return errors
    
    def extract_text(self, filename: str, content_bytes: bytes) -> str:
        """Extract text content from file."""
        file_ext = Path(filename).suffix.lower()
        
        # Check for binary content (null bytes indicate binary)
        if b'\x00' in content_bytes[:1000]:  # Check first 1000 bytes
            raise ValueError("Binary content detected. Only text files are supported.")
        
        try:
            if file_ext == '.txt' or file_ext == '.md':
                return content_bytes.decode('utf-8')
            
            elif file_ext == '.pdf':
                return self._extract_from_pdf(content_bytes)
            
            elif file_ext == '.docx':
                return self._extract_from_docx(content_bytes)
            
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    text = content_bytes.decode(encoding)
                    # Verify it's actually text (not binary decoded as text)
                    if len([c for c in text if ord(c) < 32 and c not in '\n\r\t']) > len(text) * 0.3:
                        raise ValueError("Content appears to be binary, not text")
                    return text
                except UnicodeDecodeError:
                    continue
            raise ValueError("Unable to decode file content")

    def _extract_from_pdf(self, content_bytes: bytes) -> str:
        """Extract text from PDF file."""
        from io import BytesIO
        
        pdf_file = BytesIO(content_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_parts = []
        for page in pdf_reader.pages:
            text_parts.append(page.extract_text())
        
        return '\n'.join(text_parts)
    
    def _extract_from_docx(self, content_bytes: bytes) -> str:
        """Extract text from DOCX file."""
        from io import BytesIO
        
        docx_file = BytesIO(content_bytes)
        doc = docx.Document(docx_file)
        
        text_parts = []
        for paragraph in doc.paragraphs:
            text_parts.append(paragraph.text)
        
        return '\n'.join(text_parts)
    
    def create_transcript(self, filename: str, content: str, user_id: str) -> Transcript:
        """Create transcript object with hash."""
        return Transcript.create(filename=filename, content=content, user_id=user_id)


class TranscriptChunker:
    """Chunks large transcripts into manageable segments."""
    
    def __init__(
        self,
        chunk_size_words: int = settings.chunk_size_words,
        overlap_words: int = settings.chunk_overlap_words
    ):
        """Initialize chunker with configuration."""
        self.chunk_size_words = chunk_size_words
        self.overlap_words = overlap_words
        self.logger = logging.getLogger(__name__)
    
    def chunk_transcript(self, transcript: Transcript) -> List[TranscriptChunk]:
        """Split transcript into chunks with overlap."""
        words = transcript.content.split()
        total_words = len(words)
        
        # Validate configuration
        if self.overlap_words >= self.chunk_size_words:
            self.logger.warning(
                f"Overlap ({self.overlap_words}) >= chunk size ({self.chunk_size_words}). "
                f"Adjusting overlap to chunk_size - 1"
            )
            self.overlap_words = max(0, self.chunk_size_words - 1)
        
        # If transcript is small enough, return single chunk
        if total_words <= self.chunk_size_words:
            metadata = ChunkMetadata(
                chunk_id=f"{transcript.id}_chunk_0",
                position=0,
                total_chunks=1,
                word_count=total_words,
                overlap_start=0,
                overlap_end=0,
                start_char=0,
                end_char=len(transcript.content)
            )
            return [TranscriptChunk(
                transcript_id=transcript.id,
                content=transcript.content,
                metadata=metadata
            )]
        
        # Calculate number of chunks needed
        effective_chunk_size = self.chunk_size_words - self.overlap_words
        
        # Handle edge case where effective_chunk_size is 0 or negative
        if effective_chunk_size <= 0:
            effective_chunk_size = 1
            self.logger.warning(f"Effective chunk size was <= 0, set to 1")
        
        num_chunks = (total_words - self.overlap_words + effective_chunk_size - 1) // effective_chunk_size
        
        chunks = []
        for i in range(num_chunks):
            start_word = i * effective_chunk_size
            end_word = min(start_word + self.chunk_size_words, total_words)
            
            chunk_words = words[start_word:end_word]
            chunk_content = ' '.join(chunk_words)
            
            # Calculate character positions
            start_char = len(' '.join(words[:start_word]))
            if start_char > 0:
                start_char += 1  # Account for space
            end_char = start_char + len(chunk_content)
            
            metadata = ChunkMetadata(
                chunk_id=f"{transcript.id}_chunk_{i}",
                position=i,
                total_chunks=num_chunks,
                word_count=len(chunk_words),
                overlap_start=self.overlap_words if i > 0 else 0,
                overlap_end=self.overlap_words if i < num_chunks - 1 else 0,
                start_char=start_char,
                end_char=end_char
            )
            
            chunks.append(TranscriptChunk(
                transcript_id=transcript.id,
                content=chunk_content,
                metadata=metadata
            ))
            
            self.logger.info(
                f"Created chunk {i+1}/{num_chunks} with {len(chunk_words)} words",
                extra={'chunk_id': metadata.chunk_id}
            )
        
        return chunks
