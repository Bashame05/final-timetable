import requests
import json

data = {
    "teachers": [
        {"id": "T1", "name": "Dr. Smith", "available_slots": ["Mon_9", "Mon_10"], "subjects": ["OS"]},
    ],
    "subjects": [
        {"id": "OS", "name": "Operating Systems", "type": "theory", "duration": 2, "teachers": ["T1"]},
    ],
    "rooms": [
        {"id": "C301", "name": "Classroom 301", "type": "classroom", "available_slots": ["Mon_9", "Mon_10"]},
    ],
    "batches": [
        {"id": "B1", "name": "TY CSE A", "subjects": ["OS"]},
    ],
    "days": ["Mon"],
    "time_slots": ["9", "10", "11", "12", "1", "2", "3"],
}

response = requests.post("http://localhost:8000/api/timetable/generate", json=data)
result = response.json()

with open("test_output.txt", "w") as f:
    f.write(json.dumps(result, indent=2))

print("Result written to test_output.txt")
print(f"Status: {result.get('status')}")
