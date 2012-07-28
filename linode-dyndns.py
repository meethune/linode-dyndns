#!/usr/bin/python
"""
linode-dns.py
Author: Michael Shepanski
Date: Jan 17, 2010

linode-dyndns.py
Updates: Matthew Schick
A script to update a DNS record on Linode to your external IP.

References:
  http://atxconsulting.com/content/linode-api-bindings
  https://github.com/tjfontaine/linode-python/
"""
import pycurl
import re
from linode import api
from StringIO import StringIO

APIKEY = 'ENTER API KEY HERE'
DOMAIN = 'YOUR DOMAIN HERE'
RECORD = 'HOST TO BE UPDATED'
USERAGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1'
CHECKIP = { "http://automation.whatismyip.com/n09230945.asp" ,
            "http://checkip.dyndns.org:8245/" }

def get_external_ip():
    """ Return the current external IP. """
    external=[]
    for each in CHECKIP:
        html = StringIO()
        curl = pycurl.Curl()
        curl.setopt(curl.USERAGENT, USERAGENT)
        curl.setopt(curl.URL, each)
        curl.setopt(curl.WRITEFUNCTION, html.write)
        curl.perform()
        curl.close()
        external.append(re.findall('[0-9.]+', html.getvalue())[0])
        print "%s says your IP is: %s" % ( each, external[len(external)-1] )
    # Unique Sort List to ensure both sites are saying the same thing
    external_ip = sorted(set(external))
    if len(external_ip) > 1:
        print "Someone is Lying!"
        return false
    else:
        return external_ip[0]

def set_dns_target(utarget, udomain=DOMAIN, urecord=RECORD):
    """ Update the domain's DNS record with the specified target. """
    linode = api.Api(APIKEY)
    for domain in linode.domain_list():
        if domain['DOMAIN'] == udomain:
            # Check the DNS Entry already exists
            for record in linode.domain_resource_list(domainid=domain['DOMAINID']):
                if record['NAME'] == urecord:
                    if record['TARGET'] == utarget:
                        # DNS Entry Already at the correct value
                        print "Entry '%s:%s' already set to '%s'." % (udomain, urecord, utarget)
                        return record['RESOURCEID']
                    else:
                        # DNS Entry found; Update it
                        print "Updating entry '%s:%s' target to '%s'." % (udomain, urecord, utarget)
                        return linode.domain_resource_update(domainid=domain['DOMAINID'],
                            resourceid=record['RESOURCEID'], target=utarget)
            # DNS Entry not found; Create it
            print "Creating entry '%s:%s' target as '%s'." % (udomain, urecord, utarget)
            return linode.domain_resource_create(domainid=domain['DOMAINID'],
                name=urecord, type='A', target=utarget, ttl_sec=300)
            print "Error: Domain %s not found." % udomain

if __name__ == '__main__':
    external_ip = get_external_ip()
    if external_ip:
        print "set_dns_target(%s, DOMAIN, RECORD)" % external_ip
        #set_dns_target(external_ip, DOMAIN, RECORD)
