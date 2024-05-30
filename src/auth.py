import requests
import json
import hashlib
import psutil
import os
import base64
import jwt
import platform
import wmi
import socket

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding

class Auth:
    def __init__(self,key: str, version: str) -> None:
        self.key = key
        self.hwid = self.get_hwid()
        self.version = version
        self.server_url = 'http://auth.go6.lol:4444'

    def get_hwid(self):
        hwid_data = {
            "main_info": {
                "CPU": platform.processor(),
                "RAM": psutil.virtual_memory().total,
                "BIOS": list(filter(lambda x: len(x) > 0, os.popen("wmic bios get serialnumber").read().split("\n")))[1].strip(),
                "CORES": psutil.cpu_count(logical=False),
                "HWID": wmi.WMI().Win32_ComputerSystemProduct()[0].UUID,
            },
            "host_info": {
                "USERNAME": os.environ["COMPUTERNAME"],
                "HOSTNAME": socket.gethostname(),
                "IP_ADDRESS": socket.gethostbyname(socket.gethostname()),
            },
            "os_info": {
                "OS": platform.system(),
                "OS_VERSION": platform.version(),
                "OS_ARCHITECTURE": platform.architecture()
            }
        }
        return hashlib.sha256(str(hwid_data).encode()).hexdigest()
    
    def generate_hash(self,data,sk):
        return hashlib.sha256((data + sk).encode()).hexdigest()
    
    def verify_jwt(self, token,sk):
        try:
            return jwt.decode(token, sk, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        return None
            
    def encrypt_data(self,data,pk):
        encrypted_data = pk.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_data.hex()     

    def authenticate(self,):
        try:
            #
            response = requests.get(f'{self.server_url}/verify_version', json={'data': self.version}) # 1
            result = response.json()
            #
            if result['success']:
                print(result['message'])
            elif response.status_code == 400:
                print(result['message'])
                new_version = result['link']
                os.system(f"start {new_version}")
                os._exit(1)
                while True:
                    print('tampered data') 
            else:
                print(result['message'])
                os._exit(1)
                while True:
                    print('tampered data')  
        except requests.exceptions.RequestException:
            print('server slow or down')
            os._exit(1)
            while True:
                print('tampered data')             
        except Exception:
            print(response.content)
            os._exit(1)
            while True:
                print('tampered data')

        try:
            #
            response = requests.get(f'{self.server_url}/get_session_key',json={'data': base64.b64encode(self.key.encode()).decode()}) # 2
            result = response.json()
            #
            if result['success']:
                print(result['message'])
                session_key = result['session_key']        
            else:
                print(result['message'])
                os._exit(1)
                while True:
                    print('tampered data')              
        except Exception:
            print(response.content)
            os._exit(1)
            while True:
                print('tampered data')   

        try:
            #
            response = requests.get(f'{self.server_url}/get_public_key', json={'session_key': session_key}) # 3
            result = response.json()
            #
            if result['success']:
                print(result['message'])
                public_key = result['public_key']    
            else:
                print(result['message'])
                os._exit(1)
                while True:
                    print('tampered data')       
        except Exception:
            print(response.content)
            os._exit(1)
            while True:
                print('tampered data')

        data = {'key': self.key, 'hwid': self.hwid}
        data['signature'] = self.generate_hash(self.key + self.hwid, session_key)
        server_public_key = serialization.load_pem_public_key(public_key.encode(), backend=default_backend())
        encrypted_data = self.encrypt_data(json.dumps(data), server_public_key)

        try:
            #
            response = requests.post(f'{self.server_url}/authenticate', json={'data': encrypted_data, 'session_key': session_key}) # 4
            result = response.json()
            #
            if result['success']:
                print(result['message'])
                decoded_token = self.verify_jwt(result['token'],session_key)
                if decoded_token:
                    decoded_key = decoded_token['key']
                    decoded_expiry = decoded_token['key_expiry']
                    decoded_code = decoded_token['recovery_code']
                    if decoded_token['key'] == self.key and decoded_token['hwid'] == self.hwid and decoded_token['session_key'] == session_key and data['signature'] == result['signature']:
                        #
                        response = requests.post(f'{self.server_url}/verify_integrity', json={'data': result, 'session_key': session_key}) # 5
                        result = response.json()
                        #
                        if result['success']:
                            print(result['message'])
                            decoded_token = self.verify_jwt(result['token'],session_key)
                            if decoded_token:
                                if decoded_token['session_key'] == session_key:
                                        #return True  
                                        return decoded_key,decoded_expiry,decoded_code
                                else:
                                    print(result['message'])
                                    os._exit(1)
                                    while True:
                                        print('tampered data')    
                            else:
                                print(result['message'])
                                os._exit(1)
                                while True:
                                    print('tampered data')            
                        else:
                            print(result['message'])
                            os._exit(1)
                            while True:
                                print('tampered data')
                    else:
                        print(result['message'])
                        os._exit(1)
                        while True:
                            print('tampered data')     
                else:
                    print(result['message'])
                    os._exit(1)
                    while True:
                        print('tampered data')      
            else:
                print(result['message'])
                os._exit(1)
                while True:
                    print('tampered data')
        except Exception:
            print(response.content)
            os._exit(1)
            while True:
                print('tampered data')