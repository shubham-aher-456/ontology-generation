"""Test simple transcript upload and ontology generation."""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_simple_workflow():
    print("=" * 80)
    print("Testing Simple E-Commerce Transcript")
    print("=" * 80)
    
    # 1. Upload transcript
    print("\n1. Uploading transcript...")
    with open("ecommerce_simple.txt", "rb") as f:
        files = {"file": ("ecommerce_simple.txt", f, "text/plain")}
        data = {"title": "E-Commerce System", "description": "Simple e-commerce requirements"}
        response = requests.post(f"{BASE_URL}/transcripts/upload", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        transcript_id = result["transcript_id"]
        print(f"✅ Upload successful! Transcript ID: {transcript_id}")
    else:
        print(f"❌ Upload failed: {response.text}")
        return
    
    # 2. Generate ontology
    print("\n2. Generating ontology...")
    response = requests.post(f"{BASE_URL}/transcripts/{transcript_id}/generate-ontology")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Generation successful!")
        print(f"   Entities: {result['entities_count']}")
        print(f"   Relationships: {result['relationships_count']}")
    else:
        print(f"❌ Generation failed: {response.text}")
        return
    
    # 3. Get ontology details
    print("\n3. Fetching ontology details...")
    response = requests.get(f"{BASE_URL}/transcripts/{transcript_id}/ontology")
    
    if response.status_code == 200:
        ontology = response.json()
        print(f"✅ Ontology retrieved!")
        print(f"\nEntities ({len(ontology['entities'])}):")
        for entity in ontology['entities'][:5]:
            print(f"   - {entity['name']} ({entity['type']})")
        if len(ontology['entities']) > 5:
            print(f"   ... and {len(ontology['entities']) - 5} more")
        
        print(f"\nRelationships ({len(ontology['relationships'])}):")
        for rel in ontology['relationships'][:5]:
            print(f"   - {rel['source']} --{rel['name']}--> {rel['target']}")
        if len(ontology['relationships']) > 5:
            print(f"   ... and {len(ontology['relationships']) - 5} more")
        
        # Save to file for inspection
        with open("ontology_output.json", "w") as f:
            json.dump(ontology, f, indent=2)
        print(f"\n📄 Full ontology saved to: ontology_output.json")
        
    else:
        print(f"❌ Failed to get ontology: {response.text}")
        return
    
    # 4. Load to graph
    print("\n4. Loading to knowledge graph...")
    response = requests.post(f"{BASE_URL}/transcripts/{transcript_id}/load-to-graph")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Loaded to graph!")
        print(f"   Statistics: {result['statistics']}")
    else:
        print(f"❌ Failed to load to graph: {response.text}")
    
    print("\n" + "=" * 80)
    print("✅ Test Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_simple_workflow()
