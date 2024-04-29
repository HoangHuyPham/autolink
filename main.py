from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as expected_conditions
import selenium.common.exceptions as exceptions
import utils, requests, time, os


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
        
        while(True):
            try:
                utils.changeCircuit()
                currentIP = utils.getCurrentIP()
                res = self.openChrome(url)
                attempt+=1
                self.writeLog(currentIP, attepmt=attempt, time=utils.getTimeHHmmss(time.time()-startTime), token=res["token"], username=res["userName"], statusCode=res["statusCode"])
            except KeyboardInterrupt:
                inform = "====end program with {} attempts //{}".format(attempt, time.ctime())
                utils.writeLog(url="app.log", error=f"====end program with {attempt} attempts")
                utils.killTor() 
                print(inform)   
                break
            except Exception as e:
                if (not isinstance(e, KeyboardInterrupt)):
                    utils.writeLog(error=e)
            
    def writeLog(self, ip, token="no token", username="no name", statusCode=-1, attepmt=0, time="unknown", wish="Have a good day (<Crtl+C> to Exit)"): 
        inviteCount = -1 
        try:
            inviteCount = utils.getInviteCount(username= self.username, password= self.password)
        except Exception as e:
            utils.writeLog(error=e)
            
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
            "userName":None
        }
        self.url = url
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        options.page_load_strategy = "eager"
        profile = webdriver.FirefoxProfile()
        profile.set_preference('network.proxy.type', 2)
        profile.set_preference('network.proxy.socks', '127.0.0.1')
        profile.set_preference('network.proxy.socks_port', utils.PROXY_PORT)
        profile.update_preferences()
        
        options.profile = profile
        driver = webdriver.Firefox(options=options)
        wait = WebDriverWait(driver=driver, timeout=1, ignored_exceptions=exceptions.NoSuchElementException)
        driver.get(url=url)
        
        # wait unti page appear
        tryingTime = 0
        try:
            wait.until(method=expected_conditions.title_contains("Đăng kí"), message="wait title...")
        except exceptions.TimeoutException as e:
            tryingTime = self.handleTimeoutError(driver=driver, tryingTimes=tryingTime, error=e.msg)
            if (tryingTime >= self.maxAttempts):
                return self.openChrome(url=self.url)
            
        
        # input username
        tryingTime = 0
        try:
            wait.until(method=expected_conditions.presence_of_element_located((By.NAME, "_token")), message="find _token...")
        except exceptions.TimeoutException as e:
            tryingTime = self.handleTimeoutError(driver=driver, tryingTimes=tryingTime, error=e.msg)
            if (tryingTime >= self.maxAttempts):
                return self.openChrome(url=self.url)
        
        token = driver.find_element(by=By.NAME, value="_token").get_attribute("value")
        username = utils.randomUserName(20)
        res = utils.postRequest(
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
                "XSRF-TOKEN": driver.get_cookie('XSRF-TOKEN').get("value"),
                "laravel_session": driver.get_cookie("laravel_session").get("value")
            },
            proxies = {
                'http': "socks5://127.0.0.1:{}".format(utils.PROXY_PORT),
                'https': "socks5://127.0.0.1:{}".format(utils.PROXY_PORT)
            }
        )
        
        
        resData["statusCode"] = res.status_code
        resData["token"] = token
        resData["userName"] = username
        res.close()
        driver.quit()
        
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
   
    