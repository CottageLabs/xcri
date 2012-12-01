import sources, soap_extractor, codecs, sys, os, requests

OUT = sys.argv[1]

UPDATE_ONLY = False
if len(sys.argv) == 3:
    UPDATE_ONLY = True

for endpoint in sources.soap_endpoints:
    for arg in endpoint['arguments']:
        filename = os.path.join(OUT, endpoint['name'] + "_" + arg + '.xml')
        if os.path.exists(filename) and UPDATE_ONLY:
            print "Update Only Mode: skipping " + endpoint['name'] + " / " + arg
            continue
        print "SOAP Harvest: " + endpoint['wsdl_url'] + " to " + filename
        result = soap_extractor.get_coursedata(endpoint['wsdl_url'], endpoint['operation'], arg)
        f = codecs.open(filename, encoding='utf-8', mode="wb")
        f.write(result)
        f.close()
        print "...done\n"
        
for endpoint in sources.rest_endpoints:
    filename = os.path.join(OUT, endpoint['name'] + ".xml")
    if os.path.exists(filename) and UPDATE_ONLY:
        print "Update Only Mode: skipping " + endpoint['name'] + " / " + arg
        continue
    print "REST Harvest: " + endpoint['resource_url'] + " to " + filename
    resp = requests.get(endpoint['resource_url'])
    f = codecs.open(filename, encoding='utf-8', mode='wb')
    f.write(resp.text)
    f.close()
    print "...done\n"