from requests import get


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
            return ",".join(bibs).rstrip(',')
        else:
            raise Exception(f"List of MMS IDs must be smaller than 100.  List had {len(bibs)} values.")

    def get_bibs(self):
        return get(f"{self.regional_id}/almaws/v1/bibs?mms_id={self.mms_ids}&apikey={self.__api_key}").content

