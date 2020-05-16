import concurrent
import csv
import json
from concurrent import futures

import requests

from src.exception import CoDTrackerApiException
from src.player import Player


class Match:
	def __init__(self, match_id):
		self.match_id = str(match_id)
		self.players = []

		match_api = "https://api.tracker.gg/api/v1/warzone/matches/{match_id}"
		response = requests.get(match_api.format(match_id=self.match_id))
		if response.status_code != 200:
			raise CoDTrackerApiException(response.text)

		data = json.loads(response.text)
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


def output_results(match: Match):
	with open(match.match_id + ".csv", "w") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=["username", "platform", "K/D", "Score Per Minute"])
		writer.writeheader()

		kdr_list = []
		spm_list = []
		for player in match.players:
			if player.kdr_lifetime:
				kdr_list.append(player.kdr_lifetime)
			if player.spm_lifetime:
				spm_list.append(player.spm_lifetime)
			writer.writerow({
				"username": player.username,
				"platform": player.platform,
				"K/D": player.kdr_lifetime,
				"Score Per Minute": player.spm_lifetime
			})
		writer.writerow({
			"username": "AVERAGE for %d / %d players" % (len(kdr_list), len(match.players)),
			"platform": "ALL",
			"K/D": sum(kdr_list) / len(kdr_list),
			"Score Per Minute": sum(spm_list) / len(spm_list)
		})


def main():
	match_id = input("Enter a match ID (from cod.tracker.gg): ")
	match = Match(match_id)
	output_results(match)


if __name__ == "__main__":
	main()
