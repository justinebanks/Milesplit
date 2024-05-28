import datetime
import psycopg2
import os

from . import errors


# Full Path to the Current Module
dir_path = os.path.dirname(os.path.realpath(__file__))


# PostgreSQL connection parameters (Must set these before accessing a database-related function)
db_username = 'postgres'
db_password = os.environ.get("POSTGRESQL_PWD")
db_host = 'localhost'
db_port = '5432'
db_name = 'milesplit'


def remove_extra_spacing(text: str) -> str:
    return text.replace("  ", "").replace("\n", "")


# Converts State Name to milesplit Subdomain Name (Florida -> fl, Alabama -> al)
def state_to_subdomain(state: str) -> str:
    states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
    subdomains = ["al", "ak", "az", "ar", "ca", "co", "ct", "de", "dc", "fl", "da", "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv", "wi", "wy"]
    

    # First Letter Uppercase, All Others Lowercase
    state = state[0].upper() + state.lower()[1:] 

    if state not in states:
        return "www"
    else:
        return subdomains[ states.index(state) ]


# Ex. January -> 1, February -> 2
def month_to_int(month: str) -> int:
    month_id = 0

    match month.lower():
        case "january": month_id = 1
        case "february": month_id = 2
        case "march": month_id = 3
        case "april": month_id = 4
        case "may": month_id = 5
        case "june": month_id = 6
        case "july": month_id = 7
        case "august": month_id = 8
        case "september": month_id = 9
        case "october": month_id = 10
        case "november": month_id = 11
        case "december": month_id = 12
    
    return month_id


# Converts a string in the format '%Y-%m-%d' from a string to a datetime.date
def str_to_date(date: str) -> datetime.date:
    year = int(date.split("-")[0])
    month = int(date.split("-")[1])
    day = int(date.split("-")[2])

    return datetime.date(year=year, month=month, day=day)


# Runs 'sql_code' on the database with the specified name, username, and password
def access_database(dbname: str, user: str, password: str, sql_code: str):
    # Set Up Connection To PostgreSQL Database
    conn = psycopg2.connect(dbname=dbname, user=user, password=password)
    cur = conn.cursor()

    # Executes specified SQL code and saves result
    cur.execute(sql_code)
    result = cur.fetchall()

    # Commit Database Updates and Close Connection
    conn.commit()
    cur.close()
    conn.close()

    return result


def format_database_result(result: list, column_names: tuple):
    new_result = []

    length = len(result[0])
    length2 = len(column_names)

    if length != length2:
        raise errors.FormatDatabaseError(length, length2)

    length_range = range(length)

    for row in result:
        dict_ = {}

        for i in length_range:
            dict_.update({column_names[i]: row[i]})
        
        new_result.append(dict_)
    
    return new_result