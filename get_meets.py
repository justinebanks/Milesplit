import bs4
import requests
import json
import os

from . import utils, errors


# Gets All Meets On The Specified Milesplit Result Page (https://{subdomain}.milesplit.com/results?{params})
def get_results_page(state="Florida", month=1, year=2023, page=1, verbose=False) -> list[dict]:

    subdomain = utils.state_to_subdomain(state)

    # Sends request to milesplit and finds the 'table' tag on that page
    req = requests.get(f"https://{subdomain}.milesplit.com/results?month={month}&year={year}&page={page}")
    soup = bs4.BeautifulSoup(req.text, "html.parser")
    meet_table = soup.find("table", class_="meets")

    meet_list = []

    # For row in table, append that row's information to 'meet_list'
    for row in meet_table.tbody.contents:
        if (type(row) is not bs4.element.NavigableString):
            if ("class" not in row.attrs):

                # Parsing name, link, and city
                name = utils.remove_extra_spacing(row.find("td", class_="name").a.text)
                link = utils.remove_extra_spacing(row.find("td", class_="name").a['href'])
                city = utils.remove_extra_spacing(row.find("td", class_="location").text)

                # Parsing and Formatting date
                date_ = utils.remove_extra_spacing(row.find("td", class_="date").span.text)

                month = int(date_.split("/")[0])
                day = int(date_.split("/")[1])

                month = month if month >= 10 else "0" + str(date_.split("/")[0])
                day = day if day >= 10 else "0" + str(date_.split("/")[1])

                date = f"{year}-{month}-{day}"

                meet_list.append({
                    "name": name, 
                    "date": date, 
                    "city": city,
                    "link": link,
                })

                if verbose:
                    print(f"{date}: Loading \"{name}\"... (Page: {page}, Month: {month}, Year: {year})")
    
    return meet_list



# Gets All Milesplit Meets of the Specified Year and Uploads Result to a JSON File
def get_meets_from_request(state: str, year: int, verbose=True) -> list:
    meet_list = []


    # Loops through first 10 pages of every month ajd appends it to 'meet_list'
    for month in range(1, 13):
        for page in range(1, 11):
            for meet in get_results_page(state=state, month=month, year=year, page=page, verbose=verbose):
                meet_list.append(meet)


    # Uploads Meet Array to JSON File ("{state}{year}.json")
    subdomain = utils.state_to_subdomain(state)

    with open(f"{utils.dir_path}\\years\\{subdomain}{year}.json", "w") as write_file:
        print(f"Dumping JSON to {subdomain}{year}.json...")

        string = json.dumps(meet_list, indent=4)
        write_file.write(string)

    return meet_list



# Gets the result data saved to specified JSON file
def get_meets_from_json(state: str, year: int, as_meet=False) -> list:
    subdomain = utils.state_to_subdomain(state)
    filename = f"{utils.dir_path}\\years\\{subdomain}{year}.json"

    if not os.path.exists(filename):
        raise errors.NoDataFoundError(state, year)

    with open(filename, "r") as f:
        data = json.load(f)
    
    if as_meet:
        #return list(map(lambda meet: Meet(meet), list(data)))
        pass
    else:
        return list(data)

