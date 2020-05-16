import concurrent
import json
from concurrent import futures

import requests

from src.exception import CoDTrackerApiException
from src.player import Player


class Match:
	def __init__(self, match_id):
		mycod_api = "api/papi-client/ce/v1/title/{title}/platform/{platform}/match/{matchId}/matchMapEvents"
		match_api = "https://api.tracker.gg/api/v1/warzone/matches/{match_id}"
		response = requests.get(match_api.format(match_id=match_id))
		if response.status_code != 200:
			raise CoDTrackerApiException(response.text)

		data = json.loads(response.text)

		self.players = []
		segments = data["data"]["segments"]
		executor = concurrent.futures.ThreadPoolExecutor(20)
		futures = [executor.submit(self.scrape_player, segment) for segment in segments]
		concurrent.futures.wait(futures)

	def scrape_player(self, segment):
		self.players.append(
			Player(
				segment["attributes"]["platformSlug"],
				segment["attributes"]["platformUserIdentifier"]
			)
		)


def main():
	match_id = input("Enter a match ID (from cod.tracker.gg): ")
	match = Match(match_id)

	kdr_list = []
	spm_list = []
	for player in match.players:
		if player.kdr_lifetime:
			kdr_list.append(player.kdr_lifetime)
		if player.spm_lifetime:
			spm_list.append(player.spm_lifetime)

	print(
		"Scraped the K/D of %s / %s total players with average k/d %s and average Score Per Minute %s"
		% (
			len(kdr_list),
			len(match.players),
			sum(kdr_list) / len(kdr_list),
			sum(spm_list) / len(spm_list)
		)
	)


if __name__ == "__main__":
	main()
