import random as rd
import socket, os, time
from subprocess import Popen,CREATE_NEW_CONSOLE,PIPE
import requests.cookies
import psutil, requests, json, urllib3, math, re

CONTROL_PORT = 9051
PROXY_PORT = 9050
GET_IP = "https://api.ipify.org"
MAX_LEN = 14

# return inclusive min to max 
def randomUserName(len:int=10)->str:
    res = ""
    
    for i in range(len):
        r = rd.random()
        if (r >= 0.6):
            res += str(rd.randint(0,9))
        elif (r > 0.3):
            res += chr(rd.randint(65,90))
        else:
            res += chr(rd.randint(97,122))
        
    return res

        
def command(cmd:str, value:str=None)->str|None:
    s = socket.socket()
    resp = None
    try:
        s.connect(("localhost", CONTROL_PORT))
        #AUTHENTICATE 
        s.send("{command}\n".format(command="AUTHENTICATE").encode("utf-8"))
        s.recv(1024)
        
        if (value):
            s.send("{command} {value}\n".format(command=cmd, value=value).encode("utf-8"))
        else:
            s.send("{command}\n".format(command=cmd).encode("utf-8"))
            
        resp = s.recv(1024).decode("utf-8")
   
    except ConnectionError:
        print("Can't connect to ControlPort! Trying restart...")
        handleConnectError()
        return command(cmd=cmd, value=value)
    finally:
        s.close()
    return resp

def changeCircuit()->int:
    return int(command("SIGNAL", "NEWNYM").split(" ")[0])

def handleConnectError():
    runTor()
    
def generateWish(dataTable={}, wish="No thing", maxLen=MAX_LEN):
    return f"{("="*math.floor((dataTable.items().__len__()*maxLen+3*dataTable.items().__len__()*2- wish.__len__())/2))+wish+("="*math.floor((dataTable.items().__len__()*maxLen+3*dataTable.items().__len__()*2- wish.__len__())/2)):^{dataTable.items().__len__()*maxLen+3*dataTable.items().__len__()*2+5}}"
    
def runTor():
    overwriteTorrc()
    killTor()
    print("Try running Tor...")
    os.system(f'start /b {os.getcwd()+"\\Browser\\TorBrowser\\Tor\\tor.exe"}')
    attemp = 0
    while(not tryConnectToTor()):
        attemp+=1
        if (attemp >= 15):
            runTor()
            break
        time.sleep(1)
        writeLog("app.log", f"Wait for Tor...{attemp} //{time.ctime()}")
    
    
# kill tor if its exist
def killTor():
    time.sleep(0.1)
    pid = get_pid("tor.exe")
    print("Kill Tor...")
    if (pid):    
        try:
            if (os.system("taskkill -f -pid {}".format(pid)) == 0):
                print("Kill Tor success!")
            else:
                print("Kill Tor failed! Trying again...")
                killTor()
        except Exception as e:
            writeLog(error=e)
            killTor()
    else:
        print("Not found Tor process!")
       
    
def get_pid(name:int=None)-> int:
    if (not name):
        return -1
    pid = None

    for proc in psutil.process_iter():
        
        if proc.name().startswith(name):
            pid = proc.pid
            break
    return pid

def tryConnectToTor():
    s = socket.socket()
    isSuccess = True
    resp = -1
    try:
        s.connect(("localhost", CONTROL_PORT))
        s.send("AUTHENTICATE\n".encode("utf-8"))
        resp = int(s.recv(1024).decode("utf-8").split(" ")[0])
        
    except ConnectionError:
        isSuccess = False
    finally:
        s.close()
    return isSuccess and resp == 250

def getCurrentIP():
    proxies = {
        'http': "socks5://127.0.0.1:{}".format(PROXY_PORT),
        'https': "socks5://127.0.0.1:{}".format(PROXY_PORT)
    }
    try:
        resp = requests.get(GET_IP, proxies=proxies)
    except:
        try:
            resp = requests.get(GET_IP)
        except:
            return None

    return resp.content.decode("utf-8")
    

def overwriteTorrc():
    with open(os.environ.get("APPDATA")+"\\tor\\torrc", encoding="utf-8", mode="w") as file:
        file.write("SOCKSPort 9050\nLog notice stdout\nControlPort 9051\nCookieAuthentication 0")

def getTimeHHmmss(sec):
    return "{h}:{m}:{s}".format(h=time.gmtime(sec).tm_hour, s=time.gmtime(sec).tm_sec, m=time.gmtime(sec).tm_min)

def clear():
    os.system("cls")
    
def postRequest(url, payload={}, headers={}, cookies={}, proxies={}, allowRedirect=True) -> requests.Response:
    res = requests.post(
        url= url,
        headers=headers,
        data=payload,
        cookies=cookies,
        proxies=proxies,
        allow_redirects=allowRedirect
    )
    return res

def printTable(table:dict={}, maxLen:int = MAX_LEN,padding =3, replace:str = "."):
    keys = ""
    values = ""
    for key in table.keys():
        keys += f"{key:^{maxLen+padding*2}}{"|":>}"
    print(keys)
    
    for index, val in enumerate(table.values()):
        val = str(val)
        if (val.__len__()>maxLen):
            val = val[:maxLen-1:]+replace*3
        
        values += f"{val:^{maxLen+padding*2}}{"|":>}" 
    print(values)

def getInviteCount(username = None, password = None):
    inviteCount = -1
    if (not (username and password)):
        return inviteCount
    resp1:requests.Response = requests.get("https://ngocrongking.com/dang-nhap", headers={
        'Content-Type':'application/x-www-form-urlencoded',
        'Referer': 'https://ngocrongking.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    })

    inputTag = re.search('<input name="_token" type="hidden" value=".+">', resp1.content.decode("utf-8"))
    if (inputTag):
        valueAttr = re.search('value=".+"', inputTag.group()).group().split("value=")[1]
    else:
        valueAttr = ""

    _token = valueAttr.removeprefix('"').removesuffix('"')

    resp2 = postRequest(
    url="https://ngocrongking.com/dang-nhap",
    headers={
        'Content-Type':'application/x-www-form-urlencoded',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://ngocrongking.com/dang-nhap',
    },
    cookies={
        "laravel_session": resp1.cookies.get("laravel_session"),
        "XSRF-TOKEN": resp1.cookies.get('XSRF-TOKEN')
    },
    payload={
        "_token": _token,
        "username": username,
        "password": password
    },
    allowRedirect=False
    )

    resp3 = requests.get("https://ngocrongking.com",headers={
        'Content-Type':'application/x-www-form-urlencoded',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://ngocrongking.com/dang-nhap'
    }, cookies={
    "laravel_session": resp2.cookies.get("laravel_session"),
    "XSRF-TOKEN": resp2.cookies.get('XSRF-TOKEN')
    })

    resp4 = requests.get("https://ngocrongking.com/link-gioi-thieu", cookies={
    "laravel_session": resp3.cookies.get("laravel_session"),
    "XSRF-TOKEN": resp3.cookies.get('XSRF-TOKEN')
    },headers={
    'Content-Type':'application/x-www-form-urlencoded',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://ngocrongking.com/'
    })

    inviteTag = re.search(r"Số lần sử dụng: <strong>\d+</strong>", resp4.content.decode("utf-8"))
    if (inviteTag):
        inviteCount = int(re.search(r"\d+", inviteTag.group()).group())

    resp1.close()
    resp2.close()
    resp3.close()
    resp4.close()
    
    return inviteCount

def writeLog(url="error.log", error:Exception="Unknown error", appendDate=True):
    with open(url, "a+") as log:
        if (appendDate):
            log.write(f"{str(error)} //{time.ctime()}"+"\n")
        if (appendDate):
            log.write(f"{str(error)}"+"\n")
        
