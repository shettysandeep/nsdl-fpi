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
                       #'Referer': "https://www.fpi.nsdl.co.in/web/Reports/ReportsListing.aspx",
                       #'Cookie': "NL865993ef027=080333663bab20000b23afa09f136281a18fa1ff4fe647af90503a76420e2baf422709e09563a178080cc5fa17113000a52ab5581e8166e85559f97b96d983c42982869e2a98ad399fd3c3e5bfea1290d1eeedee493f5858649125233290dca6; NL01ba3203=01e02e5d4a48942922e77088eda166f576f0cbae4a6dc1bb2416a5bc67d2fc0f0a3aaa97138990e33ca874f73109316232f9cc6fa0; ASP.NET_SessionId=0rbfl3l0v45oeseb3rbbkzpo; _fpi123456789="
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

