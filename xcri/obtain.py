import sources, soap_extractor, codecs, sys, os, requests, argparse

parser = argparse.ArgumentParser(description='Obtain XCRI data from sources')
parser.add_argument('-s', help='Source input file', required=True)
parser.add_argument('-o', help='Output directory, where XCRI XML files will be stored', required=True)
parser.add_argument('-u', help="Update Only Mode: do not attempt to update sources where an XCRI XML file already exists in the output directory",
                            action='store_const', const="update")
parser.add_argument('-e', help="Stop on error", action='store_const', const="stop")

args = parser.parse_args()

IN = args.s
OUT = args.o
UPDATE_ONLY = args.u is not None
STOP_ON_ERROR = args.e is not None

def soap(wsdl_url, operation, argument, save_to):
    print "SOAP Harvest: " + wsdl_url + " to " + save_to
    try:
        result = soap_extractor.get_coursedata(wsdl_url, operation, argument)
        f = codecs.open(filename, encoding='utf-8', mode="wb")
        f.write(result)
        f.close()
        print "...done\n"
    except:
        if STOP_ON_ERROR:
            raise
        print "...skipped due to error\n"

def get_file_path(endpoint_name, arg=None):
    endpoint_name = endpoint_name.replace("/", "_")
    if arg is not None:
        endpoint_name += "_" + arg
    return os.path.join(OUT, endpoint_name + ".xml")

endpoints = sources.Endpoints(IN)

for endpoint in endpoints.soap_endpoints():
    if len(endpoint['arguments']) > 0:
        for arg in endpoint['arguments']:
            filename = get_file_path(endpoint['name'], arg)
            if os.path.exists(filename) and UPDATE_ONLY:
                print "Update Only Mode: skipping " + endpoint['name'] + " / " + arg
                continue
            soap(endpoint['wsdl_url'], endpoint['operation'], arg, filename)
    else:
        filename = get_file_path(endpoint['name'])
        if os.path.exists(filename) and UPDATE_ONLY:
            print "Update Only Mode: skipping " + endpoint['name'] + " / " + arg
            continue
        soap(endpoint['wsdl_url'], endpoint['operation'], None, filename)
        
for endpoint in endpoints.rest_endpoints():
    filename = get_file_path(endpoint['name'])
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
        if STOP_ON_ERROR:
            raise
        print "...skipped due to error\n"