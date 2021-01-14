from requests import get
import xmltodict


class BibRetriever:
    def __init__(
        self,
        api_key,
        list_of_mms_ids,
        regional_id="https://api-na.hosted.exlibrisgroup.com",
    ):
        self.__api_key = api_key
        self.mms_ids = self.__convert_bib_list_to_string(list_of_mms_ids)
        self.regional_id = regional_id

    @staticmethod
    def __convert_bib_list_to_string(bibs):
        if len(bibs) <= 100:
            return ",".join(bibs).rstrip(",")
        else:
            raise Exception(
                f"List of MMS IDs must be smaller than 100.  List had {len(bibs)} values."
            )

    def get_bibs(self):
        converted_bibs = xmltodict.parse(
            get(
                f"{self.regional_id}/almaws/v1/bibs?mms_id={self.mms_ids}&apikey={self.__api_key}"
            ).content
        )
        return [
            BibRecord(bib).process_record() for bib in converted_bibs["bibs"]["bib"]
        ]


class BibRecord:
    def __init__(self, bib_record):
        self.record = bib_record

    def process_record(self):
        return {
            "mms_id": self.get_mms_id(),
            "title": self.get_title(),
            "author": self.get_author(),
            "thesis_advisor": self.get_thesis_advisor(),
            "link_to_etd": self.get_link_to_etd(),
            "degree": self.get_degree(),
            "abstract": self.get_abstract(),
            "date_of_publication": self.get_date_of_publication(),
            "subjects_and_keywords": self.get_subjects_and_keywords(),
        }

    def get_mms_id(self):
        return self.record["mms_id"]

    def get_title(self):
        return self.record["title"]

    def get_author(self):
        return self.record["author"]

    def get_thesis_advisor(self):
        for field in self.record["record"]["datafield"]:
            if field["@tag"] == "500" and field["subfield"]["#text"].startswith(
                "Thesis advisor:"
            ):
                return (
                    field["subfield"]["#text"]
                    .replace("Thesis advisor:", "")
                    .strip()
                    .rstrip(".")
                )
        raise Exception(f"Missing advisor: {self.get_mms_id()}")

    def get_link_to_etd(self):
        for field in self.record["record"]["datafield"]:
            if field["@tag"] == "856":
                return field["subfield"]["#text"]
        raise Exception(f"Missing link to etd: {self.get_mms_id()}")

    def get_degree(self):
        for field in self.record["record"]["datafield"]:
            if field["@tag"] == "502":
                return field["subfield"]["#text"]
        raise Exception(f"Could not determine degree type: {self.get_mms_id}")

    def get_abstract(self):
        abstract = ""
        for field in self.record["record"]["datafield"]:
            if field["@tag"] == "520":
                abstract += field["subfield"]["#text"]
        return abstract

    def get_date_of_publication(self):
        return self.record["date_of_publication"].rstrip(".")

    def get_subjects_and_keywords(self):
        subjects = []
        for field in self.record["record"]["datafield"]:
            if field["@tag"] == "650":
                for subfield in field["subfield"]:
                    if (
                        subfield["@code"] == "a"
                        and subfield["#text"].rstrip(".").replace(",", ";")
                        not in subjects
                    ):
                        subjects.append(subfield["#text"].rstrip(".").replace(",", ";"))
            elif field["@tag"] == "690":
                for subfield in field["subfield"]:
                    if (
                        subfield["@code"] == "x"
                        and subfield["#text"].rstrip(".").replace(",", ";")
                        not in subjects
                    ):
                        subjects.append(subfield["#text"].rstrip(".").replace(",", ";"))
        print(subjects)
        return ", ".join(subjects)
