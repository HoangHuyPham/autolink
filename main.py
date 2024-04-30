from selenium import webdriver
import selenium.common
import selenium.types
import selenium.webdriver
import selenium.webdriver.chrome
import selenium.webdriver.chrome.remote_connection
import selenium.webdriver.common
from selenium.webdriver.common.by import By
import selenium.webdriver.remote
import selenium.webdriver.remote.errorhandler
import selenium.webdriver.remote.remote_connection
import selenium.webdriver.remote.webdriver
import selenium.webdriver.support
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as expected_conditions
import selenium.common.exceptions as exceptions
import utils, requests, time, os, selenium, re, urllib3


class Main:
    token = None
    url = None
    maxAttempts = 5
    username = None
    password = None
    
    def init(self):
        pass
    
    def start(self, url):
        print("enjoy :)")
        currentIP = None
        attempt = 0
        startTime = time.time()
        loop = True
        while(loop):
            try:
                count=1
                while (not utils.getCurrentIP(checkConnect=True)):
                    utils.clear()
                    print(f"Lost Connect!{"."*(count%4)}")
                    time.sleep(1.2)
                    count = count%4+1
                resCode1= utils.changeCircuit()
                print("CHANGE IP")
                currentIP = utils.getCurrentIP()
                res = self.openChrome(url)
                attempt+=1
                self.writeLog(currentIP, attepmt=attempt, time=utils.getTimeHHmmss(time.time()-startTime), token=res["token"], username=res["userName"], statusCode=res["statusCode"])
            except Exception as e:
                if (not isinstance(e, KeyboardInterrupt)):
                    utils.writeLog(error=e)
            except KeyboardInterrupt:
                try:
                    inform = "====end program with {} attempts //{}".format(attempt, time.ctime())
                    utils.writeLog(url="app.log", error=f"====end program with {attempt} attempts")
                    utils.killTor()   
                except:
                    pass
                finally:
                    loop = False  
                    utils.clear()
                    print(inform)    
            
    def writeLog(self, ip, token="no token", username="no name", statusCode=-1, attepmt=0, time="unknown", wish="Have a good day (<Crtl+C> to Exit)"): 
        inviteCount = -1 
        try:
            inviteCount = utils.getInviteCount(username= self.username, password= self.password)
        except Exception as e:
            utils.writeLog(error=e)
        utils.clear()
        print(f"Attempts: {attepmt}")
        if (inviteCount != -1):
            print(f"Current account: {self.username}")
        dataTable = {
            "Invite":inviteCount,
            "IP Register":ip,
            "Username":username,
            "Status":statusCode,
            "Time":time
        }
        utils.printTable(dataTable)
        print(f"<Crtl+C> to Exit")
        print(utils.generateWish(dataTable=dataTable, wish=wish))
     
        
    def handleTimeoutError(self, driver, tryingTimes=0, maxAttemps = maxAttempts, error = "unknown"):
         # after 3 times trying open page, will restart browser
        tryingTimes += 1
        if (tryingTimes>=maxAttemps):
            utils.writeLog(error=error)
            print("{time} times (max: {max})\nTrying restart!".format(time=tryingTimes, max=maxAttemps))
            driver.quit()
        else:
            print("{err}{time} times".format(time=tryingTimes, err=str(error)))
        
        return tryingTimes
                    
    def openChrome(self, url) -> dict:  
        resData = {
                "token":None,
                "statusCode":None,
                "userName":None,
        }
        self.url = url
        
        with requests.get(url=url, headers={
            'Content-Type':'application/x-www-form-urlencoded',
            'Referer': 'https://ngocrongking.com/',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
            },
            proxies = {
                'http': "socks5://127.0.0.1:{}".format(utils.PROXY_PORT),
                'https': "socks5://127.0.0.1:{}".format(utils.PROXY_PORT)
            }, allow_redirects=False) as resp1:
        
            print("GET page")
            
            with requests.get(url="https://ngocrongking.com/dang-ky", headers={
                'Content-Type':'application/x-www-form-urlencoded',
                'Referer': 'https://ngocrongking.com/',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                },
                proxies = {
                    'http': "socks5://127.0.0.1:{}".format(utils.PROXY_PORT),
                    'https': "socks5://127.0.0.1:{}".format(utils.PROXY_PORT)
                },cookies={
                    # "XSRF-TOKEN": driver.get_cookie('XSRF-TOKEN').get("value"),
                    # "laravel_session": driver.get_cookie("laravel_session").get("value")
                    "XSRF-TOKEN": resp1.cookies.get("XSRF-TOKEN"),
                    "laravel_session": resp1.cookies.get("laravel_session")
                }) as resp2:
            
                inputTag = re.search('<input name="_token" type="hidden" value=".+">', resp2.content.decode("utf-8"))
                if (inputTag):
                    valueAttr = re.search('value=".+"', inputTag.group()).group().split("value=")[1]
                else:
                    valueAttr = ""
                token = valueAttr.removeprefix('"').removesuffix('"')

                print("GET TOKEN page")
                
        # token = driver.find_element(by=By.NAME, value="_token").get_attribute("value")
        username = utils.randomUserName(20)
        print(f"REGIST {url}")
        with utils.postRequest(
            url = "https://ngocrongking.com/dang-ky",
            payload={
                "_token": token,
                "username": username,
                "password": "1",
                "password_confirmation": "1"
                },
            headers={
                'Content-Type':'application/x-www-form-urlencoded'
            },
            cookies={
                # "XSRF-TOKEN": driver.get_cookie('XSRF-TOKEN').get("value"),
                # "laravel_session": driver.get_cookie("laravel_session").get("value")
                "XSRF-TOKEN": resp2.cookies.get("XSRF-TOKEN"),
                "laravel_session": resp2.cookies.get("laravel_session")
            },
            proxies = {
                'http': "socks5://127.0.0.1:{}".format(utils.PROXY_PORT),
                'https': "socks5://127.0.0.1:{}".format(utils.PROXY_PORT)
            }
        ) as resp3:
            resData["statusCode"] = resp3.status_code
            resData["token"] = token
            resData["userName"] = username
    
        return resData
        
    def preStart(self):
        try:
            with open("account", "r") as f:
                data = f.readline()
                if (data):
                    answ = input(f"Detect an account ({data.split(":")[0]})! Do u wanna track it?(Y/N): ")
                    if (answ):
                        if (answ.upper() == "Y"):
                            if (data):
                                arr = data.split(":")
                            if (arr.__len__()>=2):
                                self.username = arr[0]
                                self.password = arr[1]
                            if (not (self.username and self.password)):
                                print("Lack of field!...")
                                self.username = None
                                self.password = None
                        else:
                            print("Input username:password //Inorge (Enter) if no use invite count tracking!")
                            inputUP = input("Input here(username:password): ")
                            if (inputUP):
                                arr = inputUP.split(":")
                                if (arr.__len__()>=2):
                                    self.username = arr[0]
                                    self.password = arr[1]
                                    if (not (self.username and self.password)):
                                        ("Lack of field!...")
                                        self.username = None
                                        self.password = None
                                    else:
                                        with open("account", "w+") as f:
                                            f.write(inputUP)
                                else:
                                    print("Lack of field!...")
                            else:
                                print("Inorge!...")
                else:
                    print("Input username:password //Inorge (Enter) if no use invite count tracking!")
                    inputUP = input("Input here(username:password): ")
                    if (inputUP):
                        arr = inputUP.split(":")
                        if (arr.__len__()>=2):
                            self.username = arr[0]
                            self.password = arr[1]
                            if (not (self.username and self.password)):
                                print("Lack of field!...")
                                self.username = None
                                self.password = None
                            else:
                                with open("account", "w+") as f:
                                    f.write(inputUP)
                        else:
                            print("Lack of field!...")
                    else:
                        print("Inorge!...")
        except FileNotFoundError as e:
            utils.writeLog(error=e)
            open("account", "w+")
            self.preStart()

if (__name__ == "__main__"):
    main = Main()
    try:
        link = input("Input u invite link: ")
        main.preStart()
        main.start(link)
    except KeyboardInterrupt as e:
        utils.writeLog(url="app.log", error=f"====end program with 0 attempts")
        utils.killTor() 
   
    