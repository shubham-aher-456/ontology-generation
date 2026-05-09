"""Knowledge Graph Service for Neo4j integration."""
import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, Neo4jError
from config.settings import settings
from src.domain.models import OntologySchema, EntityDefinition, RelationshipDefinition


class KnowledgeGraphService:
    """Service for managing knowledge graph in Neo4j."""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """Initialize Neo4j connection."""
        self.uri = uri or settings.neo4j_uri
        self.user = user or settings.neo4j_user
        self.password = password or settings.neo4j_password
        self.driver: Optional[Driver] = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> None:
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Verify connectivity
            self.driver.verify_connectivity()
            self.logger.info(f"Connected to Neo4j at {self.uri}")
        except ServiceUnavailable as e:
            self.logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self) -> None:
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.logger.info("Neo4j connection closed")
    
    def clear_database(self) -> None:
        """Clear all nodes and relationships (use with caution!)."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            self.logger.info("Database cleared")
    
    def load_ontology(self, schema: OntologySchema) -> Dict[str, int]:
        """Load ontology schema into knowledge graph."""
        stats = {
            "entities_created": 0,
            "relationships_created": 0,
            "constraints_created": 0
        }
        
        with self.driver.session() as session:
            # Create constraints for entity uniqueness
            stats["constraints_created"] = self._create_constraints(session, schema)
            
            # Create entity nodes
            stats["entities_created"] = self._create_entities(session, schema)
            
            # Create relationships
            stats["relationships_created"] = self._create_relationships(session, schema)
        
        self.logger.info(f"Loaded ontology: {stats}")
        return stats
    
    def _create_constraints(self, session: Session, schema: OntologySchema) -> int:
        """Create uniqueness constraints for entities."""
        count = 0
        entity_types = set(e.name for e in schema.entities)
        
        for entity_type in entity_types:
            try:
                # Escape entity type with backticks for Neo4j
                escaped_type = f"`{entity_type}`"
                # Create constraint for entity name uniqueness
                session.run(
                    f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{escaped_type}) "
                    f"REQUIRE n.name IS UNIQUE"
                )
                count += 1
            except Neo4jError as e:
                self.logger.warning(f"Constraint creation failed for {entity_type}: {e}")
        
        return count
    
    def _create_entities(self, session: Session, schema: OntologySchema) -> int:
        """Create entity nodes in the graph."""
        count = 0
        
        for entity in schema.entities:
            # Build properties dict
            properties = {
                "name": entity.name,
                "entity_type": entity.entity_type.value,
                "description": entity.description or "",
                "schema_id": schema.id,
                "transcript_id": schema.transcript_id
            }
            
            # Add attributes as JSON string (Neo4j doesn't support nested dicts)
            if entity.attributes:
                import json
                attributes_list = [
                    {
                        "name": attr.name,
                        "data_type": attr.data_type,
                        "required": attr.required,
                        "description": attr.description or ""
                    }
                    for attr in entity.attributes
                ]
                properties["attributes"] = json.dumps(attributes_list)
            
            # Escape entity name with backticks for Neo4j
            escaped_name = f"`{entity.name}`"
            
            # Create node with label
            query = f"""
            MERGE (e:{escaped_name} {{name: $name}})
            SET e += $properties
            RETURN e
            """
            
            session.run(query, name=entity.name, properties=properties)
            count += 1
        
        return count
    
    def _create_relationships(self, session: Session, schema: OntologySchema) -> int:
        """Create relationships between entities."""
        count = 0
        
        for rel in schema.relationships:
            # Escape entity names with backticks for Neo4j
            escaped_source = f"`{rel.source_entity}`"
            escaped_target = f"`{rel.target_entity}`"
            escaped_rel_name = f"`{rel.name}`"
            
            # Create relationship
            query = f"""
            MATCH (source:{escaped_source} {{name: $source_name}})
            MATCH (target:{escaped_target} {{name: $target_name}})
            MERGE (source)-[r:{escaped_rel_name}]->(target)
            SET r.cardinality = $cardinality,
                r.description = $description,
                r.schema_id = $schema_id
            RETURN r
            """
            
            session.run(
                query,
                source_name=rel.source_entity,
                target_name=rel.target_entity,
                cardinality=rel.cardinality,
                description=rel.description or "",
                schema_id=schema.id
            )
            count += 1
        
        # Create parent-child relationships
        for entity in schema.entities:
            for parent in entity.parent_entities:
                # Escape entity names with backticks for Neo4j
                escaped_entity = f"`{entity.name}`"
                
                query = f"""
                MATCH (child:{escaped_entity} {{name: $child_name}})
                MATCH (parent {{name: $parent_name}})
                MERGE (child)-[r:IS_A]->(parent)
                SET r.schema_id = $schema_id
                RETURN r
                """
                
                session.run(
                    query,
                    child_name=entity.name,
                    parent_name=parent,
                    schema_id=schema.id
                )
                count += 1
        
        return count
    
    def query_graph(self, cypher_query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters or {})
            return [dict(record) for record in result]
    
    def find_entity(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Find an entity by name."""
        query = """
        MATCH (e {name: $name})
        RETURN e
        """
        results = self.query_graph(query, {"name": entity_name})
        return results[0]["e"] if results else None
    
    def find_relationships(self, source_entity: str, relationship_type: str = None) -> List[Dict[str, Any]]:
        """Find relationships from a source entity."""
        if relationship_type:
            query = f"""
            MATCH (source {{name: $source}})-[r:{relationship_type}]->(target)
            RETURN source, r, target
            """
        else:
            query = """
            MATCH (source {name: $source})-[r]->(target)
            RETURN source, type(r) as relationship_type, r, target
            """
        
        return self.query_graph(query, {"source": source_entity})
    
    def find_path(self, start_entity: str, end_entity: str, max_depth: int = 5) -> List[Dict[str, Any]]:
        """Find shortest path between two entities."""
        query = """
        MATCH path = shortestPath(
            (start {name: $start})-[*..%d]-(end {name: $end})
        )
        RETURN path, length(path) as path_length
        """ % max_depth
        
        return self.query_graph(query, {"start": start_entity, "end": end_entity})
    
    def get_entity_neighbors(self, entity_name: str, depth: int = 1) -> List[Dict[str, Any]]:
        """Get all neighbors of an entity up to specified depth."""
        query = """
        MATCH path = (e {name: $name})-[*1..%d]-(neighbor)
        RETURN DISTINCT neighbor, length(path) as distance
        ORDER BY distance
        """ % depth
        
        return self.query_graph(query, {"name": entity_name})
    
    def get_statistics(self) -> Dict[str, int]:
        """Get graph statistics."""
        stats = {}
        
        with self.driver.session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) as count")
            stats["total_nodes"] = result.single()["count"]
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            stats["total_relationships"] = result.single()["count"]
            
            # Count node labels
            result = session.run("CALL db.labels()")
            stats["total_labels"] = len(list(result))
            
            # Count relationship types
            result = session.run("CALL db.relationshipTypes()")
            stats["total_relationship_types"] = len(list(result))
        
        return stats
    
    def complex_query(self, question: str) -> Dict[str, Any]:
        """
        Answer complex questions about the knowledge graph.
        This is a simplified version - in production, use NLP to parse questions.
        """
        question_lower = question.lower()
        
        # Pattern matching for common question types
        if "how many" in question_lower and "entities" in question_lower:
            query = "MATCH (n) RETURN count(DISTINCT n) as count"
            result = self.query_graph(query)
            return {"answer": result[0]["count"], "type": "count"}
        
        elif "how many" in question_lower and "relationships" in question_lower:
            query = "MATCH ()-[r]->() RETURN count(r) as count"
            result = self.query_graph(query)
            return {"answer": result[0]["count"], "type": "count"}
        
        elif "connected to" in question_lower or "related to" in question_lower:
            # Extract entity name (simplified)
            words = question.split()
            entity_name = None
            for i, word in enumerate(words):
                if word.lower() in ["to", "with"]:
                    if i + 1 < len(words):
                        entity_name = words[i + 1].strip("?.,")
                        break
            
            if entity_name:
                relationships = self.find_relationships(entity_name)
                return {
                    "answer": relationships,
                    "type": "relationships",
                    "count": len(relationships)
                }
        
        elif "path between" in question_lower or "connect" in question_lower:
            # Extract two entity names (simplified)
            words = question.split()
            entities = []
            for word in words:
                if word[0].isupper() and word not in ["What", "How", "Is", "Are"]:
                    entities.append(word.strip("?.,"))
            
            if len(entities) >= 2:
                path = self.find_path(entities[0], entities[1])
                return {
                    "answer": path,
                    "type": "path",
                    "exists": len(path) > 0
                }
        
        return {"answer": "Unable to parse question", "type": "error"}
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
