import base64
import os
import json
from time import sleep
import sys
import itertools
import threading
import random
import string
import re
import bs4
from unidecode import unidecode
from win10toast import ToastNotifier
from time import time

from src.auth import Auth
from src.console import Console
from src.discord import Discord
from src.scraper import DiscordSocket
from src.utils import *
from src.gui import *
from src.guilogin import DraggableLoginWindow

VERSION = "4.1.0"

class Go6(Ui_MainWindow):
    def __init__(self, window) -> None:
        super().__init__()
        self.cns = Console()
        self.DATA_DICT = f"data/"
        self.ASSETS_DICT = f"assets/"
        self.TOKENS_DICT = f"{self.DATA_DICT}tokens.txt"
        self.PROXIES_DICT = f"{self.DATA_DICT}proxies.txt"
        self.CONFIG_DICT = f"{self.DATA_DICT}config.json"
        self.PFP_DICT = f"{self.DATA_DICT}pfp/"
        self.SCRAPED_DICT = f"{self.DATA_DICT}scraped/"
        self.AUTHBIN_DICT = f"authbin.txt"

       # create files
        for directory in [self.DATA_DICT, self.PFP_DICT, self.SCRAPED_DICT]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f'Created {directory}')
        for filen, content in [(self.TOKENS_DICT, ''), (self.PROXIES_DICT, ''), (self.AUTHBIN_DICT, ''), (self.CONFIG_DICT, {})]:
            file_path = os.path.join(os.getcwd(), filen)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as file: #where is auth
                    if content:
                        file.write(content)
                    elif filen == self.CONFIG_DICT:
                        file.write(json.dumps({"user_key": "", "captcha_key": "", "provider": ""}, indent=4))
                    print(f'Created {filen}')          

        # check files
        with open(self.CONFIG_DICT, "r") as f:
            data = json.loads(f.read())
            user_key = data["user_key"]
            if not user_key:
                threading.Thread(target=ToastNotifier().show_toast, args=("Invalid config | Go6","Please input key to continue",f"{self.ASSETS_DICT}go6icon.ico",7)).start()
                print('Invalid config')
                runLoginPage()
            # auth
            # key,expiry,code= Auth(
            #     user_key,
            #     VERSION
            # ).authenticate()
            key, expiry, code = "1", "1", "1"
            with open(self.AUTHBIN_DICT, 'w') as f:
                f.write(f"""KEY : {key}\nEXPIRY : {expiry}\nCODE : {code}""")

            self.solveCaptcha = False
            if len(data['captcha_key']) in (32, 36) and data["provider"] in ["capmonster.cloud", "capsolver.com"]:
                self.solveCaptcha = True
                self.capkey, self.provider = data['captcha_key'], data['provider']              
        with open(self.TOKENS_DICT, 'r') as f:
            self.tokens = f.read().splitlines()
            if self.tokens == []:
                print('Invalid config')
                threading.Thread(target=ToastNotifier().show_toast, args=("Invalid config | Go6","Please input tokens to continue",f"{self.ASSETS_DICT}go6icon.ico",7)).start()
                os.startfile(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), self.TOKENS_DICT))
                last_mod = os.path.getmtime(self.TOKENS_DICT)
                while True:
                    sleep(1)
                    if os.path.getmtime(self.TOKENS_DICT) != last_mod:
                        break
                runMainPage()    
                
        self.useProxy = False
        with open(f"{self.DATA_DICT}/proxies.txt", "r") as f:
            data = f.read().splitlines()
            if not data == []: 
                if ":" not in "".join(data):
                        print('Invalid config')
                        threading.Thread(target=ToastNotifier().show_toast, args=("Invalid config | Go6","Please fix proxy format to continue",f"{self.ASSETS_DICT}go6icon.ico",7)).start()
                        os.startfile(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), self.PROXIES_DICT))
                        last_mod = os.path.getmtime(self.PROXIES_DICT)
                        while True:
                            sleep(1)
                            if os.path.getmtime(self.PROXIES_DICT) != last_mod:
                                break
                        runMainPage() 
                if len(data) > 99:
                    data[:99]    
                self.useProxy = True
                self.proxies = itertools.cycle(data)
        self.cns.clear()          
        self.cns.logo()
        self.cns.title(f"Go6 Debug Console")   
        print("1")
        self.setupUi(window)
        window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        window.setFixedSize(791,402)
        window.setWindowTitle(f"Go6")
        window.setWindowIcon(QtGui.QIcon(f'{self.ASSETS_DICT}go6icon.ico'))
        self.build_num, self.app_num, self.darwin_num = Discord(None,None).getClientInfo()
        self.labelH_Version.setText(str(VERSION))
        self.labelH_Key.setText(f'key: {key[:9]}*')
        self.labelH_Expirey.setText(f'expirey: {expiry}')
        self.labelH_TokensCount.setText(f'tokens count: {len(self.tokens)}')
        self.labelH_BuildNumber.setText(f'build num: {self.build_num}')
        self.labelH_ClientVersion.setText(f'app version: {self.app_num}')
        self.labelH_DarwinVersion.setText(f'darwin num: {self.darwin_num}')
        self.pushButtonNAV_StartClose.clicked.connect(window.close)
        self.pushButtonNAV_StartMinimize.clicked.connect(window.showMinimized)     
        self.pushButtonNAV_Home.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.pushButtonNAV_Spammer.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.pushButtonNAV_DmSpammer.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.pushButtonNAV_Joiner.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.pushButtonNAV_VoiceSpammer.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(4))
        self.pushButtonNAV_HookSpammer.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(5))
        self.pushButtonNAV_Settings.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(6))
        self.pushButtonGM_RctBypass.clicked.connect(lambda: self.stackedWidgetGM_BypassMenu.setCurrentIndex(0))
        self.pushButtonGM_MsgBypass.clicked.connect(lambda: self.stackedWidgetGM_BypassMenu.setCurrentIndex(1))
        self.pushButtonGM_BtnBypass.clicked.connect(lambda: self.stackedWidgetGM_BypassMenu.setCurrentIndex(2))
        
        global spammerSwitch 
        spammerSwitch=False
        global voiceSwitch
        voiceSwitch=False
        global threadSwitch
        threadSwitch=False
        global dmSwitch
        dmSwitch=False
        global nickSwitch
        nickSwitch=False
        global hookSwitch
        hookSwitch=False
        global TOTAL_SENT_SUCCESS
        TOTAL_SENT_SUCCESS = 0
        global TOTAL_SENT_FAILED
        TOTAL_SENT_FAILED = 0
        global TOTAL_JOINED_SUCCESS
        TOTAL_JOINED_SUCCESS = 0
        global TOTAL_JOINED_FAILED
        TOTAL_JOINED_FAILED = 0
        global TOTAL_JOINED_CAPTCHA
        TOTAL_JOINED_CAPTCHA = 0

        # placeholders
        inputfields = [
            self.lineEditGS_ChannelId,
            self.lineEditGS_GuildId,
            self.lineEditGS_ThreadName,
            self.lineEditGS_ForumName,
            self.lineEditDS_UserId,
            self.lineEditGM_Invite,
            self.lineEditGMRB_ChannelId,
            self.lineEditGMRB_MessageId,
            self.lineEditGMRB_Emoji,
            self.lineEditGMMB_GuildId,
            self.lineEditGMMB_SpamMessage,
            self.lineEditGMBB_GuildId,
            self.lineEditGMBB_ChannelId,
            self.lineEditGMBB_MessageId,
            self.lineEditSE_BioMessage,
            self.lineEditSE_DisplayName,
            self.lineEditSE_PronounName,
            self.lineEditHS_Webhook,
            self.lineEditVS_ChannelId,
            self.lineEditVS_GuildId
        ]
        placeholders = [
            "channel id",
            "guild id",
            "go6.lol",
            "go6.lol",
            "user id",
            "discord.gg/go6",
            "channel id",
            "message id",
            "emoji",
            "channel id",
            "message",
            "guild id",
            "channel id",
            "message id",
            "https://go6.lol",
            "go6.lol",
            "go6/user",
            "url",
            "channel id",
            "guild id"
        ]
        for field, text in zip(inputfields, placeholders):
            field.setPlaceholderText(text)
            field.setAlignment(QtCore.Qt.AlignCenter)

        # button forwarding
        buttonfunc = [
            self.checkTokensLauncher,
            self.checkProxiesLauncher,
            self.refreshTokens,
            self.refreshProxies,
            self.channelSpammerLauncher,
            self.threadSpammerLauncher,
            (self.threadSpammerLauncher, True),
            self.parseUsersLauncher,
            self.dmSpammerLauncher,
            self.friendSpammerLauncher,
            self.guildJoinLauncher,
            self.guildLeaveLauncher,
            self.guildCheckerLauncher,
            self.reactionBypassLauncher,
            self.messageBypassLauncher,
            self.buttonBypassLauncher,
            (self.tokenConfigLauncher, "bio"),
            (self.tokenConfigLauncher, "display"),
            (self.tokenConfigLauncher, "pfp"),
            (self.tokenConfigLauncher, "pronouns"),
            (self.tokenConfigLauncher, "bioreset"),
            (self.tokenConfigLauncher, "displayreset"),
            (self.tokenConfigLauncher, "pfpreset"),
            (self.tokenConfigLauncher, "pronounsreset"),
            (self.utilsLauncher, "clear"), 
            (self.hookLauncher, "spam"),
            (self.hookLauncher, "delete"),
            (self.voiceLauncher, "join"),
            (self.voiceLauncher, "leave"),
            (self.voiceLauncher, "spam")

        ]

        buttons = [
            self.pushButtonH_StartCheckTokens,
            self.pushButtonH_StartCheckProxies,
            self.pushButtonH_StartLoadTokens,
            self.pushButtonH_StartLoadProxies,
            self.pushButtonGS_StartSpam,
            self.pushButtonGS_StartCreateThreads,
            self.pushButtonGS_StartCreateForum,
            self.pushButtonGS_StartParseUsers,
            self.pushButtonDS_StartSpam,
            self.pushButtonDS_StartFriend,
            self.pushButtonGM_StartJoin,
            self.pushButtonGM_StartLeave,
            self.pushButtonGM_StartCheckGuild,
            self.pushButton_GM_StartRctBypass,
            self.pushButtonGM_StartMsgBypass,
            self.pushButtonGM_StartBtnBypass,
            self.pushButtonSE_StartSetBio,
            self.pushButtonSE_StartSetDisplay,
            self.pushButtonSE_StartSetPfp,
            self.pushButtonSE_StartSetPronouns,
            self.pushButtonSE_StartUnSetBio,
            self.pushButtonSE_StartUnSetDisplay,
            self.pushButtonSE_StartUnSetPfp,
            self.pushButtonSE_StartUnSetPronouns,
            self.pushButtonSE_StartClearConsole,
            self.pushButtonHS_StartSpam,
            self.pushButtonHS_StartDelete,
            self.pushButtonVS_StartJoin,
            self.pushButtonVS_StartLeave,
            self.pushButtonVS_StartSpam
        ]

        for button, func in zip(buttons, buttonfunc):
            if isinstance(func, tuple):
                f, a = func
                button.clicked.connect(lambda _, f=f, a=a: threading.Thread(target=lambda: f(a) if a is not None else f()).start())
            else:
                button.clicked.connect(lambda _, f=func: threading.Thread(target=f).start())

        # extras
        self.horizontalSliderH_MaxTokens.valueChanged.connect(lambda: threading.Thread(target=self.updateSliderValue).start())
        self.horizontalSliderH_MaxTokens.setMaximum(len(self.tokens))
        self.horizontalSliderH_MaxTokens.setValue(len(self.tokens))
        self.comboBoxSE_PfpName.addItems([filename for filename in os.listdir(self.PFP_DICT) if os.path.isfile(f'{self.PFP_DICT}{filename}') and filename.lower().endswith(('.png', '.jpg'))])
        self.comboBoxGM_VerificationBypass.addItems(["none","restorecord", "sledgehammer", "doublecounter"])
    # other

    def updateSliderValue(self,):
        self.labelH_MaxTokensCount.setText(str((self.horizontalSliderH_MaxTokens.value()))) 

    def updateUseProxy(self,state):
        if state == QtCore.Qt.Checked:
            self.useProxy = True
        else:
            self.useProxy = False      

    def getProxy(self):
        if self.useProxy:
            return next(self.proxies)
        return None
    
    def getTokenIDS(self):
        ids = []
        self.tokens = self.splitList(self.tokens,len(self.tokens),self.horizontalSliderH_MaxTokens.value())
        for token in self.tokens:
            idd= base64.b64decode(token[0][:24].encode()).decode()
            ids.append(idd)
        return ids
        
    def getCaptchaKey(self, js: dict):
        if self.solveCaptcha:
            if not self.getProxy() == None:
                rqdata = js["captcha_rqdata"]
                rqtoken = js["captcha_rqtoken"]
                site_key = js["captcha_sitekey"]
                key = getCaptchaKey(rqdata=rqdata, site_key=site_key, cap_key=self.capkey, provider=self.provider, proxy=self.getProxy())
                if key is None: return None, None
                return key, rqtoken
            return None,None
        return None, None
    
    def splitList(self, a, n, limit=None):
        k, m = divmod(len(a), n)
        split_lines = [line.split(":")[-1] for line in a]
        tokens = list(split_lines[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))
        if limit is not None:
            return tokens[:limit]
        else:
            return tokens

    #
        
    def checkTokens(self,tokens: list,v: list,inv: list):
        for token in tokens:
            dc = Discord(self.getProxy(), token)

            try:
                st, resp = dc.check()
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                continue

            if st:
                self.cns.success(f'Valid -> {token}')
                v.append(token)
            else:
                js = resp.json()
                match resp.status_code:
                    case 401:
                        self.cns.info(f'Failed to authorize -> {token}')
                        inv.append(token)
                    case _:
                        self.cns.info(f'Failed to check -> {js}')
    def checkTokensLauncher(self, removeinv=False):
        v = []
        inv = []

        threads = []
        for token in self.splitList(self.tokens,len(self.tokens)):
            thread = threading.Thread(target=self.checkTokens, args=(token,v,inv))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
            
        self.labelH_TokensValidCount.setText(f'tokens valid: {len(v)}')
        self.labelH_TokensInValidCount.setText(f'tokens dead: {len(inv)}')        
        if removeinv:
            with open(self.TOKENS_DICT, 'w') as file:
                file.write('\n'.join(v))    


    def checkProxies(self,proxies: list,v: list):
        for proxy in proxies:
            dc = Discord(proxy, None)

            try:
                st, resp = dc.checkConnection()
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                continue

            if st:
                self.cns.success(f'Valid -> {proxy}')
                v.append(proxy)
            else:
                js = resp.json()
                match resp.status_code:
                    case 400:
                        self.cns.info(f'Failed to connect -> {proxy}')
                    case _:
                        self.cns.info(f'Failed to check -> {js}')
    def checkProxiesLauncher(self, removeinv=False):
        v = []

        threads = []
        for proxy in [line.strip() for line in open(self.PROXIES_DICT, 'r').readlines()]:
            thread = threading.Thread(target=self.checkProxies, args=([proxy],v,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join() 

        if removeinv:
            with open(self.PROXIES_DICT, 'w') as file:
                file.write('\n'.join(v))     


    def refreshTokens(self):
         with open(self.TOKENS_DICT, 'r') as file:
            self.tokens = [line.strip() for line in file.read().splitlines() if line.strip()]
            self.horizontalSliderH_MaxTokens.setMaximum(len(self.tokens))
            self.horizontalSliderH_MaxTokens.setValue(len(self.tokens))
            self.labelH_TokensCount.setText(f'tokens count: {len(self.tokens)}')
            self.cns.info(f'Loaded tokens -> {len(self.tokens)}')
    def refreshProxies(self):
        with open(self.PROXIES_DICT, 'r') as file:
            lines = file.read().splitlines()
            if len(lines) > 99:
                lines = lines[:99]
        with open(self.PROXIES_DICT, 'w') as file:
            file.write('\n'.join(lines))
        self.proxies = itertools.cycle([line.strip() for line in lines if line.strip()])
        self.cns.info(f'Loaded proxies -> {len(lines)}')


    def verifyRestoreCord(self,tokens: list, guildID: str):
        for token in tokens:
            dc = Discord(self.getProxy(), token)
            try:
                    clientID = dc.getClientID('https://restorecord.com/verify/', guildID)
            except Exception as e:
                    self.cns.error(f"-> {str(e)}")
                    continue
            try:
                    st, resp = dc.acceptRestoreCord(guildID, clientID)
            except Exception as e:
                    self.cns.error(f"-> {str(e)}")
                    continue 

            if st:
                    self.cns.success(f"Bypassed RestoreCord -> {guildID}")
            else:
                    js = resp.json()
                    match resp.status_code:
                            case 429:
                                    self.cns.info("Failed to bypass -> ratelimit")
                            case _:
                                    self.cns.info(f"Failed to bypass -> {js}") 
    def verifySledgeHammer(self,tokens: list, guildID: str):
        for token in tokens:
            dc = Discord(self.getProxy(), token)
            try:
                    cid, mid, aid = dc.findIDs(guildID, 'Sledgehammer', 'you need to prove that you are a human')
            except Exception as e:
                    return self.cns.error(f"-> {str(e)}")      
            try:
                    st, resp = dc.acceptSledgeHammer(aid, cid, mid, guildID) 
            except Exception as e:
                    self.cns.error(f"-> {str(e)}")             

            if st:
                    self.cns.success(f"Bypassed SledgeHammer -> {guildID}")
            else:
                    js = resp.json()
                    match resp.status_code:
                            case 429:
                                    self.cns.info("Failed to verify -> ratelimit")
                            case _:
                                    self.cns.info(f"Failed to verify -> {js}") 
    def verifyDoubleCounter(self,tokens: list,  guildID: str, channelID: str):
        for token in tokens:
            dc = Discord(self.getProxy(), token)
            try:
                    st, resp = dc.createDM("703886990948565003", guildID, channelID)
            except Exception as e:
                    return self.cns.error(f"-> {str(e)}")             
            try:
                    st, resp = dc.acceptDoubleCounter(resp.json()["id"])
            except Exception as e:
                    self.cns.error(f"-> {str(e)}")             

            if st:
                    self.cns.success(f"Bypassed DoubleCounter -> {guildID}")
            else:
                    js = resp.json()
                    match resp.status_code:
                            case 429:
                                    self.cns.info("Failed to verify -> ratelimit")
                            case _:
                                    self.cns.info(f"Failed to verify -> {js}")                                          
    def guildJoin(self,tokens: list,invite: str,context: str,botBypass: str,guildID: str = None, rqtoken: str = None,captcha: str = None):
        global TOTAL_JOINED_SUCCESS, TOTAL_JOINED_FAILED, TOTAL_JOINED_CAPTCHA
        TOTAL_JOINED_SUCCESS, TOTAL_JOINED_FAILED, TOTAL_JOINED_CAPTCHA = 0,0,0
        for token in tokens:
            dc = Discord(self.getProxy(),token)
            
            try:
                st, resp = dc.join(invite,context,rqtoken,captcha)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                continue

            if st:
                # temp
                try:
                    js = resp.json()
                except json.decoder.JSONDecodeError as je:
                    self.cns.error(f'-> {str(je)}')
                    continue
                #

                self.cns.success(f'Joined -> {invite}')
                # stats
                TOTAL_JOINED_SUCCESS +=1;self.labelGM_Joined.setText(f"joined: {str(int(TOTAL_JOINED_SUCCESS))}")
                #
                if guildID != "":
                    levels = js["guild"]["features"]
                if 'MEMBER_VERIFICATION_GATE_ENABLED' in levels and guildID != "":
                                st, resp = dc.acceptRules(invite, guildID)
                                if st:
                                        self.cns.success(f"Bypassed rules -> {invite}")
                                else:
                                        js = resp.json()
                                        self.cns.info(f"Failed to bypass rules -> {js}")

                if 'GUILD_ONBOARDING_EVER_ENABLED' in levels and guildID != "":  
                        st, resp = dc.acceptOnBoarding(guildID)
                        if st:
                                self.cns.success(f"Bypassed onboarding menu -> {invite}")
                        else:
                                js = resp.json()
                                self.cns.info(f"Failed to bypass onboarding -> {js}")   

                if botBypass == "doublecounter" and guildID != "":
                        channelID = js["channel"]["id"]
                        self.verifyDoubleCounter([token], guildID, channelID)                                
                if botBypass == "sledgehammer" and guildID != "":
                        self.verifySledgeHammer([token], guildID)   
                if botBypass == "restorecord" and guildID != "":
                        self.verifyRestoreCord([token], guildID)

            else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info('Failed to join -> ratelimit')
                        TOTAL_JOINED_FAILED +=1;self.labelGM_Failed.setText(f"failed: {str(int(TOTAL_JOINED_FAILED))}")
                    case 400:
                        self.cns.info('Failed to join -> captcha')
                        TOTAL_JOINED_CAPTCHA +=1;self.labelGM_Solving.setText(f"solving: {str(int(TOTAL_JOINED_CAPTCHA))}")
                        captcha, rqtoken = self.getCaptchaKey(js)
                        self.guildJoin([token],invite, context, botBypass, guildID, rqtoken=rqtoken,captcha=captcha)
                        TOTAL_JOINED_CAPTCHA -=1;self.labelGM_Solving.setText(f"solving: {str(int(TOTAL_JOINED_CAPTCHA))}")
                    case _:
                        self.cns.info(f'Failed to join -> {js}')
                        TOTAL_JOINED_FAILED +=1;self.labelGM_Failed.setText(f"failed: {str(int(TOTAL_JOINED_FAILED))}")
    def guildJoinLauncher(self):
        tokens = self.splitList(self.tokens,len(self.tokens),self.horizontalSliderH_MaxTokens.value()) 
        inv = self.lineEditGM_Invite.text()
        bot = self.comboBoxGM_VerificationBypass.currentText()

        if not tokens or not inv:
            return self.cns.info('Invalid input')

        #
        self.labelGM_Joined.setText("joined: 0");self.labelGM_Failed.setText("failed: 0");self.labelGM_Solving.setText("solving: 0")
        #

        try:
            inv = extractCode(inv)
        except Exception as e:
            self.cns.error(f'-> {str(e)}')
            return

        try:
            guildid,context = Discord.getContextProperties(inv)
        except Exception as e:
            self.cns.error(f'-> {str(e)}')
            return

        threads = []
        for i in range(len(tokens)):
                token = tokens[i % len(tokens)]  # Distribute tokens among threads
                thread = threading.Thread(target=self.guildJoin, args=(token,inv,context,bot,guildid))
                thread.start()
                threads.append(thread)
        for thread in threads:
                thread.join()


    def guildLeave(self,tokens: list,guildID: str,):
        for token in tokens:
            dc = Discord(self.getProxy(),token)

            try:
                st, resp = dc.leave(guildID) 
            except Exception as e:
                self.cns.error(f'-> {str(e)}') 
                continue

            if st:
                self.cns.success(f'Left -> {guildID}')
            else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info('Failed to leave -> ratelimit')
                    case _:
                        self.cns.info(f'Failed to leave -> {js}')  
    def guildLeaveLauncher(self):
            tokens = self.splitList(self.tokens,len(self.tokens),self.horizontalSliderH_MaxTokens.value()) 
            inv = self.lineEditGM_Invite.text()

            if not tokens or not inv:
                return self.cns.info('Invalid input')

            try:
                inv = extractCode(inv)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                return

            try:
                guildid,context = Discord.getContextProperties(inv)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                return

            threads = []
            for i in range(len(tokens)):
                    token = tokens[i % len(tokens)]  # Distribute tokens among threads
                    thread = threading.Thread(target=self.guildLeave, args=(token,guildid))
                    thread.start()
                    threads.append(thread)
            for thread in threads:
                    thread.join()

    def friendSend(self,tokens: list,userID: str,):
        for token in tokens:
            dc = Discord(self.getProxy(),token)

            try:
                st, resp = dc.friend(userID)
            except Exception as e:
                self.cns.error(f'-> {str(e)}') 
                continue

            if st:
                self.cns.success(f'Sent request -> {userID}')
            else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info('Failed to send -> ratelimit')
                    case _:
                        self.cns.info(f'Failed to send -> {js}')  
    def friendSpammerLauncher(self):
            tokens = self.splitList(self.tokens,len(self.tokens),self.horizontalSliderH_MaxTokens.value()) 
            uid = self.lineEditDS_UserId.text()

            if not tokens or not uid:
                return self.cns.info('Invalid input')

            threads = []
            for i in range(len(tokens)):
                    token = tokens[i % len(tokens)]
                    thread = threading.Thread(target=self.friendSend, args=(token,uid))
                    thread.start()
                    threads.append(thread)
            for thread in threads:
                    thread.join()               

    def guildChecker(self,tokens: list,guildID: str):
        for token in tokens:
            dc = Discord(self.getProxy(), token)

            try:
                st, resp = dc.checkGuild(guildID)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                continue

            if st:
                self.cns.success(f'Vaild guild -> {guildID}')
            else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info('Failed to check -> ratelimit')
                    case _:
                        self.cns.info(f'Failed to check -> {js}')
    def guildCheckerLauncher(self):
            tokens = self.splitList(self.tokens,len(self.tokens),self.horizontalSliderH_MaxTokens.value()) 
            inv = self.lineEditGM_Invite.text()

            if not tokens or not inv:
                return self.cns.info('Invalid input')

            try:
                inv = extractCode(inv)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                return

            try:
                guildid,context = Discord.getContextProperties(inv)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                return

            threads = []
            for i in range(len(tokens)):
                    token = tokens[i % len(tokens)]  # Distribute tokens among threads
                    thread = threading.Thread(target=self.guildChecker, args=(token,guildid))
                    thread.start()
                    threads.append(thread)
            for thread in threads:
                    thread.join()    


    def reactionBypass(self,tokens: list,messageID: str, channelID: str, emoji: str):
        for token in tokens:
            dc = Discord(self.getProxy(),token)

            try:
                st, resp = dc.reaction(messageID,channelID,emoji)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                continue

            if st:
                self.cns.success(f'Executed reaction -> {messageID}')
            else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info('Failed to execute -> ratelimit')
                    case _:
                        self.cns.info(f'Failed to execute -> {js}')
    def reactionBypassLauncher(self):
        tokens = self.splitList(self.tokens,len(self.tokens),self.horizontalSliderH_MaxTokens.value()) 
        cid = self.lineEditGMRB_ChannelId.text()
        mid = self.lineEditGMRB_MessageId.text()
        emoji = self.lineEditGMRB_Emoji.text()

        if not tokens or not cid.isdigit() or not mid.isdigit() or not emoji:
                return self.cns.info('Invalid input')

        threads = []
        for i in range(len(tokens)):
                token = tokens[i % len(tokens)]
                thread = threading.Thread(target=self.reactionBypass, args=(token,mid,cid,emoji))
                thread.start()
                threads.append(thread)
        for thread in threads:
                thread.join()


    def messageBypass(self,tokens: list,channelID: str, message: str):
        for token in tokens:
            dc = Discord(self.getProxy(),token)

            try:
                st, resp = dc.sendMessage(channelID,message)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                continue

            if st:
                self.cns.success(f'Sent message -> {channelID}')
            else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info('Failed to execute -> ratelimit')
                    case _:
                        self.cns.info(f'Failed to execute -> {js}')
    def messageBypassLauncher(self):
        tokens = self.splitList(self.tokens,len(self.tokens),self.horizontalSliderH_MaxTokens.value())
        cid = self.lineEditGMMB_GuildId.text() # CHANNELID
        msg = self.lineEditGMMB_SpamMessage.text()

        if not tokens or not cid.isdigit() or not msg:
             return self.cns.info("Invalid input")

        threads = []
        for i in range(len(tokens)):
                token = tokens[i % len(tokens)]
                thread = threading.Thread(target=self.messageBypass, args=(token,cid,msg))
                thread.start()
                threads.append(thread)
        for thread in threads:
                thread.join()


    def buttonBypass(self,tokens: list,channelID: str,messageID: str,guildID: str):
        for token in tokens:
            dc = Discord(self.getProxy(),token)

            try:
                messageshit = dc.getButton(channelID, token)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                continue  

            try:
                st, resp = dc.button(*messageshit, channelID, guildID, None)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                continue

            if st:
                self.cns.success(f'Clicked button -> {messageID}')
            else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info('Failed to execute -> ratelimit')
                    case _:
                        self.cns.info(f'Failed to execute -> {js}')
    def buttonBypassLauncher(self):
        tokens = self.splitList(self.tokens,len(self.tokens),self.horizontalSliderH_MaxTokens.value())
        cid = self.lineEditGMBB_ChannelId.text()
        gid = self.lineEditGMBB_GuildId.text()
        mid = self.lineEditGMBB_MessageId.text()

        if not tokens or not cid.isdigit or not gid.isdigit or not mid.isdigit():
            return self.cns.info("Invalid input")

        threads = []
        for i in range(len(tokens)):
                token = tokens[i % len(tokens)]
                thread = threading.Thread(target=self.buttonBypass, args=(token,cid,mid,gid))
                thread.start()
                threads.append(thread)
        for thread in threads:
                thread.join()           


      
    def channelSpammer(self,tokens: list, channelID: str, message: str, modes: dict, delay: int, start_time:int, ids: list = [],):
        global TOTAL_SENT_SUCCESS, TOTAL_SENT_FAILED
        for token in tokens:
            random.shuffle(ids)
            ids = itertools.cycle(ids)
            countmsg = 0
            

            dc = Discord(self.getProxy(),token)

            if modes["stickerspam"]:
                    stickerids = dc.scrapeStickers()

            while spammerSwitch:
                copyMessage = message
                #
                if modes["antilock"] and countmsg >= 14:
                        countmsg = 0
                        sleep(2.5)
                while "[mtag]" in copyMessage:
                    copyMessage = copyMessage.replace("[mtag]", f"||<@{next(ids)}>||" if modes["hideping"] else f"<@{next(ids)}>", 1)
                while "[num]" in copyMessage:
                    copyMessage = copyMessage.replace("[num]", "".join(random.choices('0123456789', k=choice([8, 11]))))
                while "[random]" in copyMessage:
                    copyMessage = copyMessage.replace("[random]", "".join(random.choices(string.ascii_letters, k=choice([8, 11]))))       
                while "[poon]" in copyMessage:
                    copyMessage = copyMessage.replace("[poon]", getPoonLink(), 1)

                if modes["multimsg"] and not modes["ghostpingv2"]: 
                    html_text = self.textEditGS_SpamMessage.toHtml()
                    soup = bs4.BeautifulSoup(html_text, 'html.parser')
                    body = soup.find('body')
                    lines = [element.text for element in body.descendants if element.name == 'p' or element.name == 'br']
                    copyMessage = choice(lines)
                if modes["ghostpingv2"]:
                    copyMessage+='||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|||||||||||| @everyone\n'
                if modes["emojispam"] and not modes["ghostpingv2"]:
                    random_code_point = random.randint(0x1F600, 0x1F64F)
                    new_emoji = chr(random_code_point)
                    if search(r'[^\x00-\x7F]', message):
                        copyMessage = re.sub(r'[^\x00-\x7F]+', new_emoji, message)
                    else:
                        copyMessage += " " + new_emoji 
                if modes["spaceletters"] and not modes["ghostpingv2"]: 
                    copyMessage = ' '.join(copyMessage)
                if modes["specialletters"] and not modes["ghostpingv2"]:
                    char_replace = {'a': 'à', 'b': 'ƀ', 'c': 'ç', 'd': 'đ', 'e': 'è', 'f': 'ƒ', 'g': 'ĝ', 'h': 'ĥ', 'i': 'ì', 'j': 'ĵ', 'k': 'ķ', 'l': 'ĺ', 'm': 'ɱ', 'n': 'ŋ', 'o': 'ò', 'p': 'ƿ', 'q': 'ɋ', 'r': 'ŕ', 's': 'ş', 't': 'ţ', 'u': 'ù', 'v': 'ṽ', 'w': 'ŵ', 'x': 'ẋ', 'y': 'ý', 'z': 'ź'}
                    copyMessage = ''.join(char_replace.get(char, char) for char in copyMessage)           
                #

                try:
                    st, resp = dc.sendMessage(channelID,copyMessage, choice(stickerids) if modes["stickerspam"] else None)
                except Exception as e:
                    self.cns.error(f'-> {str(e)}')
                    continue

                if st:
                    self.cns.success(f'Sent message -> {channelID}')
                    TOTAL_SENT_SUCCESS+=1;self.labelGS_SentMessageCount.setText(f'sent: {TOTAL_SENT_SUCCESS}')
                    if modes["antilock"]:
                        countmsg += 1

                    elapsed_time = time() - start_time
                    msg_rate = TOTAL_SENT_SUCCESS / elapsed_time 
                    self.labelGS_RatePerSecondCount.setText(f'rate: {msg_rate}/s')      

                    sleep(delay)
                    continue
                else:
                    js = resp.json()
                    match resp.status_code:
                        case 429:
                            self.cns.info('Failed to send message -> ratelimit')
                            TOTAL_SENT_FAILED+=1 ; self.labelGS_FailedMessageCount.setText(f'failed: {TOTAL_SENT_FAILED}')
                            handleRatelimit(js)
                            continue
                        case _:
                            TOTAL_SENT_FAILED+=1 ; self.labelGS_FailedMessageCount.setText(f'failed: {TOTAL_SENT_FAILED}')
                            self.cns.info(f'Failed to send message -> {js}')         
    def channelSpammerLauncher(self):
        global spammerSwitch, TOTAL_SENT_SUCCESS, TOTAL_SENT_FAILED

        TOTAL_SENT_SUCCESS,TOTAL_SENT_FAILED = 0,0

        tokens = self.splitList(self.tokens,len(self.tokens),self.horizontalSliderH_MaxTokens.value())
        cid = self.lineEditGS_ChannelId.text()
        gid = self.lineEditGS_GuildId.text()
        msg = self.textEditGS_SpamMessage.toPlainText()
        delay = self.horizontalSliderGS_Delay.value()

        if not tokens or not cid.isdigit() or not gid.isdigit() or not msg:
             return self.cns.info("Invalid input")

        modes = {
            "multimsg": self.checkBoxGS_MultiMsg.isChecked(),
            "antilock": self.checkBoxGS_AntiLock.isChecked(),
            "emojispam": self.checkBoxGS_EmojiSpam.isChecked(),
            "ghostpingv2": self.checkBoxGS_GhostPing.isChecked(),
            "hideping": self.checkBoxGS_HidePing.isChecked(),
            "spaceletters": self.checkBoxGS_SpaceLetters.isChecked(),  # space letters
            "specialletters": self.checkBoxGS_SpecialLetters.isChecked(),  # special letters
            "stickerspam": self.checkBoxGS_StickerSpam.isChecked(),
        }

        if self.pushButtonGS_StartSpam.text() == "Spam":
            self.pushButtonGS_StartSpam.setText("Stop")
            spammerSwitch = True

            ids = []
            if "[mtag]" in msg:
                    try:
                        ids = open(f"{self.PFP_DICT}{gid}.txt", "r").read().splitlines()
                    except Exception as e:
                         self.cns.error(f'-> {str(e)}')   
                         return       

                 
            threads = []
            for i in range(len(tokens)):
                    token = tokens[i % len(tokens)]
                    thread = threading.Thread(target=self.channelSpammer, args=(token,cid,msg, modes,delay,time(), ids))
                    thread.start()
                    threads.append(thread)
            for thread in threads:
                    thread.join() 
        else:
            self.pushButtonGS_StartSpam.setText("Spam")
            spammerSwitch = False



    def parseUsers(self,  token: str, channelID: str, guildID: str):
        token_ids = self.getTokenIDS()
        soc = DiscordSocket(token[0], guildID, channelID)
        IDs = soc.run()

        with open(f"{self.PFP_DICT}{guildID}.txt", "w+") as f:
            data = ""
            for key, values in IDs.items():
                if key in token_ids:
                    continue
                data += key + "\n"

            f.write(data)  
        with open(f"{self.PFP_DICT}names.txt", "a+", encoding="latin-1") as f:
            data = ""
            for key, values in IDs.items():
                data += unidecode(values["tag"]) + "\n"

            f.write(data)   

        self.cns.success(f"Scraped IDs -> {len(IDs)}")

        self.labelGS_ParsedCount.setText(f"parsed: {str(len(IDs))}")
        return IDs
    def parseUsersLauncher(self):
        token = choice(self.splitList(self.tokens,len(self.tokens),self.horizontalSliderH_MaxTokens.value())) 
        cid = self.lineEditGS_ChannelId.text()
        gid = self.lineEditGS_GuildId.text()

        if not token or not cid.isdigit() or not gid.isdigit():
             return self.cns.info("Invalid input")

        self.parseUsers(token, cid, gid)
        self.refreshTokens()


    def threadSpammer(self, tokens: list, channelID: str, guildID: str, threadName: str, threadMessage: str, delay: int,forum:bool):
         for token in tokens:
              dc = Discord(self.getProxy(),token)

              while threadSwitch:
                try:
                    st, resp = dc.threads(channelID,guildID,threadName,forum)
                except Exception as e:
                    self.cns.error(f'-> {str(e)}')
                    continue

                if st:
                        self.cns.success(f'Created thread -> {channelID}')
                        id = resp.json()["id"]
                        try:
                                st,resp = dc.sendMessage(id,threadMessage)
                        except Exception as e:
                                self.cns.error(f'-> {str(e)}')
                                continue
                        if st:
                            self.cns.success(f'Sent message -> {id}')
                        else:
                            js = resp.json()
                            match resp.status_code:
                                case 429:
                                    self.cns.info('Failed to create thread -> ratelimit')
                                    handleRatelimit(js)
                                    continue
                                case _:
                                    self.cns.info(f'Failed to create thread -> {js}')
                        sleep(delay)                      
                else:
                        js = resp.json()
                        match resp.status_code:
                            case 429:
                                self.cns.info('Failed to create thread -> ratelimit')
                                handleRatelimit(js)
                                continue
                            case _:
                                self.cns.info(f'Failed to create thread -> {js}')
    def threadSpammerLauncher(self, forum=False):
        global threadSwitch

        tokens = self.splitList(self.tokens, len(self.tokens), self.horizontalSliderH_MaxTokens.value())
        cid = self.lineEditGS_ChannelId.text()
        gid = self.lineEditGS_GuildId.text()
        title = self.lineEditGS_ThreadName.text() if not forum else self.lineEditGS_ForumName.text()
        msg = self.textEditGS_SpamMessage.toPlainText()
        delay = self.horizontalSliderGS_Delay.value()

        if not tokens or not cid.isdigit() or not gid.isdigit or not title or not msg:
             return self.cns.info("Invalid input")
        
        button, text = (self.pushButtonGS_StartCreateThreads, "Create Threads") if not forum else (self.pushButtonGS_StartCreateForum, "Create Forum")

        if button.text() == text:
            button.setText("Stop")
            threadSwitch=True

            threads = []
            for i in range(len(tokens)):
                    token = tokens[i % len(tokens)]
                    thread = threading.Thread(target=self.threadSpammer, args=(token, cid, gid, title, msg, delay,forum))
                    thread.start()
                    threads.append(thread)
            for thread in threads:
                    thread.join()   
        else:
            threadSwitch=False
            button.setText(text)
                                                       

    def dmSpammer(self, tokens: list, userID: str, message: str, rqtoken: str = None, captcha: str = None):
         for token in tokens:
                dc = Discord(self.getProxy(),token)

                while dmSwitch:
                    try:
                        st, resp = dc.createDM(userID)
                    except Exception as e:
                        self.cns.error(f'-> {str(e)}')
                        continue
                    if st:
                        id = resp.json()["id"]
                        self.cns.success(f'Created DM -> {id}')
                        
                        try:
                                st, resp = dc.sendDM(id,message,rqtoken,captcha)
                        except Exception as e:
                                self.cns.error(f'-> {str(e)}')
                                continue
                        if st:
                                self.cns.success(f'Sent DM -> {userID}')
                        else:
                                js = resp.json()
                                match resp.status_code:
                                    case 429:
                                        self.cns.info('Failed to send DM -> ratelimit')
                                        handleRatelimit(js)
                                        continue
                                    case 400:
                                        rqtoken,captcha=self.getCaptchaKey(js)
                                        self.dmSpammer([token],userID,message,rqtoken=rqtoken,captcha=captcha)   
                                    case _:
                                        self.cns.info(f'Failed to send DM -> {js}')
                    else:
                            js = resp.json()
                            match resp.status_code:
                                case 429:
                                    self.cns.info('Failed to create DM -> ratelimit')
                                    handleRatelimit(js)
                                    continue
                                case _:
                                    self.cns.info(f'Failed to create DM -> {js}')
    def dmSpammerLauncher(self):
        global dmSwitch

        tokens = self.splitList(self.tokens, len(self.tokens), self.horizontalSliderH_MaxTokens.value())
        uid = self.lineEditDS_UserId.text()
        msg = self.textEditDS_SpamMessage.toPlainText()

        if not tokens or not uid.isdigit() or not msg:
             return self.cns.info("Invalid input")

        if self.pushButtonDS_StartSpam.text() == "Spam":
            self.pushButtonDS_StartSpam.setText("Stop")

            dmSwitch=True
            threads = []
            for i in range(len(tokens)):
                    token = tokens[i % len(tokens)]
                    thread = threading.Thread(target=self.dmSpammer, args=(token, uid,msg))
                    thread.start()
                    threads.append(thread)
            for thread in threads:
                    thread.join()
        else:
             dmSwitch=False
             self.pushButtonDS_StartSpam.setText("Spam")  

    def setDisplay(self, tokens: list, display: str):
         for token in tokens:
              dc = Discord(self.getProxy(),token)

              try:
                   st, resp = dc.changeDisplayName(display)
              except Exception as e:
                   self.cns.error(f'-> {str(e)}')
                   continue

              if st:
                   self.cns.success(f'Changed display -> {st}')
              else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info('Failed to change display -> ratelimit')
                    case _:
                        self.cns.info(f'Failed to change display -> {js}')
    def setPronouns(self, tokens: list, pronouns: str):
         for token in tokens:
              dc = Discord(self.getProxy(),token)

              try:
                   st, resp = dc.changePronouns(pronouns)
              except Exception as e:
                   self.cns.error(f'-> {str(e)}')
                   continue

              if st:
                   self.cns.success(f'Changed pronouns -> {st}')
              else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info('Failed to change pronouns -> ratelimit')
                    case _:
                        self.cns.info(f'Failed to change pronouns -> {js}')
    def setBio(self, tokens: list, bio: str):
         for token in tokens:
              dc = Discord(self.getProxy(),token)

              try:
                   st, resp = dc.changeBio(bio)
              except Exception as e:
                   self.cns.error(f'-> {str(e)}')
                   continue
              if st:
                   self.cns.success(f'Changed bio -> {st}')
              else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info('Failed to change bio -> ratelimit')
                    case _:
                        self.cns.info(f'Failed to change bio -> {js}')
    def setPfp(self, tokens: list, pfp: bytes):
        for token in tokens:
             dc = Discord(self.getProxy(),token)

             dc.online() # temp

             try:
                  st,resp = dc.changeAvatar(pfp)
             except Exception as e:
                  self.cns.error(f'-> {str(e)}')
                  continue

             if st:
                  self.cns.success(f'Changed avatar -> {st}')
             else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info('Failed to change avatar -> ratelimit')
                    case _:
                        self.cns.info(f'Failed to change avatar -> {js}')
    def tokenConfigLauncher(self, mode: str):
        tokens = self.splitList(self.tokens, len(self.tokens), self.horizontalSliderH_MaxTokens.value())

        if not tokens:
             return self.cns.info("Invalid input")

        def fwd(func, value):
            threads = []
            for i in range(len(tokens)):
                token = tokens[i % len(tokens)]
                thread = threading.Thread(target=func, args=(token, value))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()

        if mode in {"pfp", "pfpreset"}:
            if self.comboBoxSE_PfpName.currentText() == "":
                 return self.cns.info("Invalid input")

            pfp = self.comboBoxSE_PfpName.currentText()
            avatar = 0 if mode == "preset" else open(f"{self.DATA_DICT}/pfp/{pfp}", "rb").read()
            fwd(self.setPfp, avatar)

        if mode in {"bio", "bioreset"}:
            bio = self.lineEditSE_BioMessage.text() if mode != "breset" else ""
            if not bio:
                 return self.cns.info("Invalid input")
            fwd(self.setBio, bio)

        if mode in {"pronouns", "pronounsreset"}:
            pro = self.lineEditSE_PronounName.text() if mode != "preset" else ""
            if not pro:
                 return self.cns.info("Invalid input")
            fwd(self.setPronouns, pro)

        if mode in {"display", "displayreset"}:
            dis = self.lineEditSE_DisplayName.text() if mode != "dreset" else ""
            if not dis:
                 return self.cns.info("Invalid input")
            fwd(self.setDisplay, dis)





    def utilsLauncher(self, mode:str):
         if mode == "clear":
              self.cns.clear()
              self.cns.logo()

    def hookDelete(self, hook: str,content: str = None):
            dc = Discord(self.getProxy(),None)

            try:
                st, resp = dc.deleteUrl(hook)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
            if st:
                self.cns.success(f'Deleted hook -> {st}')
            else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info('Failed to delete hook -> ratelimit')
                    case _:
                        self.cns.info(f'Failed to delete hook -> {js}')  
    def hookSpam(self, hook: str, content: str):
                global hookSwitch
                dc = Discord(self.getProxy(),None)

                while hookSwitch:

                    try:
                        st, resp = dc.sendContent(hook,content)
                    except Exception as e:
                        self.cns.error(f'-> {str(e)}')
                        continue
                    if st:
                        self.cns.success(f'Sent message -> {st}')
                    else:
                        js = resp.json()
                        match resp.status_code:
                            case 429:
                                self.cns.info('Failed to send message -> ratelimit')
                                handleRatelimit(js)
                                continue
                            case _:
                                self.cns.info(f'Failed to send message-> {js}')              
    def hookLauncher(self, mode: str):
        global hookSwitch

        hook = self.lineEditHS_Webhook.text()
        msg = self.textEditHS_SpamMessage.toPlainText()

        if not hook.startswith("https://discord.com/api/webhooks/") or not msg:
            return self.cns.info("Invalid input")

        if mode in {"delete"}:
            target = self.hookDelete
        if mode in {"spam"}:
            if self.pushButtonHS_StartSpam.text() == "Spam":
                self.pushButtonHS_StartSpam.setText("Stop")
                hookSwitch = True
                target = self.hookSpam
            else:
                hookSwitch = False
                self.pushButtonHS_StartSpam.setText("Spam")

        if hookSwitch or mode in {"delete"}:
            threads = [threading.Thread(target=target, args=(hook, msg if not mode in {"delete"} else None))]
            for thread in threads:
                thread.start()
                thread.join()  

    def voiceSpam(self, tokens: list, channelID: str, guildID: str, mute: bool, deaf: bool, stream:bool, video:bool):
        for token in tokens:
            while voiceSwitch:
                dc = Discord(self.getProxy(),token)

                try:
                    st = dc.voiceExecute(channelID,guildID,mute,deaf,stream,video,True)
                except Exception as e:
                    self.cns.error(f'-> {str(e)}')
                    continue

                if st:
                    self.cns.success(f'Joined and left -> {channelID}')
    def voiceJoin(self, tokens: list, channelID: str, guildID: str, mute: bool, deaf: bool, stream:bool, video:bool):
        for token in tokens:
            dc = Discord(self.getProxy(),token)

            try:
                st = dc.voiceExecute(channelID,guildID,mute,deaf,stream,video,False)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                continue

            if st:
                self.cns.success(f'Joined -> {channelID}')
    def voiceLeave(self, tokens: list, channelID: str, guildID: str, mute: bool, deaf: bool, stream:bool, video:bool):
        for token in tokens:
            dc = Discord(self.getProxy(),token)

            try:
                st = dc.voiceExecute(channelID,guildID,mute,deaf,stream,video,True)
            except Exception as e:
                self.cns.error(f'-> {str(e)}')
                continue
            if st:
                self.cns.success(f'Left -> {channelID}')        
    def voiceLauncher(self, mode: str):
        global voiceSwitch

        tokens = self.splitList(self.tokens, len(self.tokens), self.horizontalSliderH_MaxTokens.value())
        cid = self.lineEditVS_ChannelId.text()
        gid = self.lineEditVS_GuildId.text()

        if not cid or not cid.isdigit() or not gid or not gid.isdigit():
            return self.cns.info("Invalid input")
        
        modes = {
            "mute": self.checkBoxVS_Mute.isChecked(),
            "deafen": self.checkBoxVS_Deafen.isChecked(),
            "stream": self.checkBoxVS_Stream.isChecked(),
            "video": self.checkBoxVS_Video.isChecked(),
        }

        if mode in {"join"}:
            threads = []
            for i in range(len(tokens)):
                    token = tokens[i % len(tokens)]
                    thread = threading.Thread(target=self.voiceJoin, args=(token, cid,gid,modes['mute'],modes['deafen'],modes['stream'],modes['video']))
                    thread.start()
                    threads.append(thread)
            for thread in threads:
                    thread.join()
        if mode in {"leave"}:
            threads = []
            for i in range(len(tokens)):
                    token = tokens[i % len(tokens)]
                    thread = threading.Thread(target=self.voiceLeave, args=(token, cid,gid,modes['mute'],modes['deafen'],modes['stream'],modes['video']))
                    thread.start()
                    threads.append(thread)
            for thread in threads:
                    thread.join()
        if mode in {"spam"}:
            if self.pushButtonVS_StartSpam.text() == "Spam":
                self.pushButtonVS_StartSpam.setText("Stop")
                voiceSwitch = True
                  
                threads = []
                for i in range(len(tokens)):
                        token = tokens[i % len(tokens)]
                        thread = threading.Thread(target=self.voiceSpam, args=(token, cid,gid,modes['mute'],modes['deafen'],modes['stream'],modes['video']))
                        thread.start()
                        threads.append(thread)
                for thread in threads:
                        thread.join() 
            else:
                self.pushButtonVS_StartSpam.setText("Spam")
                voiceSwitch = False                   
                                                 

class Go6Login():
    def __init__(self):
        super().__init__()
        self.ui = DraggableLoginWindow()
        self.ui.setupUi(self.ui)
        self.ui.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.ui.pushButtonConfirm.clicked.connect(self.on_login_clicked)

    def on_login_clicked(self):
        user_key = self.ui.lineEdit_KeyInput.text()

        if user_key:
            self.ui.close()
            with open('data/config.json', "r+") as config_file:
                data = json.load(config_file)
                data["user_key"] = user_key
                config_file.seek(0)
                json.dump(data, config_file, indent=4)
                config_file.truncate()
        else:
            print("Invalid input")

def runLoginPage():
    login_app = QtWidgets.QApplication(sys.argv)
    login_window = Go6Login()
    login_window.ui.show()
    login_app.exec_()
    runMainPage()
    
def runMainPage():    
    main_app = QtWidgets.QApplication(sys.argv)
    main_window = DraggableMainWindow()
    Go6(main_window)
    main_window.show()
    sys.exit(main_app.exec_())    

if __name__ == "__main__":
    runMainPage()


    

