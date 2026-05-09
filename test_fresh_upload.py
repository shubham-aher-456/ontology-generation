#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def test_fresh_upload():
    """Test with a fresh transcript upload"""
    
    # Create a simple test transcript
    simple_content = """
    Dr. Sarah Chen is the Chief Medical Officer at City Hospital. 
    She leads a team of doctors and nurses. The hospital has an Emergency Department 
    and a Cardiology Department. Dr. Chen works closely with Dr. James Wilson, 
    who is a cardiologist. They are implementing a new Electronic Health Record system 
    that will store patient data and medical histories.
    """
    
    # Write to file
    with open("simple_test.txt", "w") as f:
        f.write(simple_content)
    
    # Upload
    with open("simple_test.txt", "rb") as f:
        files = {"file": ("simple_test.txt", f, "text/plain")}
        data = {"title": "Simple Hospital Test"}
        response = requests.post(f"{BASE_URL}/transcripts/upload", files=files, data=data)
    
    print(f"Upload Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Upload Error: {response.text}")
        return None
    
    result = response.json()
    transcript_id = result["transcript_id"]
    print(f"Uploaded transcript: {transcript_id}")
    
    # Generate ontology
    response = requests.post(f"{BASE_URL}/transcripts/{transcript_id}/generate-ontology")
    print(f"Ontology Generation Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Ontology Error: {response.text}")
        return None
    
    result = response.json()
    print(f"Generated ontology with {result['entities_count']} entities and {result['relationships_count']} relationships")
    
    # Get ontology details
    response = requests.get(f"{BASE_URL}/transcripts/{transcript_id}/ontology")
    print(f"Get Ontology Status: {response.status_code}")
    if response.status_code == 200:
        ontology = response.json()
        print(f"Retrieved ontology with {len(ontology['entities'])} entities and {len(ontology['relationships'])} relationships")
        
        if ontology['entities']:
            print("\nEntities:")
            for entity in ontology['entities'][:5]:
                print(f"  - {entity['name']} ({entity['type']}): {entity.get('description', 'No description')}")
        
        if ontology['relationships']:
            print("\nRelationships:")
            for rel in ontology['relationships'][:5]:
                print(f"  - {rel['source']} --[{rel['name']}]--> {rel['target']}")
    else:
        print(f"Get Ontology Error: {response.text}")
    
    return transcript_id

if __name__ == "__main__":
    print("=== TESTING FRESH TRANSCRIPT UPLOAD ===\n")
    test_fresh_upload()