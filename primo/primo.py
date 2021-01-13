from requests import get
import json


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

    def find_local_etd(self, etd_title):
        """Finds a local etd.

        @todo: Right now, this doesn't return the local etd but all the search results. Fix.

        Args:
            etd_title (str): The title of the etd.

        Returns:
            @todo: Fix.

        Examples:
            >>> PrimoSearch("API-KEY").find_local_etd("tectonic implications of para- and orthogneiss geochronology and geochemistry from the southern appalachian crystalline core")

        """
        return json.dumps(
            get(
                f"{self.regional_id}/primo/v1/search?vid={self.vid}&scope={self.scope}&tab={self.tab}&q=title,contains,{etd_title}&apikey={self.__api_key}"
            ).json(),
            indent=4,
        )
