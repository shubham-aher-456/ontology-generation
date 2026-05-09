#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def test_upload():
    """Test just the upload functionality"""
    with open("complex_transcript.txt", "rb") as f:
        files = {"file": ("complex_transcript.txt", f, "text/plain")}
        data = {
            "title": "AI Healthcare System Discussion",
            "description": "Complex transcript about AI-powered healthcare architecture"
        }
        response = requests.post(f"{BASE_URL}/transcripts/upload", files=files, data=data)
    
    print(f"Upload Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        return result.get("transcript_id")
    return None

if __name__ == "__main__":
    transcript_id = test_upload()
    if transcript_id:
        print(f"Success! Transcript ID: {transcript_id}")
    else:
        print("Upload failed")