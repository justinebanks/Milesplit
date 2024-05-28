from . import utils
import requests
import bs4


Level = {
    "HS_Boys": "high-school-boys",
    "HS_Girls": "high-school-girls",
    "MS_Boys": "middle-school-boys",
    "MS_Girls": "middle-school-girls",
    "Club_Boys": "club-boys",
    "Club_Girls": "club-girls",
}

Season = {
    "Outdoor": "outdoor-track-and-field",
    "Indoor": "indoor-track-and-field",
    "XC": "cross-country"
}

Grade = {
    "6th": "6th-grade",
    "7th": "7th-grade",
    "8th": "8th-grade",
    "FR": "freshman",
    "SO": "sophomore",
    "JR": "junior",
    "SR": "senior",
    "all": ""
}

Accuracy = {
    "all": "all",
    "fat": "fat",
    "legal": "legal"
}

def get_rankings_page(state: str, level: str, season: str, year: int, grade=Grade["all"], accuracy=Accuracy["all"]):
    state = utils.state_to_subdomain(state)
    req = requests.get(f"https://{state}.milesplit.com/rankings/leaders/{level}/{season}?year={year}&accuracy={accuracy}&grade={grade}")
    soup = bs4.BeautifulSoup(req.text, "html.parser")

    table = soup.find("table", id="rankingsTable")
    rankings = []

    for row in table.tbody.contents:
        if type(row) is not bs4.element.NavigableString:
            if "class" not in row.attrs:
                event = row.find("td", class_="event")
                time = row.find("td", class_="time")
                name = row.find("td", class_="name")
                meet = row.find("td", class_="meet")
                date = meet.find("div", class_="date")

                ranking = {
                    "event": utils.remove_extra_spacing(event.a.text), 
                    "time": utils.remove_extra_spacing(time.contents[0].text), 
                    "name": utils.remove_extra_spacing(name.div.a.text), 
                    "meet": utils.remove_extra_spacing(meet.div.a.text), 
                    "date": utils.remove_extra_spacing(date.time.text) 
                }

                rankings.append(ranking)

    return rankings


