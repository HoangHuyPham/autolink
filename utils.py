import random as rd
import socket, os, time
from subprocess import Popen,CREATE_NEW_CONSOLE,PIPE
import psutil, requests, json, urllib3

CONTROL_PORT = 9051
PROXY_PORT = 9050
GET_IP = "https://api.ipify.org"

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
    
def runTor():
    overwriteTorrc()
    killTor()
    print("try running Tor...")
    os.startfile(__file__+"\\..\\Browser\\TorBrowser\\Tor\\tor.exe")
    
    while(not tryConnectToTor()):
        time.sleep(1)
        print("wait for Tor...")
    print("run Tor success...")
    
# kill tor if its exist
def killTor():
    pid = get_pid("tor.exe")
    if (pid):
        print("kill Tor...")
        os.system("taskkill -f -pid {}".format(pid))
    else:
        print("not found Tor process!")
       
    
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

