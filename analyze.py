import csv
from datetime import datetime


def main():
    with open("data/players.csv", "r") as csv_file:
        players = list(csv.DictReader(csv_file))
    with open("data/votes.csv", "r") as csv_file:
        votes = list(csv.DictReader(csv_file))
    wolves = [player["user"] for player in players if "wolf" in player["role"]]
    targets = {player["full_name"]: player["user"] for player in players}
    daily_votes = {timestamp: [vote for vote in votes if datetime.strptime(
        "22/"+vote["timestamp"].split(" ")[0], "%y/%m/%d"
    ) == timestamp] for timestamp in sorted(set(datetime.strptime(
        "22/"+vote["timestamp"].split(" ")[0], "%y/%m/%d"
    ) for vote in votes))}
    for key, value in daily_votes.items():
        wolf_wolf = [
            (vote["name"], vote["vote"]) for vote in value
            if vote["user"] in wolves
            and targets[vote["vote"]] in wolves
        ]
        wolf_villager = [
            vote for vote in value
            if vote["user"] in wolves
            and targets[vote["vote"]] not in wolves
        ]
        villager_wolf = [
            vote for vote in value
            if vote["user"] not in wolves
            and targets[vote["vote"]] in wolves
        ]
        villager_villager = [
            vote for vote in value
            if vote["user"] not in wolves
            and targets[vote["vote"]] not in wolves
        ]
        for vote in wolf_wolf:
            total_votes = sum(
                1 for other_vote in value
                if other_vote["vote"] == vote[1]
            )
            other_votes = sum(
                1 for other_vote in value
                if other_vote["vote"] != vote[1]
            )
            print(f'{vote[0]} -> {vote[1]} ({total_votes}-{other_votes})')


if __name__ == "__main__":
    main()
