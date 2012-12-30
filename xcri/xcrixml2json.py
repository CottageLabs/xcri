import json, argparse, os, xmltodict
from lxml import etree

def xcrixml2json(path):
    with open(path) as source:
        xml = source.read()
    d = xmltodict.parse(xml)
    catalog = d['catalog']
    cleanup_catalog(catalog)
    #j = json.dumps(d, indent=2)
    #return j
    return d

def _remove_namespace_declarations(element):
    for key in element.keys():
        if key.startswith("@"):
            del element[key]

def _ensure_list(parent, listable):
    if not parent.has_key(listable):
        return
    if type(parent[listable]) != list:
        parent[listable] = [parent[listable]]

def _ensure_text(parent, key):
    if not parent.has_key(key):
        return
    if type(parent[key]) == list:
        for i in range(len(parent[key])):
            parent[key] = _extract_text(parent[key][i])
    elif type(parent[key]) == dict:
        parent[key] = _extract_text(parent[key])
    
def _extract_text(element):
    if type(element) == dict:
        return element.get("#text", "")
    else:
        return element

def _prepend_namespace(parent, element_name, namespace, default=None):
    if element_name.startswith(namespace + ":"):
        return
    if not parent.has_key(element_name):
        return
    new_key = namespace + ":" + element_name
    if not parent.has_key(new_key):
        parent[new_key] = default
    if type(parent[new_key]) == list:
        parent[new_key].append(parent[element_name])
    else:
        parent[new_key] = parent[element_name]
    del parent[element_name]

def _text_to_value(parent, element_name):
    if not parent.has_key(element_name):
        return
    element = parent[element_name]
    if type(element) != dict:
        nd = {"value" : element}
        parent[element_name] = nd
    else:
        element["value"] = element.get("#text", "")
        del element["#text"]

def cleanup_catalog(catalog):
    _remove_namespace_declarations(catalog)
    _ensure_list(catalog, "provider")
    for prov in catalog['provider']:
        cleanup_provider(prov)

def cleanup_provider(provider):
    for key in provider.keys():
        if key.endswith("identifier"):
            cleanup_identifier(provider, key)
    
    _ensure_list(provider, "course")
    for course in provider['course']:
        cleanup_course(course)

def cleanup_identifier(parent, identifier_key):
    # convert to object and set the #text field correctly
    _text_to_value(parent, identifier_key)
    _remove_namespace_declarations(parent[identifier_key])
    
    # if the key does not have the dc namespace prefixed, then fix that
    _prepend_namespace(parent, identifier_key, "dc", [])
    
def cleanup_course(course):
    _prepend_namespace(course, "level", "mlo")
    _ensure_text(course, "mlo:level")
    
    _prepend_namespace(course, "qualification", "mlo", [])
    _ensure_list(course, "mlo:qualification")
    for q in course.get('mlo:qualification', []):
        cleanup_qualification(q)
    
    _ensure_list(course, "presentation")
    for p in course.get("presentation", []):
        cleanup_presentation(p)
    
    _prepend_namespace(course, "credit", "mlo", [])
    _ensure_list(course, "mlo:credit")
    for c in course.get("mlo:credit", []):
        cleanup_credit(c)
    
    
    
def cleanup_credit(credit):
    pass

def cleanup_presentation(pres):
    pass

def cleanup_qualification(qual):
    pass

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Parse a directory of XCRI data files')
    parser.add_argument('-d', help='Source directory of XCRI XML files', required=True)
    parser.add_argument('-o', help='Output directory for XCRI JSON files (omit to write them into the source directory)')
    
    args = parser.parse_args()
    
    IN_DIR = args.d
    OUT_DIR = args.o if args.o is not None else args.d
    
    xml_files = [f for f in os.listdir(IN_DIR) if f.endswith(".xml")]

    fails = 0;
    for xf in xml_files:
        path = os.path.join(IN_DIR, xf)
        
        # verify the file before parsing
        with open(path) as source:
            print "Verifying " + path
            try:
                doc = etree.parse(source)
            except:
                print "Failed to parse: " + path + "\n"
                fails += 1
                continue
            root = doc.getroot()
            namespace = root.nsmap[None]
            if (root.tag != '{' + namespace + '}catalog'):
                print "Invalid XCRI in " + path + "\n"
                fails += 1
                continue
        print path + " successfully verified"
        
        # ok, yes, it's inefficient to open the file twice, but it means that
        # we can do the verification above before leaping in and coverting to JSON
        print "JSONifying " + path + " ..."
        j = xcrixml2json(path)
        
        fn = xf[:-4] + ".json"
        out = os.path.join(OUT_DIR, fn)
        with open(out, "wb") as output:
            output.write(j)
        print "done\n"