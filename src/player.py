import requests
from bs4 import BeautifulSoup

import src.selectors as selector


class Player:
	def __init__(self, platform, username):
		self.platform = platform
		self.username = username
		self.kdr_lifetime = None
		self.spm_lifetime = None
		self.kdr_weekly = None
		self.spm_weekly = None

		player_api = "https://cod.tracker.gg/warzone/profile/{platform}/{username}/overview"
		response = requests.get(player_api.format(platform=platform, username=username))
		if response.status_code == 200:
			try:
				page = BeautifulSoup(response.content, "html.parser")
				self.kdr_lifetime = float(page.select_one(selector.BATTLE_ROYALE_LIFETIME_KDR).text)
				self.spm_lifetime = float(page.select_one(selector.BATTLE_ROYALE_LIFETIME_SPM).text)
				self.kdr_weekly = float(page.select_one(selector.BATTLE_ROYALE_WEEKLY_KDR).text)
				self.spm_weekly = float(page.select_one(selector.BATTLE_ROYALE_WEEKLY_SPM).text)
			except AttributeError as e:
				print("ERROR: %s %s - " % (platform, username), e)
		else:
			print("ERROR: %s %s's profile could not be found or is private." % (platform, username))
