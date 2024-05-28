

# Raised When 'get_meets.get_meets_from_json()' References a Non-Existent JSON File
class NoDataFoundError(Exception):
    def __init__(self, state, year):
        self.state = state
        self.year = year
        self.message = f"There is no existing JSON data pertaining to \"{state} {year}\". Find data on it by running 'get_meets_from_request' with the same arguments"
        
        super().__init__(self.message)


# Raised when an attempt is made to get the raw results of a meet (Meet.get_raw_results()), but the specified result file doesn't exist
class InvalidResultFileError(Exception):
    def __init__(self, filename, meet_link):
        self.filename = filename
        self.link = meet_link
        self.message = f"Invalid result file name \"{filename}\" for the meet \"{meet_link}\""
        
        super().__init__(self.message)


# Raised when a request is made to a PostgreSQL table that doesn't exist
class NonexistentTableError(Exception):
    def __init__(self, state, year, table_name):
        self.state = state
        self.year = year
        self.table_name = table_name
        self.message = f"There is no PostgreSQL table named \"{table_name}\" for info from '{state}' in the year '{year}'"

        super().__init__(self.message)


# Raised when the 'format_database_result' has a column_names parameter with a length that doesn't match what the result parameter suggests
class FormatDatabaseError(Exception):
    def __init__(self, length1, length2):
        self.length1 = length1
        self.length2 = length2
        self.message = f"The database result suggests that the table has {length1} columns, but the array of column names entered as argument 2 suggests the existence of {length2}"

        super().__init__(self.message)