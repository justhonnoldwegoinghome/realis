import os
import requests
import pandas as pd
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from dotenv import load_dotenv

load_dotenv(override=True)

# Must refresh realis cookies and csrf for every session


class Realis:
    base_url = "https://www-ura-gov-sg.proxy.lib.sg"
    csrf = os.environ.get("REALIS_CSRF")
    headers = {
        "Cookie": os.environ.get("REALIS_COOKIES"),
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }

    @staticmethod
    def get_total_results(response):
        total_results = None
        try:
            soup = BeautifulSoup(response.content, "html.parser")
            panel_footer = soup.find("div", {"class": "panel-footer"})
            total_results_text = panel_footer.find("span", {"class": "hidden-xs"}).text
            total_results = int(total_results_text.split()[-2])
        except AttributeError:
            total_results = 0
        return total_results

    @classmethod
    def _request_sale_txns(
        cls,
        result_per_page,
        year,
        month,
    ):
        path = "reis/residentialTransactionSearch"
        return requests.post(
            urljoin(cls.base_url, path),
            headers=cls.headers,
            data={
                "resultPerPage": str(result_per_page),
                "displayResult": "true",
                "displayResultHeader": "true",
                "loadAnalysis": "false",
                "displayAnalysis": "false",
                "displayChart": "false",
                "displayAnalysisFilters": "false",
                "dashboardDisplay": "false",
                "locationDetails": [],
                "propertyTypeNo": [10, 11, 12, 20, 21, 31],
                "_propertyTypeNo": "1",
                "saleYearFrom": str(year),
                "saleMonthFrom": str(month),
                "saleYearTo": str(year),
                "saleMonthTo": str(month),
                "transactedPriceFrom": "",
                "transactedPriceTo": "",
                "pricePerUnitAreaFrom": "",
                "pricePerUnitAreaTo": "",
                "pricePerUnitAreaUOM": "PSF",
                "areaFrom": "",
                "areaTo": "",
                "areaUOM": "SQM",
                "_tenureType": "1",
                "blockHouseNumber": "",
                "levelFrom": "",
                "levelTo": "",
                "unitNumberFrom": "",
                "unitNumberTo": "",
                "_saleType": "1",
                "_typeofAreaLand": "on",
                "_typeofAreaStrata": "on",
                "_enblocYes": "on",
                "_enblocNo": "on",
                "_csrf": cls.csrf,
            },
        )

    @classmethod
    def extract_cur_year_sale_txns(cls):
        df = pd.DataFrame()

        for year in range(datetime.utcnow().year, datetime.utcnow().year + 1):
            for month in range(1, 13):
                print(f"{year}-{month}")

                total_results = cls.get_total_results(
                    cls._request_sale_txns(20, year, month)
                )
                print("Total results:", total_results)

                if total_results == 0:
                    continue

                response = cls._request_sale_txns(total_results, year, month)
                soup = BeautifulSoup(response.content, "html.parser")
                table = soup.find(
                    "table",
                    {"class": "table table-striped nowrap table-condensed width-100p"},
                )
                columns = [th.text.strip() for th in table.find_all("th")]
                data = []
                for tr in table.find_all("tr"):
                    row = [td.text.strip() for td in tr.find_all("td")]
                    if row:
                        data.append(row)
                df = pd.concat([df, pd.DataFrame(data, columns=columns)])
        return df
