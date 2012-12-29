import json, argparse, os, xmltodict
from lxml import etree

parser = argparse.ArgumentParser(description='Parse a directory of XCRI data files')
parser.add_argument('-d', help='Source directory of XCRI XML files', required=True)
parser.add_argument('-o', help='Output directory for XCRI JSON files (omit to write them into the source directory)')

args = parser.parse_args()

IN_DIR = args.d
OUT_DIR = args.o if args.o is not None else args.d

xml_files = [f for f in os.listdir(IN_DIR) if f.endswith(".xml")]

def xcrixml2json(path):
    with open(path) as source:
        xml = source.read()
    d = xmltodict.parse(xml)
    j = json.dumps(d, indent=2)
    return j

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