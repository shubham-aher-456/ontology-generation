#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def test_direct_ontology():
    """Test direct ontology generation from text"""
    sample_text = """
    Dr. Sarah Chen is the Chief Medical Officer at the hospital. 
    She works with Alex Rodriguez, who is the Lead AI Engineer. 
    They are developing an AI-powered healthcare system that includes 
    a Diagnostic AI Engine and a Treatment Recommendation System.
    The system processes patient data and medical images.
    """
    
    request_data = {
        "content": sample_text,
        "previous_context": None
    }
    
    response = requests.post(f"{BASE_URL}/llm/generate-ontology", json=request_data)
    print(f"Direct Ontology Generation Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Direct Ontology Response: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"Direct Ontology Error: {response.text}")
        return None

def test_transcript_details():
    """Get details of existing transcript"""
    # First get list of transcripts
    response = requests.get(f"{BASE_URL}/transcripts")
    if response.status_code == 200:
        transcripts = response.json()
        print(f"Available transcripts: {len(transcripts['transcripts'])}")
        
        if transcripts['transcripts']:
            transcript_id = transcripts['transcripts'][0]['id']
            print(f"Testing with transcript: {transcript_id}")
            
            # Get transcript details
            response = requests.get(f"{BASE_URL}/transcripts/{transcript_id}")
            if response.status_code == 200:
                transcript = response.json()
                print(f"Transcript word count: {transcript['word_count']}")
                print(f"Content preview: {transcript['content'][:200]}...")
                
                # Try to get ontology
                response = requests.get(f"{BASE_URL}/transcripts/{transcript_id}/ontology")
                if response.status_code == 200:
                    ontology = response.json()
                    print(f"Ontology entities: {len(ontology['entities'])}")
                    print(f"Ontology relationships: {len(ontology['relationships'])}")
                    
                    if ontology['entities']:
                        print("Sample entities:")
                        for entity in ontology['entities'][:3]:
                            print(f"  - {entity['name']} ({entity['type']})")
                    
                    if ontology['relationships']:
                        print("Sample relationships:")
                        for rel in ontology['relationships'][:3]:
                            print(f"  - {rel['source']} --[{rel['name']}]--> {rel['target']}")
                else:
                    print(f"Failed to get ontology: {response.text}")

if __name__ == "__main__":
    print("=== TESTING ONTOLOGY GENERATION ===\n")
    
    print("1. Testing Direct LLM Ontology Generation...")
    test_direct_ontology()
    print()
    
    print("2. Testing Existing Transcript Details...")
    test_transcript_details()
    print()