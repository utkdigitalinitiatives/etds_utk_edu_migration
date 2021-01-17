import csv
from tqdm import tqdm
from primo.primo import PrimoSearch
import yaml


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


if __name__ == "__main__":
    api_key = yaml.safe_load(open("config.yml", "r"))["api_key"]
    missing_etds = read_etd_csv("data/test.csv")
    updated_etds = lookup_etd_in_primo(missing_etds)
    print(updated_etds)
