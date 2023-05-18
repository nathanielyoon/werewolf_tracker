import csv
import math
from datetime import datetime
import time

from selenium import webdriver
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

from werewolf import web_driver


WEREWOLF_URL = "https://apda.online/forum/topic/ww98-basicwolf"
FORUM_URL = "https://apda.online/forum/"
with open("data/players.csv", "r") as open_file:
    PLAYERS = {row["user"]: row for row in csv.DictReader(open_file)}


def log_online(driver: webdriver.Chrome) -> None:
    print("\nlogging online users", end="\r")
    driver.get(FORUM_URL)
    soup = BeautifulSoup(driver.page_source, "lxml")
    online = soup.find("div", id="statistics-online-users")
    users = [
        anchor.text for anchor in online("a", class_="profile-link")
        if anchor.text in PLAYERS
    ]
    print("online users:".ljust(20), end="\r")
    if users:
        for index, user in enumerate(users):
            if index == 0:
                print(f'online users:  {user}')
            else:
                print(f'{" "*15}{user}')
    else:
        print("online users: none")

    with open("data/online.csv", "a") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=("timestamp", "users"))
        writer.writerow({
            "timestamp": f'{datetime.now():%-m/%-d %-I:%M:%S%p}'.lower(),
            "users": ",".join(users)
        })


def log_post(driver: webdriver.Chrome, keys: list[str]) -> None:
    print("\nlogging posts", end="\r")
    driver.get(WEREWOLF_URL)
    soup = BeautifulSoup(driver.page_source, "lxml")
    last_page = soup.find("div", class_="pages")("a")[-1].get("href")

    driver.get(last_page)
    soup = BeautifulSoup(driver.page_source, "lxml")
    for blockquote in soup("blockquote"):
        blockquote.decompose()
    posts = soup("div", class_="post-element")
    new_count = 0
    for post in posts:
        key = post.find(class_="post-meta")("a")[-1].text[1:]
        if key not in keys:
            user = post.find(class_="mention-nice-name").text[1:]
            if user not in PLAYERS:
                continue
            if not (strong_text := post("strong")):
                vote = ("", "", "")
            else:
                vote = strong_text[-1].text
                if vote.startswith("Uploaded files"):
                    if len(strong_text) == 1:
                        vote = ("", "", "")
                    else:
                        vote = strong_text[-2].text
                        vote = assign_vote(vote.replace("\xa0", "").strip())
                elif PLAYERS[user]["role"] == "mod":
                    vote = ("", "", "")
                else:
                    vote = assign_vote(vote.replace("\xa0", "").strip())

            new_post = {
                "key": key,
                "user": user,
                "full_name": PLAYERS[user]["full_name"],
                "vote": vote[0],
                "original_vote": vote[1],
                "match": vote[2],
                "link": post.find(class_="post-meta")("a")[-1].get("href"),
                "post_timestamp": datetime.strptime(
                    post.find("div", class_="forum-post-date").text,
                    "%B %d, %Y, %I:%M %p"
                ).strftime("%-m/%-d %-I:%M:%S%p").lower(),
                "log_timestamp": f'{datetime.now():%-m/%-d %-I:%M:%S%p}'.lower()
            }
            with open("data/posts.csv", "a") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=list(new_post))
                writer.writerow(new_post)
            if new_count == 0:
                print(f'new post:      {key}'.ljust(17))
            else:
                print(f'{" "*15}{key}')
            new_count += 1
    if new_count == 0:
        last = max(int(key) for key in keys)
        print(f'new_post:      none (last: {last})'.ljust(17))


def assign_vote(vote: str) -> tuple[str, str]:
    if not vote:
        return None
    new_vote = vote.capitalize()
    items = sorted(
        [row["full_name"] for row in PLAYERS.values()],
        key=lambda name: (
            fuzz.partial_token_set_ratio(name, new_vote),
            fuzz.ratio(name, new_vote)
    ), reverse=True)
    match = fuzz.partial_token_set_ratio(items[0], new_vote)
    return (items[0] if match > 50 else "", vote, match)


def main():
    driver = web_driver.login()
    url = "https://apda.online/forum/topic/ww98-basicwolf"
    try:
        while True:
            with open("data/posts.csv", "r") as csv_file:
                keys = [row["key"] for row in csv.DictReader(csv_file)]
            log_online(driver)
            log_post(driver, keys)
            print(f'\nwaiting ({datetime.now():%-I:%M:%S%p})\n'.lower())
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nexiting")


if __name__ == "__main__":
    main()
