"""Unit tests for domain models."""
import pytest
from datetime import datetime
from src.domain.models import (
    Transcript, EntityDefinition, RelationshipDefinition,
    OntologySchema, AttributeDefinition, EntityType, ApprovalStatus
)


class TestTranscript:
    """Tests for Transcript model."""
    
    def test_create_transcript(self):
        """Test transcript creation with hash computation."""
        content = "This is a test transcript."
        transcript = Transcript.create(
            filename="test.txt",
            content=content,
            user_id="user123"
        )
        
        assert transcript.filename == "test.txt"
        assert transcript.content == content
        assert transcript.user_id == "user123"
        assert len(transcript.content_hash) == 64  # SHA-256 hash
        assert transcript.size_bytes == len(content.encode('utf-8'))
    
    def test_transcript_serialization(self):
        """Test transcript to_dict and from_dict."""
        transcript = Transcript.create(
            filename="test.txt",
            content="Test content",
            user_id="user123"
        )
        
        # Serialize
        data = transcript.to_dict()
        assert isinstance(data['upload_timestamp'], str)
        
        # Deserialize
        restored = Transcript.from_dict(data)
        assert restored.filename == transcript.filename
        assert restored.content == transcript.content
        assert restored.content_hash == transcript.content_hash


class TestEntityDefinition:
    """Tests for EntityDefinition model."""
    
    def test_valid_entity(self):
        """Test valid entity definition."""
        entity = EntityDefinition(
            name="Person",
            entity_type=EntityType.CONCEPT,
            attributes=[
                AttributeDefinition(name="name", data_type="string", required=True),
                AttributeDefinition(name="age", data_type="integer")
            ]
        )
        
        errors = entity.validate()
        assert len(errors) == 0
    
    def test_entity_without_attributes(self):
        """Test entity validation fails without attributes."""
        entity = EntityDefinition(
            name="Person",
            entity_type=EntityType.CONCEPT,
            attributes=[]
        )
        
        errors = entity.validate()
        assert len(errors) > 0
        assert any("at least one attribute" in err for err in errors)

    def test_entity_duplicate_attributes(self):
        """Test entity validation fails with duplicate attribute names."""
        entity = EntityDefinition(
            name="Person",
            entity_type=EntityType.CONCEPT,
            attributes=[
                AttributeDefinition(name="name", data_type="string"),
                AttributeDefinition(name="name", data_type="string")
            ]
        )
        
        errors = entity.validate()
        assert len(errors) > 0
        assert any("duplicate attribute" in err.lower() for err in errors)
    
    def test_entity_serialization(self):
        """Test entity to_dict and from_dict."""
        entity = EntityDefinition(
            name="Person",
            entity_type=EntityType.CONCEPT,
            attributes=[
                AttributeDefinition(name="name", data_type="string", required=True)
            ]
        )
        
        data = entity.to_dict()
        restored = EntityDefinition.from_dict(data)
        
        assert restored.name == entity.name
        assert restored.entity_type == entity.entity_type
        assert len(restored.attributes) == len(entity.attributes)


class TestRelationshipDefinition:
    """Tests for RelationshipDefinition model."""
    
    def test_valid_relationship(self):
        """Test valid relationship definition."""
        relationship = RelationshipDefinition(
            name="WORKS_AT",
            source_entity="Person",
            target_entity="Company",
            cardinality="many-to-one"
        )
        
        entity_names = ["Person", "Company"]
        errors = relationship.validate(entity_names)
        assert len(errors) == 0
    
    def test_relationship_undefined_entity(self):
        """Test relationship validation fails with undefined entity."""
        relationship = RelationshipDefinition(
            name="WORKS_AT",
            source_entity="Person",
            target_entity="Company",
            cardinality="many-to-one"
        )
        
        entity_names = ["Person"]  # Company not defined
        errors = relationship.validate(entity_names)
        assert len(errors) > 0
        assert any("undefined" in err.lower() for err in errors)
    
    def test_relationship_invalid_cardinality(self):
        """Test relationship validation fails with invalid cardinality."""
        relationship = RelationshipDefinition(
            name="WORKS_AT",
            source_entity="Person",
            target_entity="Company",
            cardinality="invalid"
        )
        
        entity_names = ["Person", "Company"]
        errors = relationship.validate(entity_names)
        assert len(errors) > 0
        assert any("invalid cardinality" in err.lower() for err in errors)


class TestOntologySchema:
    """Tests for OntologySchema model."""
    
    def test_valid_schema(self):
        """Test valid ontology schema."""
        schema = OntologySchema(
            id="schema_1",
            transcript_id="transcript_1",
            entities=[
                EntityDefinition(
                    name="Person",
                    entity_type=EntityType.CONCEPT,
                    attributes=[AttributeDefinition(name="name", data_type="string")]
                )
            ],
            relationships=[]
        )
        
        errors = schema.validate()
        assert len(errors) == 0
    
    def test_schema_without_entities(self):
        """Test schema validation fails without entities."""
        schema = OntologySchema(
            id="schema_1",
            transcript_id="transcript_1",
            entities=[],
            relationships=[]
        )
        
        errors = schema.validate()
        assert len(errors) > 0
        assert any("at least one entity" in err.lower() for err in errors)
    
    def test_schema_circular_inheritance(self):
        """Test schema detects circular inheritance."""
        schema = OntologySchema(
            id="schema_1",
            transcript_id="transcript_1",
            entities=[
                EntityDefinition(
                    name="A",
                    entity_type=EntityType.CONCEPT,
                    attributes=[AttributeDefinition(name="attr", data_type="string")],
                    parent_entities=["B"]
                ),
                EntityDefinition(
                    name="B",
                    entity_type=EntityType.CONCEPT,
                    attributes=[AttributeDefinition(name="attr", data_type="string")],
                    parent_entities=["A"]
                )
            ]
        )
        
        errors = schema.validate()
        assert len(errors) > 0
        assert any("circular inheritance" in err.lower() for err in errors)
    
    def test_schema_hash_computation(self):
        """Test schema hash is computed correctly."""
        schema = OntologySchema(
            id="schema_1",
            transcript_id="transcript_1",
            entities=[
                EntityDefinition(
                    name="Person",
                    entity_type=EntityType.CONCEPT,
                    attributes=[AttributeDefinition(name="name", data_type="string")]
                )
            ]
        )
        
        assert len(schema.schema_hash) == 64  # SHA-256 hash
        
        # Same content should produce same hash
        schema2 = OntologySchema(
            id="schema_2",
            transcript_id="transcript_2",
            entities=[
                EntityDefinition(
                    name="Person",
                    entity_type=EntityType.CONCEPT,
                    attributes=[AttributeDefinition(name="name", data_type="string")]
                )
            ]
        )
        
        assert schema.schema_hash == schema2.schema_hash
    
    def test_schema_serialization(self):
        """Test schema to_dict and from_dict."""
        schema = OntologySchema(
            id="schema_1",
            transcript_id="transcript_1",
            entities=[
                EntityDefinition(
                    name="Person",
                    entity_type=EntityType.CONCEPT,
                    attributes=[AttributeDefinition(name="name", data_type="string")]
                )
            ],
            relationships=[
                RelationshipDefinition(
                    name="KNOWS",
                    source_entity="Person",
                    target_entity="Person",
                    cardinality="many-to-many"
                )
            ]
        )
        
        data = schema.to_dict()
        restored = OntologySchema.from_dict(data)
        
        assert restored.id == schema.id
        assert len(restored.entities) == len(schema.entities)
        assert len(restored.relationships) == len(schema.relationships)
        assert restored.schema_hash == schema.schema_hash
