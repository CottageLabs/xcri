import argparse, os
from lxml import etree
"""
if we need it later, some fall-back code for importing etree
try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    print("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      print("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        print("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          print("running with ElementTree")
        except ImportError:
          print("Failed to import ElementTree from any known place")
"""

parser = argparse.ArgumentParser(description='Parse a directory of XCRI data files')
parser.add_argument('-d', help='Source directory of XCRI files', required=True)

args = parser.parse_args()

IN_DIR = args.d

# get all the xml files from the specified directory
files = [f for f in os.listdir(IN_DIR) if f.endswith(".xml")]

course_count = 0
fails = 0;
for f in files:
    path = os.path.join(IN_DIR, f)
    with open(path) as source:
        try:
            doc = etree.parse(source)
        except:
            print "Failed to parse: " + path
            fails += 1
            continue
        root = doc.getroot()
        namespace = root.nsmap[None]
        if (root.tag != '{' + namespace + '}catalog'):
            print "Invalid XCRI in " + path
            fails += 1
            continue
        xp = etree.ETXPath("//{" + namespace + "}course")
        courses = xp(root)
        print str(len(courses)) + " in " + path
        course_count += len(courses)

print "Total number of courses: " + str(course_count)
print "Total number of wrongly formed XMLs: " + str(fails)
        
