import json, argparse, os, xmltodict, collections, re
from lxml import etree

DC_NS = "http://purl.org/dc/elements/1.1/"
MLO_NS = "http://purl.org/net/mlo"

def xcrixml2json(path):
    with open(path) as source:
        doc = etree.parse(source)
    root = doc.getroot()
    _add_cdata(root)
    
    xml = etree.tostring(root)
    d = xmltodict.parse(xml)
    catalog = d['catalog']
    cleanup_catalog(catalog)
    j = json.dumps(d, indent=2)
    return j
    #return d

def _add_cdata(root):
    namespace = root.nsmap[None]
    
    # all dc:description elements
    desc_xp = "//{" + DC_NS + "}description"
    _do_add_cdata(root, desc_xp)
    
    # abstract
    abstract_xp = "//{" + namespace + "}abstract"
    _do_add_cdata(root, abstract_xp)
    
    # applicationProcedure
    ap_xp = "//{" + namespace + "}applicationProcedure"
    _do_add_cdata(root, ap_xp)
    
    # mlo:assessment
    ass_xp = "//{" + MLO_NS + "}assessment"
    _do_add_cdata(root, ass_xp)
    
    # learningOutcome
    lo_xp = "//{" + namespace + "}learningOutcome"
    _do_add_cdata(root, lo_xp)
    
    # mlo:objective
    obj_xp = "//{" + MLO_NS + "}objective"
    _do_add_cdata(root, obj_xp)
    
    # mlo:prerequisite
    pre_xp = "//{" + MLO_NS + "}prerequisite"
    _do_add_cdata(root, pre_xp)
    
    # regulations
    reg_xp = "//{" + namespace + "}regulations"
    _do_add_cdata(root, reg_xp)
    
def _do_add_cdata(root, xpath):
    rx = "<.+?>(.+)</"
    desc_xp = etree.ETXPath(xpath)
    descs = desc_xp(root)
    for desc in descs:
        if len(desc.getchildren()) > 0:
            s = etree.tostring(desc)
            m = re.match(rx, s)
            cdata = None
            if m is not None:
                cdata = "<![CDATA[" + m.group(1) + "]]>"
            if cdata is not None:
                desc.text = cdata
                for i in range(len(desc.getchildren())):
                    del desc[i]

def _is_dict(element):
    return type(element) == collections.OrderedDict or type(element) == dict

def _remove_attributes(element):
    for key in element.keys():
        if key.startswith("@"):
            del element[key]

def _ensure_list(parent, listable):
    if not parent.has_key(listable):
        return
    if type(parent[listable]) != list:
        parent[listable] = [parent[listable]]

def _ensure_obj_to_text(parent, key, idx=None):
    if not parent.has_key(key):
        return
    
    if idx is not None:
        text = _extract_text(parent[key][idx])
        parent[key][idx] = text
    else:
        text = _extract_text(parent[key])
        parent[key] = text

def _ensure_text(parent, key):
    if not parent.has_key(key):
        return
    if type(parent[key]) == list:
        for i in range(len(parent[key])):
            parent[key] = _extract_text(parent[key][i])
    elif _is_dict(parent[key]):
        parent[key] = _extract_text(parent[key])
    
def _extract_text(element):
    if _is_dict(element):
        return element.get("#text", "")
    else:
        return element

def _remove_dud_text(element):
    if _is_dict(element):
        if element.has_key("#text"):
            del element["#text"]

def _prepend_namespace(parent, element_name, namespace, default=None):
    # look for reasons not to do this (the namespace prefix is already
    # applied, or the element doesn't exist to have it applied)
    if element_name.startswith(namespace + ":"):
        return
    if not parent.has_key(element_name):
        return
    
    # construct the name of the new key, with the namespace prefix
    new_key = namespace + ":" + element_name
    
    # initialise the new key, either using the default value or
    # around an existing value
    if not parent.has_key(new_key):
        parent[new_key] = default
    else:
        if type(default) == list:
            _ensure_list(parent, new_key)
    
    # now add or overwrite the value as necessary
    if type(parent[new_key]) == list:
        if type(parent[element_name]) == list:
            for e in parent[element_name]:
                parent[new_key].append(e)
        else:
            parent[new_key].append(parent[element_name])
    else:
        parent[new_key] = parent[element_name]
        
    # finally, remove the old dictionary entry
    del parent[element_name]

def _text_to_value(parent, element_name, idx=None):
    if not parent.has_key(element_name):
        return
    
    if idx is not None:
        element = parent[element_name][idx]
        if not _is_dict(element):
            nd = {"value" : element}
            parent[element_name][idx] = nd
        else:
            element["value"] = element.get("#text", "")
            del element["#text"]
    else:
        element = parent[element_name]
        if not _is_dict(element):
            nd = {"value" : element}
            parent[element_name] = nd
        else:
            element["value"] = element.get("#text", "")
            del element["#text"]

def _descriptive_text_element(parent, element, idx):
    if not parent.has_key(element):
        return
    e = parent[element][idx]
    if _is_dict(e):
        _dte_format(e)
    else:
        _text_to_value(parent, element, idx)
        _strip_cdata(parent[element][idx], "value")

def _temporal_element(parent, element):
    if not parent.has_key(element):
        return
    if _is_dict(parent[element]):
        _te_format(parent[element])
    else:
        _text_to_value(parent, element)

def _te_format(element):
    _rename_key(element, "@dtf", "dtf")
    _rename_key(element, "#text", "value")
    _remove_attributes(element)

def _dte_format(element):
    _rename_key(element, "@xml:lang", "lang")
    _rename_key(element, "@href", "href")
    _rename_key(element, "#text", "value")
    _remove_attributes(element)
    _strip_cdata(element, "value")

def _strip_cdata(element, key):
    v = element.get(key, "")
    if v is None:
        return
    if v.startswith("<![CDATA["):
        v = v[9:]
    if v.endswith("]]>"):
        v = v[:-3]
    element[key] = v
    

def _rename_key(parent, original, new_key, format=None):
    if not parent.has_key(original):
        return
    if not parent.has_key(new_key):
        parent[new_key] = format
    if type(parent[new_key]) == list:
        parent[new_key].append(parent[original])
    else:
        parent[new_key] = parent[original]
    del parent[original]

def cleanup_catalog(catalog):
    """
    "catalog" : {
        "provider" : [ ]
    }
    """
    _remove_dud_text(catalog)
    _remove_attributes(catalog)
    _ensure_list(catalog, "provider")
    for prov in catalog.get('provider', []):
        cleanup_provider(prov)

def cleanup_provider(provider):
    """
    {
        "dc:contributor" : ["contributor"],
        "dc:description" : [{"lang" : "lang", "href" : "href", "value" : "value" }],
        "dc:identifier" : [{ "type" : "type", "value" : "value"}],
        "image" : {"src" : "src","title" : "title","alt" : "alt" },
        "dc:subject" : [{"type" : "type","identifier" : "identifier","lang" : "lang","value" : "value"}],
        "dc:title" : [{"lang" : "lang","value" : "value"}],
        "dc:type" : "type",
        "mlo:url" : "url",
        "mlo:location" : {
            "mlo:street" : "street",
            "mlo:town" : "town",
            "mlo:postcode" : "postcode",
            "mlo:phone" : "phone",
            "mlo:fax" : "fax",
            "mlo:email" : "email",
            "mlo:url" : "url",
            "mlo:address" : [{"type" : "type", "value" : "value"}]
        }
        "course" : [ ]
    }
    """
    _remove_dud_text(provider)
    
    _prepend_namespace(provider, "contributor", "dc", [])
    _ensure_list(provider, "dc:contributor")
    for i in range(len(provider.get("dc:contributor", []))):
        _ensure_obj_to_text(provider, "dc:contributor", i)
    
    _prepend_namespace(provider, "description", "dc", [])
    _ensure_list(provider, "dc:description")
    for i in range(len(provider.get('dc:description', []))):
        _descriptive_text_element(provider, "dc.description", i)
    
    _prepend_namespace(provider, "identifier", "dc", [])
    _ensure_list(provider, "dc:identifier")
    for i in range(len(provider.get('dc:identifier', []))):
        cleanup_identifier(provider, "dc:identifier", i)
    
    if provider.has_key("image"):
        cleanup_image(provider['image'])
        
    _prepend_namespace(provider, "subject", "dc", [])
    _ensure_list(provider, "dc:subject")
    for i in range(len(provider.get("dc:subject", []))):
        cleanup_subject(provider, "dc:subject", i)
    
    _prepend_namespace(provider, "title", "dc", [])
    _ensure_list(provider, "dc:title")
    for i in range(len(provider.get("dc:title", []))):
        cleanup_title(provider, "dc:title", i)
    
    _prepend_namespace(provider, "type", "dc")
    _ensure_obj_to_text(provider, "dc:type")
    
    _prepend_namespace(provider, "url", "mlo")
    _ensure_obj_to_text(provider, "mlo:url")
    
    _prepend_namespace(provider, "location", "mlo")
    if provider.has_key("mlo:location"):
        cleanup_location(provider, "mlo:location")
    
    _ensure_list(provider, "course")
    for course in provider.get('course', []):
        cleanup_course(course)
    
def cleanup_course(course):
    """
    {
        "mlo:level" : "level",
        "mlo:qualification" : [ ],
        "presentation" : [ ],
        "mlo:credit" : [{"credit:scheme" : "scheme", "credit:level" : "level", "credit:value" : "value"}],
        "dc:contributor" : ["contributor"],
        "dc:description" : [{"lang" : "lang", "href" : "href", "value" : "value"}],
        "dc:identifier" : [{"type" : "type","value" : "value"}],
        "image" : {"src" : "src","title" : "title","alt" : "alt"},
        "dc:subject" : [{"type" : "type","identifier" : "identifier","lang" : "lang","value" : "value"}],
        "dc:title" : [{"lang" : "lang","value" : "value"}],
        "dc:type" : "type",
        "mlo:url" : "url",
        "abstract" : [{"lang" : "lang", "href" : "href", "value" : "value"}],             
        "applicationProcedure" : [{"lang" : "lang", "href" : "href", "value" : "value"}],
        "mlo:assessment" : [{"lang" : "lang", "href" : "href", "value" : "value"}],
        "learningOutcome" : [{"lang" : "lang", "href" : "href", "value" : "value"}],
        "mlo:objective" : [{"lang" : "lang", "href" : "href", "value" : "value"}],
        "mlo:prerequisite" : [{"lang" : "lang", "href" : "href", "value" : "value"}],
        "regulations" : [{"lang" : "lang", "href" : "href", "value" : "value"}]
    }
    """
    _remove_dud_text(course)
    
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
    
    _prepend_namespace(course, "contributor", "dc", [])
    _ensure_list(course, "dc:contributor")
    for i in range(len(course.get("dc:contributor", []))):
        _ensure_obj_to_text(course, "dc:contributor", i)
    
    _prepend_namespace(course, "description", "dc", [])
    _ensure_list(course, "dc:description")
    for i in range(len(course.get('dc:description', []))):
        _descriptive_text_element(course, "dc:description", i)
        
    _prepend_namespace(course, "identifier", "dc", [])
    _ensure_list(course, "dc:identifier")
    for i in range(len(course.get('dc:identifier', []))):
        cleanup_identifier(course, "dc:identifier", i)
        
    if course.has_key("image"):
        cleanup_image(course[image])
        
    _prepend_namespace(course, "subject", "dc", [])
    _ensure_list(course, "dc:subject")
    for i in range(len(course.get("dc:subject", []))):
        cleanup_subject(course, "dc:subject", i)
        
    _prepend_namespace(course, "title", "dc", [])
    _ensure_list(course, "dc:title")
    for i in range(len(course.get("dc:title", []))):
        cleanup_title(course, "dc:title", i)
    
    _prepend_namespace(course, "type", "dc")
    _ensure_obj_to_text(course, "dc:type")
    
    _prepend_namespace(course, "url", "mlo")
    _ensure_obj_to_text(course, "mlo:url")
    
    _ensure_list(course, "abstract")
    for i in range(len(course.get('abstract', []))):
        _descriptive_text_element(course, "abstract", i)
        
    _ensure_list(course, "applicationProcedure")
    for i in range(len(course.get('applicationProcedure', []))):
        _descriptive_text_element(course, "applicationProcedure", i)
    
    _prepend_namespace(course, "assessment", "mlo", [])
    _ensure_list(course, "mlo:assessment")
    for i in range(len(course.get('mlo:assessment', []))):
        _descriptive_text_element(course, "mlo:assessment", i)
    
    _ensure_list(course, "learningOutcome")
    for i in range(len(course.get('learningOutcome', []))):
        _descriptive_text_element(course, "learningOutcome", i)
    
    _prepend_namespace(course, "objective", "mlo", [])
    _ensure_list(course, "mlo:objective")
    for i in range(len(course.get('mlo:objective', []))):
        _descriptive_text_element(course, "mlo:objective", i)
    
    _prepend_namespace(course, "prerequisite", "mlo", [])
    _ensure_list(course, "mlo:prerequisite")
    for i in range(len(course.get('mlo:prerequisite', []))):
        _descriptive_text_element(course, "mlo:prerequisite", i)
    
    _ensure_list(course, "regulations")
    for i in range(len(course.get('regulations', []))):
        _descriptive_text_element(course, "regulations", i)

def cleanup_location(parent, location):
    """
    {
        "mlo:street" : "street",
        "mlo:town" : "town",
        "mlo:postcode" : "postcode",
        "mlo:phone" : "phone",
        "mlo:fax" : "fax",
        "mlo:email" : "email",
        "mlo:url" : "url",
        "mlo:address" : [{"type" : "type", "value" : "value"}]
    }
    """
    loc = parent[location]
    _remove_dud_text(loc)
    
    _prepend_namespace(loc, "street", "mlo")
    _ensure_text(loc, "mlo:street")
    
    _prepend_namespace(loc, "town", "mlo")
    _ensure_text(loc, "mlo:town")
    
    _prepend_namespace(loc, "postcode", "mlo")
    _ensure_text(loc, "mlo:postcode")
    
    _prepend_namespace(loc, "phone", "mlo")
    _ensure_text(loc, "mlo:phone")
    
    _prepend_namespace(loc, "fax", "mlo")
    _ensure_text(loc, "mlo:fax")
    
    _prepend_namespace(loc, "email", "mlo")
    _ensure_text(loc, "mlo:email")
    
    _prepend_namespace(loc, "url", "mlo")
    _ensure_text(loc, "mlo:url")
    
    _prepend_namespace(loc, "address", "mlo")
    _ensure_list(loc, "mlo:address")
    for i in range(len(loc.get("mlo:address", []))):
        cleanup_address(loc, "mlo:address", i)
    

def cleanup_address(parent, address, idx):
    """
    {"type" : "type", "value" : "value"}
    """
    _text_to_value(parent, address, idx)
    _rename_key(parent[address][idx], "@xsi:type", "type")
    _remove_attributes(parent[address][idx])

def cleanup_identifier(parent, identifier_key, idx):
    # convert to object and set the #text field correctly
    _text_to_value(parent, identifier_key, idx)
    _rename_key(parent[identifier_key][idx], "@xsi:type", "type")
    _remove_attributes(parent[identifier_key][idx])

def cleanup_title(parent, title, idx):
    """
    {"lang" : "lang","value" : "value"}
    """
    _text_to_value(parent, title, idx)
    _rename_key(parent[title][idx], "@xml:lang", "lang")
    _remove_attributes(parent[title][idx])

def cleanup_subject(parent, subject, idx):
    """
    {"type" : "type","identifier" : "identifier","lang" : "lang","value" : "value"}
    """
    _text_to_value(parent, subject, idx)
    _rename_key(parent[subject][idx], "@xsi:type", "type")
    _rename_key(parent[subject][idx], "@identifier", "identifier")
    _rename_key(parent[subject][idx], "@xml:lang", "lang")
    _remove_attributes(parent[subject][idx])
    
def cleanup_image(image):
    """
    {"src" : "src","title" : "title","alt" : "alt" }
    """
    _remove_dud_text(image)
    _rename_key(image, "@src", "src")
    _rename_key(image, "@title", "title")
    _rename_key(image, "@alt", "alt")
    _remove_attributes(image)
 
def cleanup_credit(credit):
    """
    {"credit:scheme" : "scheme", "credit:level" : "level", "credit:value" : "value"}
    """
    _remove_dud_text(credit)
    _prepend_namespace(credit, "scheme", "credit")
    _ensure_text(credit, "credit:scheme")
    _prepend_namespace(credit, "level", "credit")
    _ensure_text(credit, "credit:level")
    _prepend_namespace(credit, "value", "credit")
    _ensure_text(credit, "credit:value")
    _remove_attributes(credit)

def cleanup_presentation(pres):
    """
    {
        "dc:description" : [{"lang" : "lang", "href" : "href", "value" : "value"}],
        "dc:identifier" : [{"type" : "type","value" : "value"}],
        "image" : {"src" : "src","title" : "title","alt" : "alt"},
        "dc:subject" : [{"type" : "type","identifier" : "identifier","lang" : "lang","value" : "value"}],
        "dc:title" : [{"lang" : "lang","value" : "value"}],
        "dc:type" : "type",
        "mlo:url" : "url",
        "abstract" : [{"lang" : "lang", "href" : "href", "value" : "value"}],             
        "applicationProcedure" : [{"lang" : "lang", "href" : "href", "value" : "value"}],
        "mlo:assessment" : [{"lang" : "lang", "href" : "href", "value" : "value"}],
        "learningOutcome" : [{"lang" : "lang", "href" : "href", "value" : "value"}],
        "mlo:objective" : [{"lang" : "lang", "href" : "href", "value" : "value"}],
        "mlo:prerequisite" : [{"lang" : "lang", "href" : "href", "value" : "value"}],
        "regulations" : [{"lang" : "lang", "href" : "href", "value" : "value"}]
        "mlo:start" : {"dtf" : "datetime", "value" : "value"},
        "mlo:end" : {"dtf" : "datetime", "value" : "value"},
        "mlo:duration" : {"interval" : "interval", "value" : "value"},
        "applyFrom" : {"dtf" : "datetime", "value" : "value"},
        "applyUntil" : {"dtf" : "datetime", "value" : "value"},
        "applyTo" : "apply to",
        "mlo:engagement" : [{}],
        "studyMode" : {"identifier" : "identifier", "value" : "value"},
        "attendanceMode" : {"identifier" : "identifier", "value" : "value"},
        "attendancePattern" : {"identifier" : "identifier", "value" : "value"},
        "mlo:languageOfInstruction" : ["lang"],
        "languageOfAssessment" : ["lang"],
        "mlo:places" : "places",
        "mlo:cost" : "cost",
        "age" : "age",
        "venue" : [ ]
    }
    """
    _remove_dud_text(pres)
    
    _prepend_namespace(pres, "description", "dc", [])
    _ensure_list(pres, "dc:description")
    for i in range(len(pres.get('dc:description', []))):
        _descriptive_text_element(pres, "dc:description", i)
        
    _prepend_namespace(pres, "identifier", "dc", [])
    _ensure_list(pres, "dc:identifier")
    for i in range(len(pres.get('dc:identifier', []))):
        cleanup_identifier(pres, "dc:identifier", i)
        
    if pres.has_key("image"):
        cleanup_image(pres[image])
        
    _prepend_namespace(pres, "subject", "dc", [])
    _ensure_list(pres, "dc:subject")
    for i in range(len(pres.get("dc:subject", []))):
        cleanup_subject(pres, "dc:subject", i)
        
    _prepend_namespace(pres, "title", "dc", [])
    _ensure_list(pres, "dc:title")
    for i in range(len(pres.get("dc:title", []))):
        cleanup_title(pres, "dc:title", i)
    
    _prepend_namespace(pres, "type", "dc")
    _ensure_obj_to_text(pres, "dc:type")
    
    _prepend_namespace(pres, "url", "mlo")
    _ensure_obj_to_text(pres, "mlo:url")
    
    _ensure_list(pres, "abstract")
    for i in range(len(pres.get('abstract', []))):
        _descriptive_text_element(pres, "abstract", i)
        
    _ensure_list(pres, "applicationProcedure")
    for i in range(len(pres.get('applicationProcedure', []))):
        _descriptive_text_element(pres, "applicationProcedure", i)
    
    _prepend_namespace(pres, "assessment", "mlo", [])
    _ensure_list(pres, "mlo:assessment")
    for i in range(len(pres.get('mlo:assessment', []))):
        _descriptive_text_element(pres, "mlo:assessment", i)
    
    _ensure_list(pres, "learningOutcome")
    for i in range(len(pres.get('learningOutcome', []))):
        _descriptive_text_element(pres, "learningOutcome", i)
    
    _prepend_namespace(pres, "objective", "mlo", [])
    _ensure_list(pres, "mlo:objective")
    for i in range(len(pres.get('mlo:objective', []))):
        _descriptive_text_element(pres, "mlo:objective", i)
    
    _prepend_namespace(pres, "prerequisite", "mlo", [])
    _ensure_list(pres, "mlo:prerequisite")
    for i in range(len(pres.get('mlo:prerequisite', []))):
        _descriptive_text_element(pres, "mlo:prerequisite", i)
    
    _ensure_list(pres, "regulations")
    for i in range(len(pres.get('regulations', []))):
        _descriptive_text_element(pres, "regulations", i)
        
    _prepend_namespace(pres, "start", "mlo")
    _temporal_element(pres, "mlo:start")
    
    _prepend_namespace(pres, "end", "mlo")
    _temporal_element(pres, "mlo:end")
    
    _prepend_namespace(pres, "duration", "mlo")
    _temporal_element(pres, "mlo:duration")
    
    _temporal_element(pres, "applyFrom")
    
    _temporal_element(pres, "applyUntil")
    
    if pres.has_key("applyTo"):
        _ensure_text(pres, "applyTo")
    
    # not enough information about mlo:engagement to do any serious cleanup on it
    _prepend_namespace(pres, "engagement", "mlo", [])
    
    if pres.has_key("studyMode"):
        cleanup_mode(pres, "studyMode")
    
    if pres.has_key("attendanceMode"):
        cleanup_mode(pres, "attendanceMode")
    
    if pres.has_key("attendancePattern"):
        cleanup_mode(pres, "attendancePattern")
        
    _prepend_namespace(pres, "languageOfInstruction", "mlo", [])
    _ensure_list(pres, "mlo:languageOfInstruction")
    for i in range(len(pres.get("mlo:languageOfInstruction", []))):
        _ensure_obj_to_text(pres, "mlo:languageOfInstruction", i)
        
    _ensure_list(pres, "languageOfAssessment")
    for i in range(len(pres.get("languageOfAssessment", []))):
        _ensure_obj_to_text(pres, "languageOfAssessment", i)
        
    _prepend_namespace(pres, "places", "mlo")
    _ensure_text(pres, "mlo:places")
    
    _prepend_namespace(pres, "cost", "mlo")
    _ensure_text(pres, "mlo:cost")
    
    _prepend_namespace(pres, "age", "mlo")
    _ensure_text(pres, "mlo:age")
    
    _ensure_list(pres, "venue")
    for i in range(len(pres.get("venue", []))):
        cleanup_venue(pres, "venue", i)

def cleanup_venue(parent, venue, idx):
    element = parent[venue][idx]
    _remove_dud_text(element)
    if not _is_dict(element):
        # not spec conformant, so delete
        del parent[venue][idx]
        return
    if element.has_key("provider"):
        cleanup_provider(element["provider"])

def cleanup_mode(parent, mode):
    """
    {"identifier" : "identifier", "value" : "value"}
    """
    _text_to_value(parent, mode)
    _rename_key(parent[mode], "@identifier", "identifier")
    _remove_attributes(parent[mode])

def cleanup_qualification(qual):
    """
    {
        "dc:identifier" : [{"type" : "type","value" : "value"}],
        "dc:title" : [{"lang" : "lang","value" : "value"}],
        "abbr" : "abbr",
        "dc:description" : [{"lang" : "lang","href" : "href","value" : "value"}],
        "dcterms:educationLevel" : ["education level"],
        "dc:type" : "type",
        "mlo:url" : "url",
        "awardedBy" : "awarded by",
        "accreditedBy" : "accredited by"
    }
    """
    _remove_dud_text(qual)
    
    _prepend_namespace(qual, "identifier", "dc", [])
    _ensure_list(qual, "dc:identifier")
    for i in range(len(qual.get('dc:identifier', []))):
        cleanup_identifier(qual, "dc:identifier", i)
    
    _prepend_namespace(qual, "title", "dc", [])
    _ensure_list(qual, "dc:title")
    for i in range(len(qual.get("dc:title", []))):
        cleanup_title(qual, "dc:title", i)
    
    if qual.has_key("abbr"):
        _ensure_text(qual, "abbr")
        
    _prepend_namespace(qual, "description", "dc", [])
    _ensure_list(qual, "dc:description")
    for i in range(len(qual.get('dc:description', []))):
        _descriptive_text_element(qual, "dc:description", i)
    
    _prepend_namespace(qual, "educationLevel", "dcterms", [])
    _ensure_list(qual, "dcterms:educationLevel")
    for i in range(len(qual.get("dcterms:educationLevel", []))):
        _ensure_obj_to_text(qual, "dcterms:educationLevel", i)
    
    _prepend_namespace(qual, "type", "dc")
    _ensure_obj_to_text(qual, "dc:type")
    
    _prepend_namespace(qual, "url", "mlo")
    _ensure_obj_to_text(qual, "mlo:url")
    
    # we don't know enough about awardedBy and accreditedBy, so 
    # just leave them alone

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