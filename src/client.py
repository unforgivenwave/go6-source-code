import requests, re, base64, json, tls_client

class application:

    @staticmethod
    def native_build() -> int:
        return int(requests.get(
            "https://updates.discord.com/distributions/app/manifests/latest",
            params={
                "install_id":'0',
                "channel":"stable",
                "platform":"win",
                "arch":"x86"
            },
            headers={
                "user-agent": "Discord-Updater/1",
                "accept-encoding": "gzip"
        }).json()["metadata_version"])

    @staticmethod
    def client_build() -> int:
        page = requests.get("https://discord.com/app").text.split("app-mount")[1]
        assets = re.findall(r'src="/assets/([^"]+)"', page)[::-1]

        for asset in assets:
            js=requests.get(f"https://discord.com/assets/{asset}").text
            
            if "buildNumber:" in js:
                return int(js.split('buildNumber:"')[1].split('"')[0])

    @staticmethod
    def main_version() -> str:
        app=requests.get(
            "https://discord.com/api/downloads/distributions/app/installers/latest",
            params={
                "channel":"stable",
                "platform":"win",
                "arch":"x86"
            },
            allow_redirects=False
        ).text

        return re.search(r'x86/(.*?)/', app).group(1)


class client:
    def __init__(self):
        #os.system("cls")

        self.native_build=application.native_build()
        self.main_version=application.main_version()
        self.client_build=application.client_build()
        print(self.native_build)
        print(self.main_version)
        print(self.client_build)

        self.chrome="108.0.5359.215"
        self.electron="22.3.26"
        self.safari="537.36"
        self.os_version="10.0.19045"

    def xprops(self):
        return base64.b64encode(json.dumps({
            "os":"Windows",
            "browser":"Discord Client",
            "release_channel":"stable",
            "client_version":self.main_version,
            "os_version":self.os_version,
            "os_arch":"x64",
            "app_arch":"ia32",
            "system_locale":"en",
            "browser_user_agent":self.useragent,
            "browser_version":self.electron,
            "client_build_number":self.client_build,
            "native_build_number":self.native_build,
            "client_event_source":None,
            "design_id":0
        }).encode()).decode()

    def get_session(self, token:str=None, proxy:str=None):
        session=tls_client.Session(
            client_identifier=f"chrome_108",
            random_tls_extension_order=True
        )
        if proxy:
                session.proxies=proxy
                session.timeout_seconds=700//1000  

        self.useragent=f"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/{self.safari} (KHTML, like Gecko) discord/{self.main_version} Chrome/{self.chrome} Electron/{self.electron} Safari/{self.safari}"

        session.headers = {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'en,en-US;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.useragent,
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'Europe/Stockholm',
            'x-super-properties': self.xprops()
        }

        if token:
            session.headers["Authorization"]=token

        try:
            session.cookies=session.get("https://discord.com").cookies
        except Exception as e:
            print(e)   
  
        return session
    
