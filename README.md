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
* ``co_manage_auth``: HTTP Basic Auth credentials for the COmanage server
* ``co_id``: the "collaborative organization ID" of the CO
* ``idp_attribute_name``: name of the attribute asserted by the IdP to use as
        user identifier, e.g. "eduPersonPrincipalName"

To use the attribute transformation module with the s2sproxy, add the initialized instance as the
``ATTRIBUTE_MODULE`` in proxy configuration (``proxy_conf.py``):

    ATTRIBUTE_MODULE = COmanageAttributeModule(url, auth, co_id, attr_name)