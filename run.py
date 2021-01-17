import csv
from tqdm import tqdm
from primo.primo import PrimoSearch
import yaml
from alma.alma import BibRetriever


class ETD:
    def __init__(self, etd_from_csv):
        self.etd = self.__generate_etd(etd_from_csv)

    def __str__(self):
        return f"An ETD called {self.etd['title']} by {self.etd['author']}."

    def __repr__(self):
        return self.etd

    @staticmethod
    def __generate_etd(etd_data):
        return {
            "title": etd_data[1],
            "document_type": etd_data[2],
            "author": etd_data[3],
            "date_of_award": f"{etd_data[4]} {etd_data[5]}",
        }


def read_etd_csv(a_csv):
    etds = []
    with open(a_csv, "r") as original_csv:
        reader = csv.reader(original_csv, delimiter="|")
        for row in reader:
            if row[0] != "FILE":
                etds.append(ETD(row).etd)
    return etds


def lookup_etd_in_primo(list_of_etds):
    for etd in tqdm(list_of_etds):
        if etd["title"] != "":
            try:
                etd["mms"] = PrimoSearch(api_key).find_local_etd(etd["title"])
            except IndexError:
                etd["mms"] = "Cannot find in Primo based on title."
    return list_of_etds


def prep_mms_ids_for_searching(etds):
    mms_ids = [
        etd["mms"]
        for etd in etds
        if etd["mms"] != "Cannot find in Primo based on title."
    ]
    max_size = 99
    return [
        mms_ids[i * max_size : (i + 1) * max_size]
        for i in range((len(mms_ids) + max_size - 1) // max_size)
        if i != "Cannot find in Primo based on title."
    ]


def get_bib_records_from_alma(a_list_of_etds_as_dicts, alma_api):
    alma_data = []
    approved_searches = prep_mms_ids_for_searching(a_list_of_etds_as_dicts)
    for search in approved_searches:
        results = BibRetriever(alma_api, search).get_bibs()
        for result in results:
            alma_data.append(result)
    return alma_data


if __name__ == "__main__":
    api_key = yaml.safe_load(open("config.yml", "r"))["api_key"]
    missing_etds = read_etd_csv("data/test.csv")
    updated_etds = lookup_etd_in_primo(missing_etds)
    etds_found_in_alma = get_bib_records_from_alma(updated_etds, api_key)
    print(etds_found_in_alma)
