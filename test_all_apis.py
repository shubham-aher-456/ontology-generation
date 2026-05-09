"""Comprehensive API testing script for all endpoints."""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_endpoint(method, endpoint, description, **kwargs):
    """Test an API endpoint and print results."""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Testing: {description}")
    print(f"   Method: {method.upper()}")
    print(f"   URL: {url}")
    
    try:
        if method.lower() == "get":
            response = requests.get(url, **kwargs)
        elif method.lower() == "post":
            response = requests.post(url, **kwargs)
        elif method.lower() == "delete":
            response = requests.delete(url, **kwargs)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code < 400:
            print(f"   ✅ SUCCESS")
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:500]}")
                return data
            except:
                print(f"   Response: {response.text[:500]}")
                return response.text
        else:
            print(f"   ❌ FAILED")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return None

def main():
    """Run all API tests."""
    print("\n" + "🚀"*40)
    print("  ONTOLOGY KNOWLEDGE BASE - COMPREHENSIVE API TESTING")
    print("🚀"*40)
    
    # ============= BASIC ENDPOINTS =============
    print_section("1. BASIC ENDPOINTS")
    
    test_endpoint("GET", "/", "Root endpoint")
    test_endpoint("GET", "/health", "Health check")
    test_endpoint("GET", "/config", "Get configuration")
    test_endpoint("GET", "/system/status", "System status")
    
    # ============= TRANSCRIPT UPLOAD =============
    print_section("2. TRANSCRIPT UPLOAD & MANAGEMENT")
    
    # Create a test transcript file
    test_transcript = """
    Meeting Transcript: Product Development Discussion
    
    John: We need to develop a new customer management system.
    Sarah: The system should have user authentication and role-based access control.
    Mike: We also need a database to store customer information including name, email, and phone.
    John: The customer can place multiple orders, and each order contains products.
    Sarah: Each product has a name, price, and category.
    Mike: We should implement a payment processing system that handles credit cards and PayPal.
    John: The system needs to generate invoices and send email notifications.
    Sarah: We also need an admin dashboard to view analytics and reports.
    """
    
    # Save test transcript
    with open("test_transcript.txt", "w") as f:
        f.write(test_transcript)
    
    # Upload transcript
    with open("test_transcript.txt", "rb") as f:
        files = {"file": ("test_transcript.txt", f, "text/plain")}
        data = {"title": "Product Development Meeting", "description": "Discussion about new CMS"}
        upload_result = test_endpoint("POST", "/transcripts/upload", 
                                     "Upload transcript", 
                                     files=files, data=data)
    
    if not upload_result:
        print("\n❌ Transcript upload failed. Cannot continue with remaining tests.")
        return
    
    transcript_id = upload_result.get("transcript_id")
    print(f"\n📝 Transcript ID: {transcript_id}")
    
    # List transcripts
    test_endpoint("GET", "/transcripts", "List all transcripts")
    
    # Get specific transcript
    test_endpoint("GET", f"/transcripts/{transcript_id}", "Get transcript details")
    
    # ============= ONTOLOGY GENERATION =============
    print_section("3. ONTOLOGY GENERATION")
    
    ontology_result = test_endpoint("POST", f"/transcripts/{transcript_id}/generate-ontology",
                                   "Generate ontology from transcript")
    
    if ontology_result:
        # Get generated ontology
        test_endpoint("GET", f"/transcripts/{transcript_id}/ontology", 
                     "Get generated ontology")
        
        # List all ontologies
        test_endpoint("GET", "/ontologies", "List all ontologies")
    
    # ============= CHUNK ENDPOINTS =============
    print_section("4. CHUNK MANAGEMENT")
    
    test_endpoint("GET", f"/transcripts/{transcript_id}/chunks", 
                 "Get transcript chunks")
    
    # ============= KNOWLEDGE GRAPH ENDPOINTS =============
    print_section("5. KNOWLEDGE GRAPH OPERATIONS")
    
    # Load ontology to graph
    load_result = test_endpoint("POST", f"/transcripts/{transcript_id}/load-to-graph",
                               "Load ontology to knowledge graph")
    
    if load_result:
        # Get graph statistics
        test_endpoint("GET", "/knowledge-graph/statistics", 
                     "Get knowledge graph statistics")
        
        # Find entity
        test_endpoint("GET", "/knowledge-graph/entity/Customer", 
                     "Find Customer entity")
        
        # Get entity relationships
        test_endpoint("GET", "/knowledge-graph/entity/Customer/relationships",
                     "Get Customer relationships")
        
        # Get entity neighbors
        test_endpoint("GET", "/knowledge-graph/entity/Customer/neighbors?depth=2",
                     "Get Customer neighbors")
        
        # Find path between entities
        test_endpoint("GET", "/knowledge-graph/path/Customer/Order",
                     "Find path between Customer and Order")
        
        # Execute Cypher query
        cypher_query = {
            "query": "MATCH (n) RETURN labels(n) as label, count(n) as count",
            "parameters": {}
        }
        test_endpoint("POST", "/knowledge-graph/query",
                     "Execute Cypher query",
                     json=cypher_query)
        
        # Complex query
        complex_query = {
            "question": "What entities are related to Customer?"
        }
        test_endpoint("POST", "/knowledge-graph/complex-query",
                     "Execute complex query",
                     json=complex_query)
    
    # ============= LLM SERVICE ENDPOINTS =============
    print_section("6. LLM SERVICE")
    
    llm_request = {
        "content": "A user has a profile with username and email. Users can create posts."
    }
    test_endpoint("POST", "/llm/generate-ontology",
                 "Generate ontology from text using LLM",
                 json=llm_request)
    
    # ============= CLEANUP =============
    print_section("7. CLEANUP OPERATIONS")
    
    # Delete transcript
    test_endpoint("DELETE", f"/transcripts/{transcript_id}",
                 "Delete transcript")
    
    # Clear knowledge graph
    test_endpoint("DELETE", "/knowledge-graph/clear",
                 "Clear knowledge graph")
    
    # Final status check
    test_endpoint("GET", "/system/status", "Final system status")
    
    # ============= SUMMARY =============
    print_section("TEST SUMMARY")
    print("\n✅ All API endpoints have been tested!")
    print("📊 Check the results above for any failures or errors.")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
