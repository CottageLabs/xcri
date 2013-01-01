import codecs, argparse, os, shutil
from lxml import etree

NS_11 = "http://xcri.org/profiles/catalog"

def upgrade(root):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    xslt_file = os.path.join(this_dir, "xcri-cap_1-1_to_1-2.xslt")
    with open(xslt_file) as f: xslt = etree.parse(f)
    transform = etree.XSLT(xslt)
    result = transform(root)
    return result
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Upgrade XCRI 1.1 files to XCRI 1.2')
    parser.add_argument('-d', help='Source directory of XCRI XML (of mixed version) files', required=True)
    parser.add_argument('-o', help='Output directory for XCRI XML 1.2 (if omitted, will overwrite the incoming files)')
    
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
        
        # figure out if we need to upgrade from 1.1 to 1.2
        namespace = root.nsmap[None]
        if namespace == NS_11:
            print "Upgrading 1.1 to 1.2 ..."
            result = upgrade(root)
            f = codecs.open(os.path.join(OUT_DIR, xf), "wb", "utf-8")
            f.write(unicode(result))
            f.close()
            print "done\n"
        else:
            if IN_DIR != OUT_DIR:
                shutil.copyfile(path, os.path.join(OUT_DIR, xf))
            print "no upgrade necessary, just copying to output dir\n"
        
