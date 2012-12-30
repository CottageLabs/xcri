import json, argparse, os, requests, uuid

parser = argparse.ArgumentParser(description='Parse XCRI JSON files into an ES index, Your ES index has to be running for this to succeed')
parser.add_argument('-d', help='Source directory of XCRI JSON files', required=True)

args = parser.parse_args()

ES_URL = 'http://localhost:9200/xcri'

IN_DIR = args.d

mapping = {
    "feed" : {
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
pt = requests.put(ES_URL + '/feed/_mapping', json.dumps(mapping))

mapping["course"] = mapping["feed"]
del mapping["feed"]
pta = requests.put(ES_URL + '/course/_mapping', json.dumps(mapping))

json_files = [f for f in os.listdir(IN_DIR) if (f.endswith(".json") and f not in ['broken-sources.json','directory-scrape.json','sources.json'])]

errors = open('errors','w')

feedcount = 0
coursecount = 0

for jf in json_files:
    path = os.path.join(IN_DIR, jf)
    print path

    with open(path) as source:
        js = source.read()
    rec = json.loads(js)

    try:
        feedid = uuid.uuid4().hex
        record = rec['catalog']['provider']
        record['_id'] = feedid

        courses = rec['catalog']['provider']['course']
        for course in courses:
            courseid = uuid.uuid4().hex
            course['sourcefeed'] = feedid
            course['sourcepath'] = path
            course['_id'] = courseid
            r = requests.post(ES_URL + '/course/' + courseid, json.dumps(course))

            coursecount += 1
            print str(feedcount) + ' - ' + str(coursecount)

        del record['course']
        r = requests.post(ES_URL + '/feed/' + feedid, json.dumps(record))

        feedcount += 1
        print feedcount

    except:
        errors.write('no provider or other error in JSON for ' + path + '\n')
        print "hmm, there is not a provider in this xml doc."

errors.close()




