import sources, soap_extractor, codecs, sys, os

OUT = sys.argv[1]

for endpoint in sources.soap_endpoints:
    for arg in endpoint['arguments']:
        result = soap_extractor.get_coursedata(endpoint['wsdl_url'], endpoint['operation'], arg)
        filename = os.path.join(OUT, endpoint['name'] + "_" + arg + '.xml')
        f = codecs.open(filename, encoding='utf-8', mode="wb")
        f.write(result)
        f.close()