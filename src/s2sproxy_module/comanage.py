import urllib

import requests
from s2sproxy.util.attribute_module import AttributeModule, NoUserData


class FailedRequestError(Exception):
    pass


class COmanageAttributeModule(AttributeModule):
    def __init__(self, co_manage_url, co_manage_auth, co_id,
                 idp_attribute_name):
        """
        Initialize the COmanage attribute module.
        :param co_manage_url: url to the COmanage server (without trailing slash)
        :param co_manage_auth: HTTP Basic Auth credentials for the COmanage server
        :param co_id: the "collaborative organization ID" of the CO
        :param idp_attribute_name: which attribute asserted by the IdP to use as
        user identifier, e.g. "eduPersonPrincipalName"
        """
        self.co_manage_url = co_manage_url
        self.co_manage_auth = co_manage_auth
        self.co_id = co_id
        self.idp_attribute_name = idp_attribute_name

    def get_attributes(self, idp_attributes):
        """Will not fail on missing user data, returns what it gets from
        COmanage."""
        try:
            user_id = self._get_user_id(idp_attributes)
            org_id = self._get_org_id(user_id)
            person_id = self._get_person_id(org_id)

            attributes = {}
            attributes.update(self._get_name_info(person_id))
            attributes.update(self._get_email_address(person_id))
            attributes.update(self._get_vo_info(person_id))
            attributes.update(self._get_group_info(person_id))
        except FailedRequestError as e:
            raise NoUserData(
                "Failed to fetch user attributes: {}".format(e))

        return attributes

    def _get_user_id(self, attributes):
        """Get the user id from the attributes from the IdP."""
        try:
            return attributes[self.idp_attribute_name][0]
        except KeyError:
            raise NoUserData(
                "Necessary attribute '{}' not returned by IdP.".format(
                    self.idp_attribute_name))

    def _get_org_id(self, user_id):
        """Get the 'organizational identity' to which the user identifier is
        linked."""
        params = {"coid": self.co_id, "search_identifier": user_id}
        json = self._make_request("/org_identities.json", params)
        return json["OrgIdentities"][0]["Id"]

    def _get_person_id(self, org_id):
        """Get the 'CoPersonId'."""
        json = self._make_request("/co_org_identity_links.json",
                                  {"orgidentityid": org_id})

        # Search all links to find the COPerson linked with this COId
        for link in json["CoOrgIdentityLinks"]:
            person_id = link["CoPersonId"]
            if self._person_id_in_co(person_id):
                return person_id

    def _person_id_in_co(self, person_id):
        """Verify that a COPerson is linked with this COId."""
        json = self._make_request(
            "/co_people/{person_id}.json".format(person_id=person_id))

        return json["CoPeople"][0]["CoId"] == self.co_id

    def _get_name_info(self, person_id):
        """Get the users name information."""
        json = self._make_request("/names.json", {"copersonid": person_id})

        for entry in json["Names"]:
            if entry["PrimaryName"]:
                gn = entry["Given"]
                sn = entry["Family"]
                return {
                    "givenName": gn,
                    "sn": sn,
                    "displayName": "{gn} {sn}".format(gn=gn, sn=sn)
                }

    def _get_email_address(self, person_id):
        """Get the users email address."""
        json = self._make_request("/email_addresses.json",
                                  {"copersonid": person_id})
        for entry in json["EmailAddresses"]:
            if entry["Type"] == "official":
                return {"mail": entry["Mail"]}

    def _get_vo_info(self, person_id):
        """Get the 'voIdentifier'"""
        json = self._make_request("/identifiers.json",
                                  {"copersonid": person_id})
        for entry in json["Identifiers"]:
            if entry["Type"] == "voIdentifier":
                return {"uid": entry["Identifier"]}

    def _get_group_info(self, person_id):
        """Get all groups the user is a member of."""
        json = self._make_request("/co_groups.json", {"copersonid": person_id})
        return {"isMemberOf": [entry["Name"] for entry in json["CoGroups"]]}

    def _make_request(self, path, parameters=None):
        """Make request to the COmanage server."""
        url = "{base_url}{path}".format(base_url=self.co_manage_url,
                                        path=path)
        if parameters:
            url = "{url}?{params}".format(url=url,
                                          params=urllib.parse.urlencode(
                                              parameters))

        try:
            resp = requests.get(url, auth=self.co_manage_auth)
        except requests.RequestException as e:
            raise FailedRequestError(str(e))

        if resp.status_code == 200:
            return resp.json()
        else:
            raise FailedRequestError(
                "{status}: {text}".format(status=resp.status_code,
                                          text=resp.text))
