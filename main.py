from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as expected_conditions
import selenium.common.exceptions as exceptions
import utils, requests, time, os

class Main:
    tryingTimes = 10
    token = None
    url = None
    
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
                self.openChrome(url)
                attempt+=1
                utils.clear()
                self.writeLog(currentIP, attepmt=attempt, time=utils.getTimeHHmmss(time.time()-startTime))
            except KeyboardInterrupt:
                with open("error.log", "a+") as log:
                    inform = "====end program //{}\n".format(time.ctime())
                    log.write(inform)
                    print(inform)    
                break
            except Exception as e:
                with open("error.log", "a+") as log:
                    log.write(type(e)+str(e)+"\n")
            
    def writeLog(self, ip, attepmt, time):
        str = "[Current IP: {}, Attempt: {}, Timelapse: {}]\nCrtl+C to Exit".format(ip, attepmt, time)    
        print(str)
        
    def handleTimeoutError(self, driver, tryingTimes=0, maxAttemps = 3, error = None):
        tryingTimes +=1
         # after 3 times trying open page, will restart browser
        if (tryingTimes>=maxAttemps):
            with open("error.log", "a+") as log:
                if (isinstance(error, exceptions.TimeoutException)):
                    log.write(type(e)+str(error)+"\n")
            print("Attempt...{time} times (max: {max})\nTrying restart!".format(time=tryingTimes, max=maxAttemps))
            driver.quit()
            self.openChrome(url=self.url)
        else:
            print("Attempt...{time} times".format(time=tryingTimes))
            driver.quit()
        return tryingTimes
        
                    
    def openChrome(self, url):
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
        tryingTime = 0
        
        # wait unti page appear
        try:
            wait.until(method=expected_conditions.title_contains("Đăng kí"))
        except Exception as e:
            tryingTime=self.handleTimeoutError(driver=driver, tryingTimes=tryingTime, error=e)
            return
        
        # input username
        try:
            wait.until(method=expected_conditions.element_to_be_clickable(driver.find_element(by=By.NAME, value="_token")))
        except Exception as e:
            tryingTime=self.handleTimeoutError(driver=driver, tryingTimes=tryingTime, error=e)
            return
        token = driver.find_element(by=By.NAME, value="_token").get_attribute("value")
        if (token):
            print("Found token: ", token)
        
        
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
        
        if (res.status_code >= 200 and res.status_code < 400):
            print("Success! ", res.status_code)
        else:
            print("Failed! ", res.status_code)
        
        driver.quit()
        
        
        


if (__name__ == "__main__"):
    main = Main()
    link = input("Input u invite link: ")
    main.start(link)
  

