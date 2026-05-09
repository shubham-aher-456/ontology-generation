"""Tests for LLM service."""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from src.services.llm_service import (
    LLMService, CircuitBreaker, CircuitBreakerOpenError,
    retry_with_backoff
)


class TestCircuitBreaker:
    """Tests for CircuitBreaker."""
    
    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker allows calls in CLOSED state."""
        cb = CircuitBreaker(failure_threshold=3, timeout_seconds=1)
        
        def success_func():
            return "success"
        
        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0
    
    def test_circuit_breaker_opens_after_threshold(self):
        """Test circuit breaker opens after failure threshold."""
        cb = CircuitBreaker(failure_threshold=3, timeout_seconds=1)
        
        def failing_func():
            raise Exception("Test failure")
        
        # Fail 3 times to reach threshold
        for i in range(3):
            with pytest.raises(Exception):
                cb.call(failing_func)
        
        assert cb.state == "OPEN"
        assert cb.failure_count == 3
        
        # Next call should raise CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(failing_func)
    
    def test_circuit_breaker_half_open_after_timeout(self):
        """Test circuit breaker transitions to HALF_OPEN after timeout."""
        cb = CircuitBreaker(failure_threshold=2, timeout_seconds=1)
        
        def failing_func():
            raise Exception("Test failure")
        
        # Open the circuit
        for i in range(2):
            with pytest.raises(Exception):
                cb.call(failing_func)
        
        assert cb.state == "OPEN"
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Next call should transition to HALF_OPEN and try again
        with pytest.raises(Exception):
            cb.call(failing_func)
        
        # State should have been HALF_OPEN during the call
        # (it will go back to OPEN after failure)
        assert cb.state == "OPEN"


class TestRetryWithBackoff:
    """Tests for retry_with_backoff decorator."""
    
    def test_retry_succeeds_on_first_attempt(self):
        """Test function succeeds on first attempt."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, initial_delay=0.1, exponential_base=2)
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = success_func()
        assert result == "success"
        assert call_count == 1
    
    def test_retry_succeeds_after_failures(self):
        """Test function succeeds after some failures."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, initial_delay=0.1, exponential_base=2)
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = flaky_func()
        assert result == "success"
        assert call_count == 3
    
    def test_retry_fails_after_max_attempts(self):
        """Test function fails after max retry attempts."""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, initial_delay=0.1, exponential_base=2)
        def failing_func():
            nonlocal call_count
            call_count += 1
            raise Exception("Persistent failure")
        
        with pytest.raises(Exception, match="Persistent failure"):
            failing_func()
        
        assert call_count == 3  # Initial + 2 retries


class TestLLMService:
    """Tests for LLMService."""
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_generate_ontology_success(self, mock_azure_openai):
        """Test successful ontology generation."""
        # Mock LLM response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
{
  "entities": [
    {
      "name": "Person",
      "type": "concept",
      "attributes": [
        {"name": "name", "data_type": "string", "required": true},
        {"name": "age", "data_type": "integer", "required": false}
      ],
      "parent_entities": [],
      "description": "A human being"
    }
  ],
  "relationships": [
    {
      "name": "KNOWS",
      "source_entity": "Person",
      "target_entity": "Person",
      "cardinality": "many-to-many",
      "properties": [],
      "description": "Person knows another person"
    }
  ]
}
'''
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        # Create service and generate ontology
        service = LLMService()
        chunk_content = "John knows Mary. Mary knows Bob."
        
        ontology = service.generate_ontology(chunk_content)
        
        assert 'entities' in ontology
        assert 'relationships' in ontology
        assert len(ontology['entities']) == 1
        assert len(ontology['relationships']) == 1
        assert ontology['entities'][0]['name'] == 'Person'
        assert ontology['relationships'][0]['name'] == 'KNOWS'
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_generate_ontology_with_context(self, mock_azure_openai):
        """Test ontology generation with previous context."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"entities": [], "relationships": []}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        service = LLMService()
        chunk_content = "Test content"
        previous_context = {
            'entity_names': ['Person', 'Company'],
            'relationship_names': ['WORKS_AT']
        }
        
        ontology = service.generate_ontology(chunk_content, previous_context)
        
        assert 'entities' in ontology
        assert 'relationships' in ontology
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_parse_ontology_with_markdown(self, mock_azure_openai):
        """Test parsing ontology response with markdown code blocks."""
        mock_azure_openai.return_value = Mock()
        
        service = LLMService()
        
        # Test with markdown code block
        response_text = '''```json
{
  "entities": [{"name": "Test", "type": "concept", "attributes": []}],
  "relationships": []
}
```'''
        
        ontology = service._parse_ontology_response(response_text)
        
        assert len(ontology['entities']) == 1
        assert ontology['entities'][0]['name'] == 'Test'
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_parse_ontology_invalid_json(self, mock_azure_openai):
        """Test parsing handles invalid JSON gracefully."""
        mock_azure_openai.return_value = Mock()
        
        service = LLMService()
        
        # Invalid JSON should return empty ontology
        response_text = "This is not valid JSON"
        ontology = service._parse_ontology_response(response_text)
        
        assert ontology == {'entities': [], 'relationships': []}
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_refine_schema(self, mock_azure_openai):
        """Test schema refinement based on feedback."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
{
  "entities": [
    {
      "name": "Person",
      "type": "concept",
      "attributes": [
        {"name": "full_name", "data_type": "string", "required": true}
      ],
      "parent_entities": [],
      "description": "Updated description"
    }
  ],
  "relationships": []
}
'''
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        service = LLMService()
        current_schema = {
            'entities': [{'name': 'Person', 'type': 'concept', 'attributes': []}],
            'relationships': []
        }
        feedback = "Change 'name' attribute to 'full_name'"
        original_text = "Test text"
        
        refined_schema = service.refine_schema(current_schema, feedback, original_text)
        
        assert len(refined_schema['entities']) == 1
        assert refined_schema['entities'][0]['attributes'][0]['name'] == 'full_name'
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_compute_embedding(self, mock_azure_openai):
        """Test embedding computation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3]
        mock_client.embeddings.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        service = LLMService()
        embedding = service.compute_embedding("Test text")
        
        assert embedding == [0.1, 0.2, 0.3]
    
    @patch('src.services.llm_service.AzureOpenAI')
    def test_compute_embeddings_batch(self, mock_azure_openai):
        """Test batch embedding computation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(), Mock()]
        mock_response.data[0].embedding = [0.1, 0.2]
        mock_response.data[1].embedding = [0.3, 0.4]
        mock_client.embeddings.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        service = LLMService()
        embeddings = service.compute_embeddings_batch(["Text 1", "Text 2"])
        
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2]
        assert embeddings[1] == [0.3, 0.4]
