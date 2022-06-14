from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm
import json 

credential = DefaultAzureCredential()
key_client = KeyClient(vault_url="https://AzureKeyValut123.vault.azure.net/", credential=credential)

key = key_client.get_key("SampleKeyValut")
#print(key)
crypto_client = CryptographyClient(key, credential=credential)
#print(crypto_client)

f = open("D:/11111.txt", "r", encoding="utf-8")
original = json.load(f)
#print(original)
data = bytes(original['rawText'], 'utf-8')

encrypt = crypto_client.encrypt(EncryptionAlgorithm.rsa_oaep, data)
encrypted_data = encrypt.ciphertext
print(encrypted_data)

with open ('encrypted_data.txt','wb') as encrypted_file:
    encrypted_file.write(encrypted_data)
    
decrypt = crypto_client.decrypt(EncryptionAlgorithm.rsa_oaep, encrypted_data)
print(decrypt.plaintext)

with open ('decrypted_data.txt','wb') as encrypted_file:
    encrypted_file.write(decrypt.plaintext)


