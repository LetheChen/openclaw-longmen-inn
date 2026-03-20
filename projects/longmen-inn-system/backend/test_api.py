#!/usr/bin/env python3
import requests

def test_api():
    url = 'http://localhost:8000/api/v1/agents/'
    print(f"Testing: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Agent数量: {len(data)}")
            for agent in data:
                print(f"  - {agent['name']} ({agent['agent_id']}): {agent['status']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
