from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as expected_conditions
import selenium.common.exceptions as exceptions
import utils, requests, time

class Main:
    tryingTimes = 10
    token = None
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
                self.writeLog(currentIP, attepmt=attempt, time=utils.getTimeHHmmss(time.time()-startTime))
            except Exception as e:
                with open("error.log", "rb") as log:
                    print(e)
                    log.write(repr(e))
            
    def writeLog(self, ip, attepmt, time):
        str = "[Current IP: {}, Attempt: {}, Timelapse: {}]\nCrtl+C to Exit".format(ip, attepmt, time)    
        print(str)
                    
    def openChrome(self, url):
        
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
        except exceptions.TimeoutException:
            tryingTime+=1
            print("trying...{time} times".format(time=tryingTime))
            # after 3 times trying open page, will restart browser
            if (tryingTime>=self.tryingTimes):
                driver.quit()
                print("failed...{time} times, trying restart browser!".format(time=tryingTime))
                self.openChrome(url=url)
                return
        
        # input username
        try:
            wait.until(method=expected_conditions.element_to_be_clickable(driver.find_element(by=By.NAME, value="_token")))
        except exceptions.TimeoutException:
            tryingTime+=1
            print("trying...{time} times".format(time=tryingTime))
            # after 3 times trying open page, will restart browser
            if (tryingTime>=self.tryingTimes):
                driver.quit()
                print("failed...{time} times, trying restart browser!".format(time=tryingTime))
                self.openChrome(url=url)
                return
        token = driver.find_element(by=By.NAME, value="_token").get_attribute("value")
        if (token):
            print("found token: ", token)
        
        
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
  

