import sources, soap_extractor, codecs, sys, os, requests

IN = sys.argv[1]
OUT = sys.argv[2]

UPDATE_ONLY = False
if len(sys.argv) == 4:
    UPDATE_ONLY = True

def soap(wsdl_url, operation, argument, save_to):
    print "SOAP Harvest: " + wsdl_url + " to " + save_to
    try:
        result = soap_extractor.get_coursedata(wsdl_url, operation, argument)
        f = codecs.open(filename, encoding='utf-8', mode="wb")
        f.write(result)
        f.close()
        print "...done\n"
    except:
        print "...skipped due to error\n"

endpoints = sources.Endpoints(IN)

for endpoint in endpoints.soap_endpoints():
    if len(endpoint['arguments']) > 0:
        for arg in endpoint['arguments']:
            filename = os.path.join(OUT, endpoint['name'] + "_" + arg + '.xml')
            if os.path.exists(filename) and UPDATE_ONLY:
                print "Update Only Mode: skipping " + endpoint['name'] + " / " + arg
                continue
            soap(endpoint['wsdl_url'], endpoint['operation'], arg, filename)
    else:
        filename = os.path.join(OUT, endpoint['name'] + '.xml')
        if os.path.exists(filename) and UPDATE_ONLY:
            print "Update Only Mode: skipping " + endpoint['name'] + " / " + arg
            continue
        soap(endpoint['wsdl_url'], endpoint['operation'], None, filename)
        
for endpoint in endpoints.rest_endpoints():
    filename = os.path.join(OUT, endpoint['name'] + ".xml")
    if os.path.exists(filename) and UPDATE_ONLY:
        print "Update Only Mode: skipping " + endpoint['name']
        continue
    print "REST Harvest: " + endpoint['resource_url'] + " to " + filename
    try:
        resp = requests.get(endpoint['resource_url'])
        f = codecs.open(filename, encoding='utf-8', mode='wb')
        f.write(resp.text)
        f.close()
        print "...done\n"
    except:
        print "...skipped due to error\n"