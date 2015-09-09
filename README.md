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
    * ``co_manage_url``:
    * ``co_manage_auth``: HTTP basic auth credentials
    * ``co_id``:
    * ``idp_attribute_name``: EPPN or EPTID

Add the initialized instance as the ``ATTRIBUTE_MODULE` in proxy configuration (``proxy_conf.py``):

    ATTRIBUTE_MODULE = COmanageAttributeModule(url, auth, co_id, attr_name)