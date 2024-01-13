import asyncio
import requests

async def mintNFT():
    number = input("Teddy Bear #: ")
    owner = input("Your name: ")

    url = "https://api.verbwire.com/v1/nft/mint/quickMintFromMetadata"

    payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"chain\"\r\n\r\ngoerli\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\nTeddy Bear #{number}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"description\"\r\n\r\nOwner: {owner}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"imageUrl\"\r\n\r\nhttps://i.ebayimg.com/images/g/vlIAAOSwikBcR0nA/s-l1200.jpg\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"data\"\r\n\r\nhttps://i.ebayimg.com/images/g/vlIAAOSwikBcR0nA/s-l1200.jpg\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"recipientAddress\"\r\n\r\n0x0E5d299236647563649526cfa25c39d6848101f5\r\n-----011000010111000001101001--\r\n\r\n"
    headers = {
        "accept": "application/json",
        "content-type": "multipart/form-data; boundary=---011000010111000001101001",
        "X-API-Key": "sk_live_5b963604-629c-4156-ac69-433d1db6f108"
    }


    print("Minting your personal Teddy Bear NFT")

    response = requests.post(url, data=payload, headers=headers)

    print(response.text)

    print("Mint success!")

asyncio.run(mintNFT())