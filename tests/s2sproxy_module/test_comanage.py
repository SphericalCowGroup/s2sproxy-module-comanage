# pylint: disable=redefined-outer-name, protected-access, no-self-use, missing-docstring

from collections import Counter
import json
from urllib.parse import urlencode

import pytest
import requests
import responses

from s2sproxy_module.comanage import COmanageAttributeModule, \
    FailedRequestError

CO_ID = "15"
IDP_ATTRIBUTE_NAME = "eduPersonPrincipalName"
COMANAGE_SERVER = "http://example.com"


def _build_url(path, params=None):
    url = "{host}{path}".format(host=COMANAGE_SERVER, path=path)
    if params:
        url = "{url}?{query}".format(url=url, query=urlencode(params))

    return url


@pytest.fixture(scope="class")
def attribute_module():
    return COmanageAttributeModule(COMANAGE_SERVER,
                                   ("foo", "bar"), CO_ID,
                                   IDP_ATTRIBUTE_NAME)


class TestCOmanageAttributeModule(object):
    @responses.activate
    def test_get_org_id(self, attribute_module):
        org_id = "123"
        user_id = "foobar"

        body = {"OrgIdentities": [{"Id": org_id}]}
        params = {"coid": CO_ID, "search_identifier": user_id}
        responses.add(responses.GET,
                      _build_url("/org_identities.json", params),
                      body=json.dumps(body), match_querystring=True)

        assert attribute_module._get_org_id(user_id) == org_id

    @responses.activate
    def test_get_person_id(self, attribute_module):
        org_id = "123"
        person_id = "456"

        body_identity_links = {
            "CoOrgIdentityLinks": [{
                "CoPersonId": person_id,
                "OrgIdentityId": org_id
            }]
        }
        params_identity_links = {"orgidentityid": org_id}
        responses.add(responses.GET,
                      _build_url("/co_org_identity_links.json",
                                 params_identity_links),
                      body=json.dumps(body_identity_links),
                      match_querystring=True)
        body_people = {
            "CoPeople": [{
                "CoId": CO_ID,
                "Id": person_id,
            }]
        }
        responses.add(responses.GET,
                      _build_url("/co_people/{}.json".format(person_id)),
                      body=json.dumps(body_people), match_querystring=True)

        assert attribute_module._get_person_id(org_id) == person_id

    @responses.activate
    def test_person_id_in_co(self, attribute_module):
        person_id = "123"
        body = {
            "CoPeople": [{
                "CoId": CO_ID,
                "Id": person_id,
            }]
        }
        responses.add(responses.GET,
                      _build_url("/co_people/{}.json".format(person_id)),
                      body=json.dumps(body), match_querystring=True)

        assert attribute_module._person_id_in_co(person_id)

    @responses.activate
    def test_get_name_info(self, attribute_module):
        person_id = "123"
        given_name = "Donald"
        family_name = "Duck"

        body = {
            "Names": [{
                "Family": family_name,
                "Given": given_name,
                "Person": {
                    "Id": person_id,
                },
                "PrimaryName": True,
            }]
        }
        params = {"copersonid": person_id}
        responses.add(responses.GET,
                      _build_url("/names.json", params),
                      body=json.dumps(body), match_querystring=True)

        name_info = attribute_module._get_name_info(person_id)
        assert name_info["givenName"] == given_name
        assert name_info["sn"] == family_name
        assert name_info["displayName"] == "{} {}".format(given_name,
                                                          family_name)

    @responses.activate
    def test_get_email_address(self, attribute_module):
        person_id = "123"
        email = "donald.duck@donaldduck.com"
        body = {
            "EmailAddresses": [{
                "Mail": email,
                "Type": "official",
            }]
        }
        params = {"copersonid": person_id}
        responses.add(responses.GET,
                      _build_url("/email_addresses.json", params),
                      body=json.dumps(body), match_querystring=True)

        email_info = attribute_module._get_email_address(person_id)
        assert email_info["mail"] == email

    @responses.activate
    def test_get_vo_id(self, attribute_module):
        person_id = "123"
        vo_id = "VO1111"

        body = {
            "Identifiers": [{
                "Identifier": vo_id,
                "Type": "voIdentifier",
            }]
        }
        params = {"copersonid": person_id}
        responses.add(responses.GET, _build_url("/identifiers.json", params),
                      body=json.dumps(body), match_querystring=True)

        vo_id_info = attribute_module._get_vo_info(person_id)
        assert vo_id_info["uid"] == vo_id

    @responses.activate
    def test_get_group_info(self, attribute_module):
        person_id = "123"
        body = {
            "CoGroups": [
                {"Name": "members"}, {"Name": "members:Test COU 1"}
            ]
        }
        params = {"copersonid": person_id}
        responses.add(responses.GET,
                      _build_url("/co_groups.json", params),
                      body=json.dumps(body), match_querystring=True)

        group_info = attribute_module._get_group_info(person_id)
        assert Counter(group_info["isMemberOf"]) == Counter(
            ["members", "members:Test COU 1"])

    @responses.activate
    def test_failing_request(self, attribute_module):
        path = "/test"
        exception = requests.ConnectionError("Something went wrong.")
        responses.add(responses.GET,
                      _build_url(path),
                      body=exception)

        with pytest.raises(FailedRequestError):
            attribute_module._make_request(path)

    @responses.activate
    def test_make_request(self, attribute_module):
        path = "/test"
        params = {"foo": "bar"}

        # must use context manager so assert_all_requests_are_fired=True in
        # responses
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, _build_url(path, params),
                     body=json.dumps(params), match_querystring=True)
            attribute_module._make_request(path, params)

    def test_get_user_id(self, attribute_module):
        user_id = "foo@example.com"

        assert attribute_module._get_user_id(
            {IDP_ATTRIBUTE_NAME: [user_id]}) == user_id
