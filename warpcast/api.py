import requests

warp_api = "http://127.0.0.1:2281"


esponse = requests.get(f"{warp_api}/v1/")

if response.status_code == 200:
    response_data = response.json()
    print(response_data)
else:
    print(f"Error: {response.status_code}, {response.text}")