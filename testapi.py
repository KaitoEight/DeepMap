import requests
response = requests.post('http://localhost:8000/recommend', 
                        json={'lat': 10.869638, 'lon': 106.803820, 'radius': 1000})
print(response.json())