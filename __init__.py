import pandas as pd
from sqlalchemy import create_engine
import requests
import psycopg2
import bs4

from . import get_meets, get_results, utils, errors


# Information About A Specified State-Year Combination
class MilesplitYearInfo:

    def __init__(self, state: str, year: int):
        self.state = state.lower()
        self.year = year
        self.meets = get_meets.get_meets_from_json(state, year)
    

    def __repr__(self):
        return f"MilesplitYearInfo(state=\"{self.state}\", year=\"{self.year}\")"
    

    def DataFrame(self) -> pd.DataFrame:
        return pd.DataFrame(self.meets)
    

    # Uploads the current information to a postgresql database (named f"{self.state}{self.year}")
    def upload_to_database(self):
        table_name = f"{self.state}{self.year}"

        # SQLAlchemy engine
        engine = create_engine(f'postgresql://{utils.db_username}:{utils.db_password}@{utils.db_host}:{utils.db_port}/{utils.db_name}')

        # Insert DataFrame into PostgreSQL
        print(f"Inserting data from {self.state} in the year {self.year} to the PostgreSQL table \"{table_name}\"...")
        self.DataFrame().to_sql(table_name, engine, if_exists='replace', index=True)


    def average_meets_per_month(self) -> float:
        total_meets = len(self.meets)
        return total_meets/12


    def meets_in_month(self, month: str) -> int:
        meets_in_month = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        month_int = utils.month_to_int(month)

        for meet in self.meets:
            meet_month = int(meet["date"].split("-")[1])
            meets_in_month[meet_month-1] += 1
        
        return meets_in_month[month_int-1]
    

    # Percentage of meets that year that took place in the specified month
    def perc_in_month(self, month) -> str:
        percent = self.meets_in_month(month) / len(self.meets) * 100

        return "%.2f" % percent + "%"
    

    # All Cities Mentioned as Locations for Meets in the List of Meets
    def get_cities(self) -> list:
        cities = []

        for meet in self.meets:
            cities.append(meet["city"])
        
        return list(set(cities))


    # Number of Meets Hosted that year in the specified city
    def meets_in_city(self, city: str) -> int:
        cities = []

        count = 0

        for meet in self.meets:
            cities.append(meet["city"])
        
        for i in cities:
            if city.lower() in i.lower():
                count += 1
        
        return count


    # Percent of Meets That Happened in the Specified City That Year
    def perc_in_city(self, city: str) -> str:
        percent = self.meets_in_city(city) / len(self.meets) * 100
        return "%.2f" % percent + "%"


    def has_table_in_database(self) -> bool:
        state = self.state
        year = self.year

        possible_table_name = f"{state}{year}"

        try:
            result = utils.access_database(utils.db_name, utils.db_username, utils.db_password, f"SELECT * FROM {possible_table_name}")
        except psycopg2.errors.UndefinedTable:
            return False

        return True


    # Gets meet count per day
    def get_meet_count_per_day(self) -> list[dict]:
        table_name = f"{self.state}{self.year}"

        if self.has_table_in_database():

            results = utils.access_database(utils.db_name, utils.db_username, utils.db_password, 
                f"""
                SELECT 
                    date, 
                    COUNT(date) AS "count", 
                    (SPLIT_PART(date, '-', 2))::int AS "month", 
                    (SPLIT_PART(date, '-', 3))::int AS "day",
                    (SPLIT_PART(date, '-', 1))::int AS "year"
                FROM {table_name}
                GROUP BY date
                ORDER BY COUNT(date) DESC;
                """)

            result_arr = \
                [{"full_date": i[0], "month": i[2], "day": i[3], "year": i[4], "count": i[1]} for i in results]
            
            return result_arr
        else:
            raise errors.NonexistentTableError(self.state, self.year, table_name)



class Meet:

    # 'meet_info' parameter is expected to be any indivisual index of 'MilesplitYearInfo.meets'
    def __init__(self, meet_info: dict):
        self.name = meet_info["name"]
        self.date = utils.str_to_date(meet_info["date"])
        self.city = meet_info["city"]
        self.link = meet_info["link"]
    

    def __repr__(self):
        return f"Meet(name=\"{self.name}\", date=\"{self.date}\")"


    def get_venue(self) -> str:
        result_page = requests.get(self.link).text
        soup = bs4.BeautifulSoup(result_page, "html.parser")

        basicInfo = soup.find("div", class_="basicInfo")

        try:
            return utils.remove_extra_spacing(basicInfo.find("div", class_="venueName").a.text)
        except Exception:
            return "None"


    def get_host(self) -> str:
        result_page = requests.get(self.link).text
        soup = bs4.BeautifulSoup(result_page, "html.parser")

        extendedInfo = soup.find("div", class_="extendedInfo")

        try:
            return utils.remove_extra_spacing(extendedInfo.find("div", class_="hostedBy").a.text)
        except Exception:
            return "None"


    # Retrieves Raw Meet Results
    def get_raw_results(self, file_name='', file_index=0) -> str:
        result_files = get_results.request_result_files(self.link)
        print()
        print("Getting Raw Results...")

        if len(result_files) == 0:
            print("Requesting Raw Results Immediately...")
            return get_results.request_raw_results(self.link)
        
        else:
            if file_name != '':
                print(f"Requesting Result File \"{file_name}\"")

                try:
                    result_link = result_files[file_name]
                except KeyError:
                    raise errors.InvalidResultFileError(file_name, self.link)

                return get_results.request_raw_results(result_link)
            
            else:
                selected_key = list(result_files.keys())[file_index]
                selected_value = list(result_files.values())[file_index]

                print("No file_name selected - Automatically Choosing index 0...")
                print("Result File Name: ", selected_key)

                return get_results.request_raw_results(selected_value)
    

    # Returns the number of line breaks in the meet's raw results
    def size(self) -> int:
        results = self.get_raw_results()
        count_line_breaks = len(results.split("\n"))

        return count_line_breaks
