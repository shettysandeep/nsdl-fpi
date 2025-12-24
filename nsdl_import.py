""" Obtaining FPI investments data from NSDL """
import os
import requests
import zipfile
import calendar

class download_nsdl():
    def __init__(self, mnth, year):
        self.mnth = mnth
        self.year = year
        self.BASE_URL = "https://fpi.nsdl.co.in/web/StaticReports/statistics/zip/{}_{}.zip"
        self.header = {'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.4 Safari/605.1.15",
                       }
    
    def unzip_file(self, filepath=None):
        """Unzip file"""
        if os.path.exists(filepath):
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall("nsdl_data/")
    
    def extract_file(self):
        """Download and Unzip FPI data from NSDL"""
        url = self.BASE_URL.format(self.mnth, self.year)
        print(url)
        try:
            response = requests.get(url, headers=self.header, stream=True)
            response.raise_for_status()
            print(response.status_code)
            with open("data.zip", "wb") as f:
                f.write(response.content)
            self.unzip_file(filepath="data.zip") 
        except requests.exceptions.HTTPError as err:
            #if err==400:
            print("Link not active. Next in loop.")
            #raise SystemExit(err)       

if __name__ == '__main__' :
    month_names_abbr = [calendar.month_abbr[i] for i in range(1, 13)]
    for month in month_names_abbr:
        print("Downloadin... {}".format(month))
        nsdl = download_nsdl(month,"2025")
        nsdl.extract_file()
        continue

