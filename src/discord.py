from wsgiref.headers import Headers
from .client     import client
from .utils      import GetEphemeralEmbed

from tls_client     import response
from typing         import Union
from re             import search
from base64         import b64encode
from json           import dumps
from random         import sample,choice
from string         import ascii_lowercase,digits 
from urllib.parse   import quote
from time           import time, sleep
from decimal        import Decimal
from json           import loads
from websocket      import create_connection

import httpx
import threading

builder=client()

class Discord():
    def __init__(self, proxy, token) -> None:
        if proxy:
            self.proxy = f'http://{proxy}'
        else: self.proxy = None    
        if token:
            self.token = token
        else: self.token = None  
        self.session=builder.get_session(self.token,self.proxy)

    @staticmethod
    def getClientInfo():
        return builder.client_build, builder.main_version, builder.native_build

    @staticmethod
    def getContextProperties(invite: str) -> Union[str, str]:
        req = httpx.get(
                f"https://discord.com/api/v9/invites/{invite}?with_counts=true&with_expiration=true"
            )
        req = req.json()
        g = req["guild"]["id"]
        c = req["channel"]["id"]
        t = req["channel"]["type"]

        return g, b64encode(dumps({"location":"Accept Invite Page","location_guild_id":g,"location_channel_id":c,"location_channel_type":int(t)}).encode()).decode()    

    def check(self) -> Union[bool, response.Response]:

        req = self.session.get("https://discord.com/api/v9/users/@me/settings",)
        return req.status_code == 200, req

    def checkConnection(self) -> Union[bool, response.Response]:
        with httpx.Client(proxies=self.proxy, headers={'user-agent': self.session.headers['user-agent']}) as client:
            req = client.get("https://api.ipify.org",)
        return req.status_code == 200, req

    def join(self, invite: str, context: str, rqtoken: str, captcha: str) -> Union[bool, response.Response]:

        self.session.headers.update({"x-context-properties": context})
        self.session.headers.update({"referer": "https://discord.com/invite/"+invite})
        if captcha:
            self.session.headers.update({"x-captcha-key": captcha})
            self.session.headers.update({"x-captcha-rqtoken": rqtoken})
        js = {
            "session_id": (''.join(sample(ascii_lowercase+digits,32))),
        }

        req = self.session.post(f"https://discord.com/api/v9/invites/{invite}", json=js, )
        return req.status_code == 200, req    

    def leave(self, guildID: str) -> Union[bool, response.Response]:

        js = {
            "lurking": False
        }

        req = self.session.delete("https://discord.com/api/v9/users/@me/guilds/"+guildID, json=js)
        return req.status_code == 204, req
    
    def friend(self, userID: str) -> Union[bool, response.Response]:

        req = self.session.put("https://discord.com/api/v9/users/@me/relationships/"+userID,json={})
        return req.status_code == 204, req

    def checkGuild(self, guildID: str) -> Union[bool, response.Response]:

        req = self.session.get(f"https://discord.com/api/v9/guilds/{guildID}",)
        return req.status_code == 200, req   

    def reaction(self, messageID: str, channelID: str, emoji: str) -> Union[bool, response.Response]:
        
        req = self.session.put(f"https://discord.com/api/v9/channels/{channelID}/messages/{messageID}/reactions/{quote(emoji)}/%40me?locat13on=Message&burst=false",)
        return req.status_code == 204, req

    def sendMessage(self, channelID: str, message: str, stickerID: str = None) -> Union[bool, response.Response]:
        js = {
            "content": message, 
            "tts": "false"
        }

        if stickerID:
            js['sticker_ids']=[stickerID]

        req = self.session.post(f"https://discord.com/api/v9/channels/{channelID}/messages", json=js)
        return req.status_code == 200, req

    def getButton(self, channelID: str, token: str):

        req = self.session.get(f"https://discord.com/api/v9/channels/{channelID}/messages?limit=50")
        js = req.json()

        if req.status_code == 200:
            for i in js:
                if i.get("components"):
                    message_id = i["id"]
                    flags = i["flags"]
                    application_id = i["author"]["id"]

                    for component_group in i["components"]:
                        for component in component_group.get("components", []):
                            custom_id = component["custom_id"]
                            typee = component["type"]
                            options = component.get("options", None)
                            return application_id, typee, custom_id, flags, message_id, options

        return    

    def button(self, application_id: str, typee: str, custom_id: str, flags: str, message_id: str, opt: str, channelID: str, guildID: str, value: str) -> Union[bool, response.Response]:
        sessionID = (''.join(sample(ascii_lowercase+digits,32)))

        js = {
            "application_id": application_id,
            "channel_id": channelID,
            "data": {
                "component_type": typee,
                "custom_id": custom_id,
            },
            "guild_id": guildID,
            "message_flags": flags,
            "message_id": message_id,
            "nonce": ((int(time()) * 1000) - 1420070400000) * 4194304,
            "type": 3,
            "session_id": sessionID,
        }
        
        if value:
            js["data"]["values"] = [value]      

        self.session.headers.update({"referer": "https://discord.com/channels/" + guildID + "/" + channelID})

        req = self.session.post("https://discord.com/api/v9/interactions", json=js)

        return req.status_code == 204, req

    def acceptRules(self, invite: str, guildID: str) -> Union[bool, response.Response]:
        req = self.session.get(f"https://discord.com/api/v9/guilds/{guildID}/member-verification?with_guild=false&invite_code="+invite,)
        js = req.json()
        payload = js
        if payload.get("form_fields") == None:
            return False, req

        for i in range(len(payload["form_fields"])):
            payload["form_fields"][i]["response"] = "true"

        req = self.session.put(f"https://discord.com/api/v9/guilds/{guildID}/requests/@me", json=payload)
        return req.status_code == 201, req  

    def acceptOnBoarding(self, guildID: str) -> Union[bool, response.Response]:
            class OnboardingInfo:
                guild_id: int = 0
                required_prompts: list[dict[str, Union[str, list[Union[str, dict, list, bool, None]]]]] = []
                onboarding_prompts_seen: dict[str, int] = {}
                onboarding_responses_seen: dict[str, int] = {}
                onboarding_responses: list[str] = []

            req=False
            while not req:
                req = self.session.get(f"https://discord.com/api/v9/guilds/{guildID}/onboarding",)

                if req.status_code == 200:
                    break
                else:
                    sleep(1)

            req = req.json()

            updated_prompts = []
            try:
                for prompt in req["prompts"]:
                    if prompt["required"]:
                        updated_prompts.append(prompt)
            except Exception as e:
                return False, None    

            try:
                req["prompts"] = updated_prompts
                for prompt in req["prompts"]:
                    OnboardingInfo.onboarding_prompts_seen[str(prompt["id"])] = 1681404058976
                for prompt in req["prompts"]:
                    for option in prompt["options"]:
                        OnboardingInfo.onboarding_responses_seen[str(option["id"])] = 1681404058976

                for prompt in req["prompts"]:
                    OnboardingInfo.onboarding_responses.append(choice(prompt["options"])["id"])
            except Exception as e:
                return False, None         

            self.session.headers.update({"content-type": "application/json"})
            self.session.headers.update({"referer": f"https://discord.com/channels/{guildID}/onboarding"})

            js = {
                "onboarding_prompts_seen": OnboardingInfo.onboarding_prompts_seen,
                "onboarding_responses": OnboardingInfo.onboarding_responses,
                "onboarding_responses_seen": OnboardingInfo.onboarding_responses_seen,
                "update_roles_and_channels": True,
            }

            req = self.session.post(f"https://discord.com/api/v9/guilds/{guildID}/onboarding-responses", json=js)
            return req.status_code == 200, req

    def acceptDoubleCounter(self, channelID: str) -> Union[bool, response.Response]:
        
        self.session.headers.update({"referer": f"https://discord.com/channels/@me/" + channelID})
        req = self.session.get(f"https://discord.com/api/v9/channels/{channelID}/messages", params={"limit":1})

        js = req.json()

        link = js[0]["embeds"][0]["fields"][1]["value"].split("(")[1].split(")")[0]
        sleep(2)

        headersDoubleCounter = {
            "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            "Accept-Encoding": 'gzip, deflate, br',
            "Accept-Language": 'en-US,en;q=0.9',
            "Cache-Control": 'max-age=0',
            "Connection": 'keep-alive',
            "Host": 'verify.dcounter.space',
            "sec-ch-ua": '"Chromium";v="95", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": '?0',
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": 'document',
            "Sec-Fetch-Mode": 'navigate',
            "Sec-Fetch-Site": 'cross-site',
            "Sec-Fetch-User": '?1',
            "Upgrade-Insecure-Requests": '1',
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4624.0 Safari/537.36',
        }

        with httpx.Client(proxies=self.proxy, headers=headersDoubleCounter) as client:
            req = client.get(link)
        return req.status_code == 200,req.text#, req,  

    def acceptSledgeHammer(self, authorID: str, channelID: str, messageID: str, guildID: str) -> Union[bool, response.Response]:
        scoopedMessages = []

        t = GetEphemeralEmbed(self.token, authorID, scoopedMessages)                
        thread = threading.Thread(target=t.run)
        thread.start() 

        button = authorID, 2, 'startVerification.en', 0, messageID, None

        self.button(*button, channelID, guildID, value=None)     

        while not t.open:
                sleep(0.1)

        try:
                msgID=t.message["id"]
                customID=t.message["components"][0]["components"][0]["custom_id"]
                options=t.message["components"][0]["components"][0]["options"] 
                desc=t.message["embeds"][0]["description"]
        except Exception as e:
                return False, None 
        
        t.close()
        thread.join()

        object=(search(r'select the (.*?) on the',desc).group(1)[2:][:-2]).lower()

        if " " in object:
            words = object.split()
            object=''.join([words[0]]+[word.capitalize() for word in words[1:]])

        for option in t.message["components"][0]["components"][0]["options"]:
            value=option["value"]

            if value==object:
                button = authorID, 3, customID, 64, msgID, options
                st, resp = self.button(*button, channelID, guildID, value=value) 
                return st, resp

    def acceptRestoreCord(self, guildID: str, clientID: str, url: str = None) -> Union[bool, response.Response]:
        req = self.session.post('https://discord.com/api/v9/oauth2/authorize',
            params={
                'client_id': clientID,
                'response_type': 'code',
                'redirect_uri': 'https://restorecord.com/api/callback',
                'scope': 'identify guilds.join',
                'state': guildID
            },
            json={
                'permissions': '0',
                'authorize': True
            },
        ).json()

        del self.session.headers["Authorization"]
        url= req["location"]
        code = search(r'code=(.*?)&',url).group(1)

        req = self.session.get('https://restorecord.com/api/callback', params={
            'code': code,
            'state': guildID
        })
        return req.status_code == 307, req 

    def findIDs(self, guildID: str, author: str, description: str):
        st, chIds = self.getAllChannels(guildID)
        if st:
                for channelIDtoScrape in chIds:
                        st, resp = self.getMessages(channelIDtoScrape)
                        if st:
                                messagescraped = resp.json()
                                for message in messagescraped:
                                    username = message['author']['username']
                                    embeds = message['embeds']
                                    aid= message['author']['id']
                                    for embed in embeds:       
                                        if author and description and 'description' in embed and description in embed['description'] and username == author:
                                            mid, cid = message['id'], message['channel_id']
                                            break
        return cid, mid, aid                        

    def getClientID(self, url: str, serverID: str) -> Union[bool, response.Response]:
        clientID = None

        with httpx.Client(proxies=self.proxy, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}) as client:
            req = client.get(url+serverID)
        match = search(r'clientId":"(.*?)"', req.text)
        if match:
            clientID = match.group(1)
            if not clientID.isdigit():
                clientID = None
        return clientID
    
    # # temp
    # def createTag(self, guildID: str, channelID: str, tagName: str, message: str):
    #     nonce=str(round(Decimal(time()*1000-1420070400000)*4194304))
        
    #     data = '''------WebKitFormBoundaryL7DeY24O29SiWVGO\r\nContent-Disposition: form-data; name="payload_json"\r\n\r\n{"type":2,"application_id":"161660517914509312","guild_id":"GUILD_ID_HERE","channel_id":"CHANNEL_ID_HERE","session_id":"SESSION_ID_HERE","data":{"version":"1116144106687692895","id":"824701594749763611","name":"tag","type":1,"options":[{"type":1,"name":"create","options":[{"type":3,"name":"name","value":"NAME_HERE"},{"type":3,"name":"content","value":"MESSAGE_HERE"}]}],"application_command":{"id":"824701594749763611","application_id":"161660517914509312","version":"1116144106687692895","default_member_permissions":null,"type":1,"nsfw":false,"name":"tag","description":"Get or create a tag","dm_permission":false,"contexts":null,"options":[{"type":1,"name":"raw","description":"Get the raw tag for use copying/editing.","options":[{"type":3,"name":"name","description":"Tag name","required":true,"autocomplete":true},{"type":3,"name":"category","description":"Tag category","autocomplete":true}]},{"type":1,"name":"get","description":"Get a tag","options":[{"type":3,"name":"name","description":"Tag name","required":true,"autocomplete":true},{"type":3,"name":"category","description":"Tag category","autocomplete":true}]},{"type":1,"name":"edit","description":"Edit a tag","options":[{"type":3,"name":"name","description":"Tag name","required":true,"autocomplete":true},{"type":3,"name":"content","description":"Tag content","required":true},{"type":3,"name":"category","description":"Tag category","autocomplete":true}]},{"type":1,"name":"delete","description":"Delete a tag","options":[{"type":3,"name":"name","description":"Tag name","required":true,"autocomplete":true},{"type":3,"name":"category","description":"Tag category","autocomplete":true}]},{"type":1,"name":"create","description":"Create a tag","options":[{"type":3,"name":"name","description":"Tag name","required":true,"autocomplete":true},{"type":3,"name":"content","description":"Tag content","required":true},{"type":3,"name":"category","description":"Tag category","autocomplete":true}]},{"type":1,"name":"category","description":"Creates a tag category","options":[{"type":3,"name":"category","description":"Category name","required":true}]},{"type":1,"name":"categories","description":"Creates a tag category"},{"type":1,"name":"delcat","description":"Deletes a tag category","options":[{"type":3,"name":"category","description":"Category name","required":true,"autocomplete":true}]}]},"attachments":[]},"nonce":"NONCE_HERE"}\r\n------WebKitFormBoundaryL7DeY24O29SiWVGO--\r\n
    #     '''[:-1].replace("GUILD_ID_HERE",guildID).replace("CHANNEL_ID_HERE",channelID).replace("SESSION_ID_HERE",(''.join(sample(ascii_lowercase+digits,32)))).replace("NAME_HERE", tagName).replace("MESSAGE_HERE",message).replace("NONCE_HERE",nonce)

    #     with httpx.Client(proxies=self.proxy) as client:
    #         req = client.post('https://discord.com/api/v9/interactions', data=data, headers={"content-type":"multipart/form-data; boundary=----WebKitFormBoundaryL7DeY24O29SiWVGO","authorization":self.token})
    #     return req.status_code == 204, req
    
    # def postTag(self, guildID: str, channelID: str, tagName: str):
    #     nonce=str(round(Decimal(time()*1000-1420070400000)*4194304))

    #     data = '''------WebKitFormBoundarySI8fFeBrINpG6IbB\r\nContent-Disposition: form-data; name="payload_json"\r\n\r\n{"type":2,"application_id":"161660517914509312","guild_id":"GUILD_ID_HERE","channel_id":"CHANNEL_ID_HERE","session_id":"SESSION_ID_HERE","data":{"version":"1116144106687692895","id":"824701594749763611","name":"tag","type":1,"options":[{"type":1,"name":"raw","options":[{"type":3,"name":"name","value":"NAME_HERE"}]}],"application_command":{"id":"824701594749763611","application_id":"161660517914509312","version":"1116144106687692895","default_member_permissions":null,"type":1,"nsfw":false,"name":"tag","description":"Get or create a tag","dm_permission":false,"contexts":null,"options":[{"type":1,"name":"raw","description":"Get the raw tag for use copying/editing.","options":[{"type":3,"name":"name","description":"Tag name","required":true,"autocomplete":true},{"type":3,"name":"category","description":"Tag category","autocomplete":true}]},{"type":1,"name":"get","description":"Get a tag","options":[{"type":3,"name":"name","description":"Tag name","required":true,"autocomplete":true},{"type":3,"name":"category","description":"Tag category","autocomplete":true}]},{"type":1,"name":"edit","description":"Edit a tag","options":[{"type":3,"name":"name","description":"Tag name","required":true,"autocomplete":true},{"type":3,"name":"content","description":"Tag content","required":true},{"type":3,"name":"category","description":"Tag category","autocomplete":true}]},{"type":1,"name":"delete","description":"Delete a tag","options":[{"type":3,"name":"name","description":"Tag name","required":true,"autocomplete":true},{"type":3,"name":"category","description":"Tag category","autocomplete":true}]},{"type":1,"name":"create","description":"Create a tag","options":[{"type":3,"name":"name","description":"Tag name","required":true,"autocomplete":true},{"type":3,"name":"content","description":"Tag content","required":true},{"type":3,"name":"category","description":"Tag category","autocomplete":true}]},{"type":1,"name":"category","description":"Creates a tag category","options":[{"type":3,"name":"category","description":"Category name","required":true}]},{"type":1,"name":"categories","description":"Creates a tag category"},{"type":1,"name":"delcat","description":"Deletes a tag category","options":[{"type":3,"name":"category","description":"Category name","required":true,"autocomplete":true}]}]},"attachments":[]},"nonce":"NONCE_HERE"}\r\n------WebKitFormBoundarySI8fFeBrINpG6IbB--\r\n
    #     '''[:-1].replace("GUILD_ID_HERE",guildID).replace("CHANNEL_ID_HERE",channelID).replace("SESSION_ID_HERE",(''.join(sample(ascii_lowercase+digits,32)))).replace("NAME_HERE",tagName).replace("NONCE_HERE",nonce)

    #     with httpx.Client(proxies=self.proxy) as client:
    #         req = client.post('https://discord.com/api/v9/interactions', data=data, headers={"content-type":"multipart/form-data; boundary=----WebKitFormBoundarySI8fFeBrINpG6IbB", "authorization":self.token})
    #     return req.status_code == 204, req
    # #

    def threads(self, channelID: str,guildID: str, title: str,forum:bool) -> Union[bool, response.Response]:
        
        self.session.headers.update({"referer": "https://discord.com/channels/" + guildID + "/" + channelID})

        js = {
            "applied_tags": [],
            "auto_archive_duration": 4320,
            "name": title,
            "type": 11,
        }

        if forum:
            js["message"] = {'content': title}

        req = self.session.post(f"https://discord.com/api/v9/channels/{channelID}/threads", json=js)

        return req.status_code == 201, req

    def createDM(self, userID: str,) -> Union[bool, response.Response]:
        
        js = {
            "recipients": [
                userID
            ]
        }
        req = self.session.post("https://discord.com/api/v9/users/@me/channels", json=js)

        return req.status_code == 200, req

    def sendDM(self, channelID: str, message: str, rqtoken: str, captcha: str) -> Union[bool, response.Response]:

        self.session.headers.update({"referer": "https://discord.com/channels/@me/" + channelID})
        
        if captcha is not None:
            self.session.headers.update({"x-captcha-key": captcha})
            self.session.headers.update({"x-captcha-rqtoken": rqtoken})
            sleep(0.1)

        js = {
            "content": message,
            "mobile_network_type": "unknown",
            "nonce": ((int(time()) * 1000) - 1420070400000) * 4194304,
            "tts": False
        }

        req = self.session.post(f"https://discord.com/api/v9/channels/{channelID}/messages", json=js)
        return req.status_code == 200, req  

    def nickname(self, guildID: str, nickname: str) -> Union[bool, response.Response]:
        
        payload = {"nick": nickname}

        req = self.session.patch(f"https://discord.com/api/v9/guilds/{guildID}/members/@me", json=payload)
        return req.status_code == 200, req 

    def sendContent(self, webhook: str, message: str):

        js = {
            "content": message
        }
        with httpx.Client(proxies=self.proxy, headers={'user-agent': self.session.headers["user-agent"]}) as client:
            req = client.post(webhook, json=js)
        return req.status_code == 204, req 
    
    def deleteUrl(self, webhook: str):

        with httpx.Client(proxies=self.proxy, headers={'user-agent': self.session.headers["user-agent"]}) as client:
            req = client.delete(webhook)
        return req.status_code == 404, req

    def changeDisplayName(self, name: str) -> Union[bool, response.Response]:

        js = {
            "global_name": name
        }

        req = self.session.patch(f"https://discord.com/api/v9/users/@me", json=js,)
        return req.status_code == 200, req
    
    def changePronouns(self, pronouns: str) -> Union[bool, response.Response]:
        
        js = {
            "pronouns": pronouns
        }

        req = self.session.patch(f"https://discord.com/api/v9/users/@me", json=js,)
        return req.status_code == 200, req

    def changeBio(self, bio: str) -> Union[bool, response.Response]:
        
        js = {
            "bio": bio
        }

        req = self.session.patch(f"https://discord.com/api/v9/users/@me", json=js,)
        return req.status_code == 200, req  
    
    def changeAvatar(self, pfp: bytes) -> Union[bool, response.Response]:

        data = b64encode(pfp)
        
        js = {
            "avatar": f"data:image/png;base64,{(data.decode('utf-8'))}"
        }
        
        req = self.session.patch("https://discord.com/api/v9/users/@me", json=js)
        return req.status_code == 200, req
    
    def scrapeStickers(self,) -> Union[bool, response.Response]:
        req = self.session.get("https://discord.com/api/v9/sticker-packs")

        ids = [sticker['id'] for sticker in loads(req.text)['sticker_packs'][0]['stickers']]
        return ids

    #
    def _connect_and_authenticate(self):
            ws = create_connection("wss://gateway.discord.gg/?v=8&encoding=json")
            hello = loads(ws.recv())
            heartbeat_interval = hello['d']['heartbeat_interval']
            ws.send(dumps({"op": 2, "d": {"token": self.token, "properties": {"$os": "windows", "$browser": "Discord", "$device": "desktop"}}}))
            return ws

    def _send_payload(self, ws, op, data):
        ws.send(dumps({"op": op, "d": data}))

    def _close_connection(self, ws):
        ws.close()

    def voiceExecute(self, channelID, guildID, mute, deaf, stream, video, close):
        ws = self._connect_and_authenticate()
        self._send_payload(ws, 4, {"guild_id": guildID, "channel_id": channelID, "self_mute": mute, "self_deaf": deaf, "self_stream?": stream, "self_video": video})
        self._send_payload(ws, 18, {"type": "guild", "guild_id": guildID, "channel_id": channelID, "preferred_region": "singapore"})
        if close:
            self._send_payload(ws, 1, None)
            self._close_connection(ws)
        sleep(0.3) 
        return True   
    #    