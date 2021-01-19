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


class TraceMigrater:
    def __init__(self, primo_etds, alma_etds, filename="migrate.csv"):
        self.filename = filename
        self.final_etds = self.__merge_etds(alma_etds, primo_etds)

    @staticmethod
    def __add_new_fields(an_etd):
        an_etd["link_to_pdf"] = ""
        an_etd["thesis_advisor"] = ""
        an_etd["degree"] = ""
        an_etd["abstract"] = ""
        an_etd["subjects_and_keywords"] = ""
        return an_etd

    def __merge_etds(self, etds_from_alma, etds_from_primo):
        final_etds = []
        for primo_etd in etds_from_primo:
            primo_etd = self.__add_new_fields(primo_etd)
            for alma_etd in etds_from_alma:
                if primo_etd["mms"] == alma_etd["mms_id"]:
                    primo_etd["link_to_pdf"] = alma_etd["link_to_pdf"]
                    primo_etd["thesis_advisor"] = alma_etd["thesis_advisor"]
                    primo_etd["degree"] = alma_etd["degree"]
                    primo_etd["abstract"] = alma_etd["abstract"]
                    primo_etd["subjects_and_keywords"] = alma_etd[
                        "subjects_and_keywords"
                    ]
                    primo_etd["title"] = alma_etd["title"]
                    break
            final_etds.append(primo_etd)
        return final_etds

    @staticmethod
    def determine_degree_name(degree):
        return degree.split('(')[1].split(')')[0]

    def generate_migration_spreadsheet(self, filename="migration.csv"):
        with open(filename, "w") as migration_csv:
            headings = [
                "title",
                "fulltext_url",
                "keywords",
                "abstract",
                "author1_fname",
                "author1_mname",
                "author1_lname",
                "author1_suffix",
                "author1_email",
                "author1_institution",
                "advisor1",
                "advisor2",
                "advisor3",
                "author1_orcid",
                "disciplines",
                "comments",
                "degree_name",
                "department",
                "document_type",
                "embargo_date",
                "instruct",
                "publication_date",
                "season",
            ]
            writer = csv.DictWriter(
                migration_csv, delimiter='|',
                fieldnames=headings,
                quotechar="'"
            )
            writer.writeheader()
            for etd in self.final_etds:
                writer.writerow(
                    {
                        "title": etd["title"],
                        "fulltext_url": etd["link_to_pdf"],
                        "keywords": etd["subjects_and_keywords"],
                        "abstract": etd["abstract"],
                        "author1_fname": "",
                        "author1_mname": "",
                        "author1_lname": "",
                        "author1_suffix": "",
                        "author1_email": "",
                        "author1_institution": "University of Tennessee",
                        "advisor1": etd["thesis_advisor"],
                        "advisor2": "",
                        "advisor3": "",
                        "author1_orcid": "",
                        "disciplines": "",
                        "comments": "",
                        "degree_name": self.determine_degree_name(etd["degree"]),
                        "department": "",
                        "document_type": etd["document_type"],
                        "embargo_date": "",
                        "instruct": "",
                        "publication_date": etd["date_of_award"],
                        "season": "",
                    }
                )
        return


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
    # Write Alma Response as a Precaution
    with open("alma_data.py", "w") as alma_data:
        alma_data.write(str(etds_found_in_alma))
    TraceMigrater(primo_etds=updated_etds, alma_etds=etds_found_in_alma).generate_migration_spreadsheet()
