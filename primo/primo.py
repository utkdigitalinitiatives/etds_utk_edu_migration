from requests import get


class PrimoSearch:
    def __init__(
        self,
        api_key,
        regional_id="https://api-na.hosted.exlibrisgroup.com",
        vid="01UTN_KNOXVILLE:01UTK",
        scope="MyInstitution",
        tab="LibraryCatalog",
    ):
        self.__api_key = api_key
        self.regional_id = regional_id
        self.vid = vid
        self.scope = scope
        self.tab = tab

    @staticmethod
    def __confirm_if_etd(pnx_record):
        if "manuscript" in pnx_record["display"]["type"] and "Alma" in pnx_record["display"]["source"]:
            return
        else:
            raise Exception(f"{pnx_record['display']['mms']} is not an etd.")

    def find_local_etd(self, etd_title):
        """Finds a local etd.

        Args:
            etd_title (str): The title of the etd.

        Returns:
            str: The mms_id of an ETD's bib record.

        Examples:
            >>> PrimoSearch("API-KEY").find_local_etd("tectonic implications of para- and orthogneiss geochronology and geochemistry from the southern appalachian crystalline core")

        """
        primo_response = get(f"{self.regional_id}/primo/v1/search?vid={self.vid}&scope={self.scope}&tab={self.tab}&q=title,contains,{etd_title}&apikey={self.__api_key}").json()
        first_result = primo_response["docs"][0]
        self.__confirm_if_etd(first_result["pnx"])
        return first_result["pnx"]["display"]["mms"][0]
