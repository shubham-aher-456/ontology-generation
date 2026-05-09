#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def upload_transcript():
    """Upload the complex transcript"""
    with open("complex_transcript.txt", "rb") as f:
        files = {"file": ("complex_transcript.txt", f, "text/plain")}
        data = {
            "title": "AI Healthcare System Discussion",
            "description": "Complex transcript about AI-powered healthcare architecture"
        }
        response = requests.post(f"{BASE_URL}/transcripts/upload", files=files, data=data)
    
    print(f"Upload Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Upload Response: {json.dumps(result, indent=2)}")
        return result.get("transcript_id")
    else:
        print(f"Upload Error: {response.text}")
        return None

def generate_ontology(transcript_id):
    """Generate ontology from transcript"""
    response = requests.post(f"{BASE_URL}/transcripts/{transcript_id}/generate-ontology")
    print(f"Ontology Generation Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Ontology Response: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"Ontology Error: {response.text}")
        return False

def get_ontology(transcript_id):
    """Get the generated ontology"""
    response = requests.get(f"{BASE_URL}/transcripts/{transcript_id}/ontology")
    print(f"Get Ontology Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Ontology Details:")
        print(f"  Entities: {len(result.get('entities', []))}")
        print(f"  Relationships: {len(result.get('relationships', []))}")
        
        # Show first few entities and relationships
        entities = result.get('entities', [])[:5]
        relationships = result.get('relationships', [])[:5]
        
        print(f"\nFirst 5 Entities:")
        for entity in entities:
            print(f"  - {entity.get('name')} ({entity.get('type')}): {entity.get('description', 'No description')}")
        
        print(f"\nFirst 5 Relationships:")
        for rel in relationships:
            print(f"  - {rel.get('source')} --[{rel.get('name')}]--> {rel.get('target')}")
        
        return result
    else:
        print(f"Get Ontology Error: {response.text}")
        return None

def get_chunks(transcript_id):
    """Get transcript chunks"""
    response = requests.get(f"{BASE_URL}/transcripts/{transcript_id}/chunks")
    print(f"Get Chunks Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Chunks: {result.get('total_chunks')} chunks created")
        return result
    else:
        print(f"Get Chunks Error: {response.text}")
        return None

def load_to_graph(transcript_id):
    """Load ontology to knowledge graph"""
    response = requests.post(f"{BASE_URL}/transcripts/{transcript_id}/load-to-graph")
    print(f"Load to Graph Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Graph Load Response: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"Graph Load Error: {response.text}")
        return False

def get_system_status():
    """Get system status"""
    response = requests.get(f"{BASE_URL}/system/status")
    print(f"System Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"System Status: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"System Status Error: {response.text}")
        return None

def main():
    """Run complete end-to-end test"""
    print("=== ONTOLOGY KNOWLEDGE BASE API TEST ===\n")
    
    # Test 1: Health check
    print("1. Testing Health Check...")
    if not test_health():
        print("Health check failed!")
        return
    print()
    
    # Test 2: Upload transcript
    print("2. Uploading Complex Transcript...")
    transcript_id = upload_transcript()
    if not transcript_id:
        print("Upload failed!")
        return
    print()
    
    # Test 3: Generate ontology
    print("3. Generating Ontology...")
    if not generate_ontology(transcript_id):
        print("Ontology generation failed!")
        return
    print()
    
    # Test 4: Get ontology details
    print("4. Retrieving Ontology Details...")
    ontology = get_ontology(transcript_id)
    if not ontology:
        print("Failed to retrieve ontology!")
        return
    print()
    
    # Test 5: Get chunks
    print("5. Retrieving Transcript Chunks...")
    chunks = get_chunks(transcript_id)
    print()
    
    # Test 6: Load to knowledge graph
    print("6. Loading to Knowledge Graph...")
    if not load_to_graph(transcript_id):
        print("Failed to load to knowledge graph!")
        return
    print()
    
    # Test 7: System status
    print("7. Getting System Status...")
    status = get_system_status()
    print()
    
    print("=== END-TO-END TEST COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()