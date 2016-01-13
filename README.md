# COManage module for the SAML2 to SAML2 proxy

[![Build Status](https://travis-ci.org/its-dirg/s2sproxy-module-comanage.svg?branch=master)](https://travis-ci.org/its-dirg/s2sproxy-module-comanage)

Installation
============

    git clone https://github.com/its-dirg/s2sproxy-module-comanage
    cd s2sproxy-module-comanage
    pip install .
    

Configuration
=============

Instance attributes:

* ``co_manage_url``: url to the COmanage server (without trailing slash)
* ``co_manage_auth``: tuple of HTTP Basic Auth credentials (login, password) for the COmanage API user
* ``co_id``: the "collaborative organization ID" of the CO
* ``idp_attribute_name``: name of the attribute asserted by the IdP to use as
        user identifier, e.g. "eduPersonPrincipalName"
* ``email_re_object``: a regular expression object used to match against the COmanage email type to
        select which COPerson email is asserted, default is ``re.compile('official|delivery')``
* ``membership_attribute_saml_name``: on the wire SAML name used for asserting group membership, default
        is ``urn:oid:1.3.6.1.4.1.5923.1.5.1.1``

To use the attribute transformation module with the s2sproxy, add the initialized instance as the value for
``ATTRIBUTE_MODULE`` in the proxy configuration file ``proxy_conf.py`` or with mod_wsgi ``proxy_mod_wsgi_config.py``:

    ATTRIBUTE_MODULE = COmanageAttributeModule(url, auth, co_id, attr_name)
