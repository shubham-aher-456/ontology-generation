"""Core domain models for ontology and knowledge graph."""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import hashlib
import json


class ApprovalStatus(Enum):
    """Schema approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class EntityType(Enum):
    """Entity type classification."""
    CONCEPT = "concept"
    INSTANCE = "instance"
    ABSTRACT = "abstract"


@dataclass
class Transcript:
    """Represents an uploaded transcript document."""
    id: str
    filename: str
    content: str
    content_hash: str
    size_bytes: int
    upload_timestamp: datetime
    user_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, filename: str, content: str, user_id: str) -> "Transcript":
        """Create a new transcript with computed hash."""
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return cls(
            id=f"transcript_{content_hash[:16]}",
            filename=filename,
            content=content,
            content_hash=content_hash,
            size_bytes=len(content.encode('utf-8')),
            upload_timestamp=datetime.utcnow(),
            user_id=user_id,
            metadata={}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['upload_timestamp'] = self.upload_timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transcript":
        """Create from dictionary."""
        data['upload_timestamp'] = datetime.fromisoformat(data['upload_timestamp'])
        return cls(**data)


@dataclass
class AttributeDefinition:
    """Defines an attribute of an entity."""
    name: str
    data_type: str  # string, integer, float, boolean, date, datetime
    required: bool = False
    default_value: Optional[Any] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttributeDefinition":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class EntityDefinition:
    """Defines an entity type in the ontology."""
    name: str
    entity_type: EntityType
    attributes: List[AttributeDefinition] = field(default_factory=list)
    parent_entities: List[str] = field(default_factory=list)
    description: Optional[str] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> List[str]:
        """Validate entity definition."""
        errors = []
        
        if not self.name:
            errors.append("Entity name is required")
        
        if not self.attributes:
            errors.append(f"Entity {self.name} must have at least one attribute")
        
        # Check for duplicate attribute names
        attr_names = [attr.name for attr in self.attributes]
        if len(attr_names) != len(set(attr_names)):
            errors.append(f"Entity {self.name} has duplicate attribute names")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['entity_type'] = self.entity_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntityDefinition":
        """Create from dictionary."""
        data['entity_type'] = EntityType(data['entity_type'])
        data['attributes'] = [AttributeDefinition.from_dict(a) for a in data.get('attributes', [])]
        return cls(**data)


@dataclass
class RelationshipDefinition:
    """Defines a relationship type in the ontology."""
    name: str
    source_entity: str
    target_entity: str
    cardinality: str  # one-to-one, one-to-many, many-to-one, many-to-many
    properties: List[AttributeDefinition] = field(default_factory=list)
    is_symmetric: bool = False
    inverse_relationship: Optional[str] = None
    description: Optional[str] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self, entity_names: List[str]) -> List[str]:
        """Validate relationship definition."""
        errors = []
        
        if not self.name:
            errors.append("Relationship name is required")
        
        if not self.source_entity:
            errors.append(f"Relationship {self.name} must have source entity")
        elif self.source_entity not in entity_names:
            errors.append(f"Relationship {self.name} references undefined source entity: {self.source_entity}")
        
        if not self.target_entity:
            errors.append(f"Relationship {self.name} must have target entity")
        elif self.target_entity not in entity_names:
            errors.append(f"Relationship {self.name} references undefined target entity: {self.target_entity}")
        
        valid_cardinalities = ["one-to-one", "one-to-many", "many-to-one", "many-to-many"]
        if self.cardinality not in valid_cardinalities:
            errors.append(f"Relationship {self.name} has invalid cardinality: {self.cardinality}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelationshipDefinition":
        """Create from dictionary."""
        data['properties'] = [AttributeDefinition.from_dict(p) for p in data.get('properties', [])]
        return cls(**data)


@dataclass
class OntologySchema:
    """Represents a complete ontology schema."""
    id: str
    transcript_id: str
    entities: List[EntityDefinition] = field(default_factory=list)
    relationships: List[RelationshipDefinition] = field(default_factory=list)
    version: int = 1
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    user_id: str = ""
    feedback_count: int = 0
    schema_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Compute schema hash after initialization."""
        if not self.schema_hash:
            self.schema_hash = self.compute_hash()

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of schema content."""
        schema_content = {
            'entities': [e.to_dict() for e in self.entities],
            'relationships': [r.to_dict() for r in self.relationships]
        }
        content_str = json.dumps(schema_content, sort_keys=True)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()
    
    def validate(self) -> List[str]:
        """Validate complete schema."""
        errors = []
        
        if not self.entities:
            errors.append("Schema must contain at least one entity")
        
        # Validate each entity
        for entity in self.entities:
            errors.extend(entity.validate())
        
        # Get entity names for relationship validation
        entity_names = [e.name for e in self.entities]
        
        # Check for duplicate entity names
        if len(entity_names) != len(set(entity_names)):
            errors.append("Schema contains duplicate entity names")
        
        # Validate each relationship
        for relationship in self.relationships:
            errors.extend(relationship.validate(entity_names))
        
        # Check for circular inheritance
        circular = self._detect_circular_inheritance()
        if circular:
            errors.append(f"Circular inheritance detected: {' -> '.join(circular)}")
        
        return errors
    
    def _detect_circular_inheritance(self) -> Optional[List[str]]:
        """Detect circular inheritance using DFS."""
        # Build adjacency list
        graph: Dict[str, List[str]] = {}
        for entity in self.entities:
            graph[entity.name] = entity.parent_entities
        
        # DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    result = dfs(neighbor, path.copy())
                    if result:
                        return result
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            rec_stack.remove(node)
            return None
        
        for entity_name in graph:
            if entity_name not in visited:
                result = dfs(entity_name, [])
                if result:
                    return result
        
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'transcript_id': self.transcript_id,
            'entities': [e.to_dict() for e in self.entities],
            'relationships': [r.to_dict() for r in self.relationships],
            'version': self.version,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id,
            'feedback_count': self.feedback_count,
            'schema_hash': self.schema_hash,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OntologySchema":
        """Create from dictionary."""
        data['entities'] = [EntityDefinition.from_dict(e) for e in data.get('entities', [])]
        data['relationships'] = [RelationshipDefinition.from_dict(r) for r in data.get('relationships', [])]
        data['status'] = ApprovalStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class ChunkMetadata:
    """Metadata for a transcript chunk."""
    chunk_id: str
    position: int
    total_chunks: int
    word_count: int
    overlap_start: int
    overlap_end: int
    start_char: int
    end_char: int


@dataclass
class TranscriptChunk:
    """Represents a chunk of a large transcript."""
    transcript_id: str
    content: str
    metadata: ChunkMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'transcript_id': self.transcript_id,
            'content': self.content,
            'metadata': asdict(self.metadata)
        }


@dataclass
class UserFeedback:
    """User feedback on a schema."""
    id: str
    schema_id: str
    user_id: str
    feedback_text: str
    feedback_type: str  # approve, reject, modify
    timestamp: datetime
    changes_requested: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
