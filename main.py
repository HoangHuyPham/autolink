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
                utils.clear()
                self.writeLog(currentIP, attepmt=attempt, time=utils.getTimeHHmmss(time.time()-startTime), token=res["token"], username=res["userName"], statusCode=res["statusCode"])
            except KeyboardInterrupt:
                with open("error.log", "a+") as log:
                    inform = "====end program with {} attempts //{}\n".format(attempt, time.ctime())
                    log.write(inform)
                    print(inform)    
                break
            except Exception as e:
                with open("error.log", "a+") as log:
                    log.write(str(e)+"\n")
            
    def writeLog(self, ip, token="no token", username="no name", statusCode=-1, attepmt=0, time="unknown"):
        str = "[Current IP: {}, Token: {}, Username: {}, Status: {}, Attempt: {}, Timelapse: {}]\n<Crtl+C> to Exit".format(ip, token, username, statusCode, attepmt, time)    
        print(str)
        
    def handleTimeoutError(self, driver, tryingTimes=0, maxAttemps = maxAttempts, error = "unknown"):
         # after 3 times trying open page, will restart browser
        tryingTimes += 1
        if (tryingTimes>=maxAttemps):
            with open("error.log", "a+") as log:
                log.write(str(error)+"\n")
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
        proxies = {
            'http': "socks5://127.0.0.1:{}".format(utils.PROXY_PORT),
            'https': "socks5://127.0.0.1:{}".format(utils.PROXY_PORT)
        }
        res = requests.post(
            url="https://ngocrongking.com/dang-ky",
            headers={
                'Content-Type':'application/x-www-form-urlencoded'
            },
            data={
                "_token": token,
                "username": username,
                "password": "1",
                "password_confirmation": "1"
            },
            cookies={
                "XSRF-TOKEN":driver.get_cookie('XSRF-TOKEN').get("value"),
                "laravel_session":driver.get_cookie("laravel_session").get("value")
            },
            proxies=proxies
          
            
        )
        driver.quit()
        resData["statusCode"] = res.status_code
        resData["token"] = token
        resData["userName"] = username
        
        return resData
        
        
        


if (__name__ == "__main__"):
    main = Main()
    link = input("Input u invite link: ")
    main.start(link)
  

