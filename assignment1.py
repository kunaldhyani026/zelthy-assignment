import requests
import pandas as pd
import time
import os


def fetch_data(url):
    """
    This function fetches data from the api url and returns in dict of array-like or dict format.

    :param url: api url to get data from
    :return: json data from the api response
    """
    
    response = requests.get(url)                    # GET call to the url
    data = response.json()                          # fetching json data from repsonse object
    return data


def json_to_dataframe(data):
    """
    This function creates dataframe from the given input dict or dict of array-like.

    :param data: dictionary or list of dicts
    :return: pandas dataframe contaning the data
    """
    
    df = pd.DataFrame(data)                         # creating pandas dataframe from dict
    return df


def export_excel(dataframe):
    """
    This function export the input dataframe into an excel file.

    :param dataframe: pandas dataframe to be exported to excel.
    :return: path to the saved excel file.
    """
    
    file_name = "file" + "_" + str(time.time()).split(".")[0] + ".xlsx"         # generating unique file_name for every file by appending timestamp
    dataframe.to_excel(file_name, index = False)                                # exporting dataframe to excel

    path_to_file = f"{os.getcwd()}/{file_name}"
    print(f"\n Excel saved at : {path_to_file}")

    return path_to_file


if __name__ == '__main__':
    
    api = "https://606f76d385c3f0001746e93d.mockapi.io/api/v1/auditlog"         # api to get the data from

    data = fetch_data(api)                                                      # calling fetch_data
    dataframe = json_to_dataframe(data)                                         # calling json_to_dataframe
    saved_file_path = export_excel(dataframe)                                   # calling export_excel
