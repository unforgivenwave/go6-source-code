from typing     import Union
from re         import search
from time       import sleep
from websocket  import WebSocketApp
from json       import loads
from random     import choice

import httpx
    
@staticmethod
def handleRatelimit(js):
    retry_after = js["retry_after"]
    sleep(retry_after)

@staticmethod
def getPoonLink():
    return choice(httpx.get('https://pastebin.com/raw/8fgjDDnm').text.split("\n"))

@staticmethod
def extractCode(invite: str) -> Union[str, str]:
        code_regex = r"(?:(?:http:\/\/|https:\/\/)?discord\.gg\/|discordapp\.com\/invite\/|discord\.com\/invite\/)?([a-zA-Z0-9-]+)"
        match = search(code_regex, invite)
        if match:
                try:
                        return match.group(1)
                except:
                        return match.group(0)
        else:
                return None        

@staticmethod        
def getCaptchaKey(rqdata: str, site_key: str, proxy: str, cap_key: str, provider: str, useragent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'):   

    CAPMONSTER_API = 'https://api.capmonster.cloud'
    CAPSOLVER_API = 'https://api.capsolver.com'

    taskType = "HCaptchaTurboTask" if "capsolver.com" in provider else "HCaptchaTask"
    proxySolver = ":".join(proxy.replace("http://", "").split('@')[::-1])

    payload = {
        "clientKey": cap_key,
        "task": {
            "type": taskType,
            "websiteURL": "https://discord.com", 
            "websiteKey": site_key,
            "isInvisible": True,
            "userAgent": useragent,
            **({"enterprisePayload": {"rqdata": rqdata}} if "capsolver.com" in provider else {"data": rqdata}),
            **({"proxyAddress": proxySolver.split(":")[0], "proxyPort": proxySolver.split(":")[1], "proxyLogin": proxySolver.split(":")[2], "proxyPassword": proxySolver.split(":")[3]} if "capmonster.cloud" in provider else {"proxy": f"http:{proxySolver}"}),
        }
    } 
    api_url = CAPMONSTER_API if 'capmonster.cloud' in provider else CAPSOLVER_API

    with httpx.Client(headers={'content-type': 'application/json', 'accept': 'application/json'}, timeout=30) as client:
        task_id = client.post(f'{api_url}/createTask', json=payload).json().get('taskId')

        key = None
        while True:
            try:
                response = client.post(f'{api_url}/getTaskResult', json={'clientKey': cap_key, 'taskId': task_id}).json()
                if response['status'] == 'ready':
                    key = response['solution']['gRecaptchaResponse']
                    break
                elif response['status'] == 'idle' or response['status'] == 'processing':
                    sleep(1)
                elif response['status'] == 'failed':
                    return None
            except Exception as e:
                print(f'{str(e)}')
                return None
        return key

@staticmethod
class GetEphemeralEmbed(WebSocketApp):
    def __init__(self, token, bot_id, scoopedMessge):
        self.packets_recv = 0
        self.message: dict = {}
        self.bot_id = str(bot_id)
        self.token = token
        self.open = False
        self.create_id = None
        self.scoopedMessage = scoopedMessge

        self.socket_headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9013 Chrome/108.0.5359.215 Electron/22.3.2 Safari/537.36"
        }
        super().__init__(
            "wss://gateway.discord.gg/?encoding=json&v=9",
            header=self.socket_headers,
            on_open=lambda ws: self.sock_open(ws),
            on_message=lambda ws, msg: self.sock_message(ws, msg)
        )
        
    def run(self) -> dict:
        self.run_forever()
        self.open = True

        return self.message
    
    def sock_open(self, ws):
        self.send(
            '{"op":2,"d":{"token":"'
            + self.token
            + '","capabilities":125,"properties":{"os":"Windows","browser":"Firefox","device":"","system_locale":"it-IT","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0","browser_version":"94.0","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":103981,"client_event_source":null},"presence":{"status":"online","since":0,"activities":[],"afk":false},"compress":false,"client_state":{"guild_hashes":{},"highest_last_message_id":"0","read_state_version":0,"user_guild_settings_version":-1,"user_settings_version":-1}}}'
        )

    def sock_message(self, ws, message):
        decoded = loads(message)
        self.scoopedMessage.append(decoded)

        if "Verify yourself to gain access to the server" in str(decoded):
            self.message=decoded["d"]
            self.close()
        if "Please verify yourself to gain access to" in str(decoded):
            self.message=decoded["d"]
            self.close()         

    def sock_close(self, ws, close_code, close_msg):
        pass