import json, argparse, os, requests, uuid
from copy import deepcopy

parser = argparse.ArgumentParser(description='Parse XCRI JSON files into an ES index, Your ES index has to be running for this to succeed')
parser.add_argument('-d', help='Source directory of XCRI JSON files', required=True)

args = parser.parse_args()

ES_URL = 'http://localhost:9200/xcri'

IN_DIR = args.d

mapping = {
    "provider" : {
        "date_detection" : "false",
        "dynamic_templates" : [
            {
                "default" : {
                    "match" : "*",
                    "match_mapping_type": "string",
                    "mapping" : {
                        "type" : "multi_field",
                        "fields" : {
                            "{name}" : {"type" : "{dynamic_type}", "index" : "analyzed", "store" : "no"},
                            "exact" : {"type" : "{dynamic_type}", "index" : "not_analyzed", "store" : "yes"}
                        }
                    }
                }
            }
        ]
    }
}

d = requests.delete(ES_URL)
p = requests.post(ES_URL)
pt = requests.put(ES_URL + '/provider/_mapping', json.dumps(mapping))

mapping["course"] = mapping["provider"]
del mapping["provider"]
pta = requests.put(ES_URL + '/course/_mapping', json.dumps(mapping))

json_files = [f for f in os.listdir(IN_DIR) if (f.endswith(".json") and f not in ['broken-sources.json','directory-scrape.json','sources.json'])]

errors = open('errors','w')

providercount = 0
coursecount = 0

for jf in json_files:
    path = os.path.join(IN_DIR, jf)
    print path

    with open(path) as source:
        js = source.read()
    rec = json.loads(js)

    try:
        for record in rec['catalog']['provider']:
            record['_id'] = uuid.uuid4().hex
            record['sourcepath'] = path

            meta = deepcopy(record)
            del meta['course']

            for course in record['course']:
                course['provider'] = meta
                course['_id'] = uuid.uuid4().hex
                r = requests.post(ES_URL + '/course/' + course['_id'], json.dumps(course))

                coursecount += 1
                print str(providercount) + ' - ' + str(coursecount)

            del record['course']
            r = requests.post(ES_URL + '/provider/' + record['_id'], json.dumps(record))

            providercount += 1
            print providercount

    except:
        errors.write('no provider or other error in JSON for ' + path + '\n')
        print "hmm, something went wrong. maybe there is not a provider in this xml doc."

errors.close()




