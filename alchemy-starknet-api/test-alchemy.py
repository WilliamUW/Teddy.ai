import requests

url = "https://starknet-mainnet.g.alchemy.com/v2/eucheJf7r_lvnEZbEJ3dmtKRqn"

payload = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "starknet_estimateFee"
}
headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)