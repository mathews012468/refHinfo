from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import re
import csv
import time

def getRefInfo(url):
    driver.get(url)
    time.sleep(1)

    #scroll down to see the game info table
    END = "\uE010"
    webdriver.ActionChains(driver).send_keys(END).perform()

    soup = BeautifulSoup(driver.page_source, "html.parser")
    info = []

    #date is the first 8 numbers after the final slash
    date = url.split("/")[-1][:8]
    info.append(date)

    scorebox = soup.find("table", class_="linescore")
    for teamRow in scorebox.tbody.find_all("tr"):
        scores = teamRow.find_all("td")
        #team name
        info.append(scores[1].text)
        #score
        info.append(scores[-1].text)

    vegasLine = soup.find("th", string=re.compile("Vegas Line")).next_sibling.text
    overUnder = soup.find("th", string=re.compile("Over/Under")).next_sibling.text
    info.append(vegasLine)
    info.append(overUnder)

    try:
        for officialRow in soup.find("table", id="officials").tbody.find_all("tr"):
            official = " ".join([data.text for data in officialRow.find_all(True, recursive=False)])
            info.append(official)
    except AttributeError:
        print("No officials listed")

    return info

year = 2018
#start with week 1
for i in range(18,22):
    url = f"https://www.pro-football-reference.com/years/{year}/week_{i}.htm"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    gameLinks = []
    for game in soup.find("div", class_="game_summaries").find_all(True, recursive=False):
        #boxcore link
        gameLink = "https://www.pro-football-reference.com/" + game.find("td", class_="gamelink").a["href"]
        gameLinks.append(gameLink)

    print(gameLinks)

    driver = webdriver.Chrome()
    with open(f"ref{year}InfoWeek{i}.csv", "w") as f:
        refWriter = csv.writer(f)

        headers = ["Date", "Away Team", "Away Score", "Home Team", "Home Score", "Spread", "Over/Under", "Referee", "Umpire", "Down Judge", "Line Judge", "Back Judge", "Side Judge", "Field Judge"]
        refWriter.writerow(headers)

        for link in gameLinks:
            refInfo = getRefInfo(link)
            refWriter.writerow( refInfo )
            print(refInfo)


input("Return to exit")
driver.close()
