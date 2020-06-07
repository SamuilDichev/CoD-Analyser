import concurrent
import csv
import json
from concurrent import futures

import requests

from src.exception import CoDTrackerApiException
from src.player import Player
import numpy as np
import matplotlib.pyplot as plt

class Match:
	def __init__(self, match_id):
		self.match_id = str(match_id)
		self.players = []

		match_api = "https://api.tracker.gg/api/v1/warzone/matches/{match_id}"
		response = requests.get(match_api.format(match_id=self.match_id))
		if response.status_code != 200:
			raise CoDTrackerApiException(response.text)

		data = json.loads(response.text)
		self.timestamp = data["data"]["metadata"]["timestamp"]
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
	kdr_list = []
	spm_list = []
	with open(match.timestamp + "_" + match.match_id + ".csv", "w") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=["username", "platform", "K/D", "Score Per Minute"])
		writer.writeheader()
		pc_players = 0
		console_players = 0
		for player in match.players:
			if player.kdr_lifetime:
				kdr_list.append(player.kdr_lifetime)
			if player.spm_lifetime:
				spm_list.append(player.spm_lifetime)
			if player.platform == "battlenet":
				pc_players += 1
			elif player.platform == "xbl" or player.platform == "psn":
				console_players += 1
			writer.writerow({
				"username": player.username,
				"platform": player.platform,
				"K/D": player.kdr_lifetime,
				"Score Per Minute": player.spm_lifetime
			})
		writer.writerow({
			"username": "AVERAGE for %d / %d players" % (len(kdr_list), len(match.players)),
			"platform": "PC: %d, Console: %d" % (pc_players, console_players),
			"K/D": sum(kdr_list) / len(kdr_list),
			"Score Per Minute": sum(spm_list) / len(spm_list)
		})

	generate_distribution_graphs(match, kdr_list, spm_list)


def generate_distribution_graphs(match: Match, kdr_list, spm_list):
	fig, axs = plt.subplots(1, 2)
	fig.tight_layout()
	# 1920x540 (Half height of 1080p)
	fig.set_size_inches(19.2, 5.4)

	# KDR Graph
	avg_kdr = round(sum(kdr_list) / len(kdr_list), 2)
	axs[0].set_title('K/D (Avg: {avg}) for match {match_id}'.format(avg=avg_kdr, match_id=match.match_id))
	axs[0].set(xlabel='K/D', ylabel='# of players')
	axs[0].set_xlim(0, 5.1)
	axs[0].set_xticks([tick/10 for tick in range(5, 51, 5)])
	axs[0].hist(kdr_list, np.arange(0, 5, 0.1), alpha=0.5, histtype='bar', ec='black')

	# SPM Graph
	avg_spm = round(sum(spm_list) / len(spm_list))
	axs[1].set_title('Score/min (Avg: {avg}) for match {match_id}'.format(avg=avg_spm, match_id=match.match_id))
	axs[1].set(xlabel='Score/min', ylabel='# of players')
	axs[1].set_xlim(0, 510)
	axs[1].set_xticks([tick*10 for tick in range(5, 51, 5)])
	axs[1].hist(spm_list, np.arange(0, 500, 10), alpha=0.5, histtype='bar', ec='black')

	plt.savefig(match.timestamp + "_" + match.match_id + "_" + str(avg_kdr) + "_" + str(avg_spm) + ".png")

def main():
	match_ids = input("Enter match ID(s) separated by a comma (from cod.tracker.gg): ")
	for match_id in match_ids.split(","):
		print("------ Analysing match " + match_id + " ------")
		match = Match(match_id.strip())
		output_results(match)


if __name__ == "__main__":
	main()
