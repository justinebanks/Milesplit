import bs4
import requests

from . import utils


# Make 'is_raw_results_page'


# Returns if the html code given is that of a Milesplit Result File Page (https://..../results)
def is_result_files_page(html: str) -> bool:
    soup = bs4.BeautifulSoup(html, "html.parser")
    result_file_list = soup.find("ul", id="resultFileList")

    if result_file_list == None:
        return False
    else:
        return True


# Returns a dictionary of each result file on a 'Milesplit Result File Page'
def request_result_files(url: str) -> dict:
    text = requests.get(url).text
    soup = bs4.BeautifulSoup(text, "html.parser")

    if is_result_files_page(text) == False:
        return {}

    result_file_list = soup.find("ul", id="resultFileList")

    result_files = {}

    for li in result_file_list.contents:
        if type(li) is not bs4.element.NavigableString:
            filename = utils.remove_extra_spacing(li.a.text)
            file_link = utils.remove_extra_spacing(li.a.attrs["href"])

            result_files[filename] = file_link
    
    return result_files


# Returns the string of raw results on a 'Milesplit Result Page' (https://....results/69493/raw)
def request_raw_results(url: str) -> str:
    id_ = url.split("/")[-1]

    print(id_)

    try:
        int(id_)

        text = requests.get(url + "/raw").text
        soup = bs4.BeautifulSoup(text, "html.parser")
        data = soup.find("pre")

        return data.text

    except ValueError:
        text = requests.get(url).text
        soup = bs4.BeautifulSoup(text, "html.parser")
        
        try:
            new_url = soup.find("small", class_="disclaimer").a.attrs["href"]

            text = requests.get(new_url).text
            soup = bs4.BeautifulSoup(text, "html.parser")
            data = soup.find("pre")
            
            return data.text
        
        except AttributeError:
            data = soup.find("pre")
            return data.text
        

