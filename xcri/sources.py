import json

class Endpoints(object):

    def __init__(self, source_file_path):
        self.source_file_path = source_file_path
        self.source = json.load(open(self.source_file_path))
    
    def soap_endpoints(self):
        return [e for e in self.source if e['type'] == "SOAP"]
        
    def rest_endpoints(self):
        return [e for e in self.source if e['type'] == "REST"]
    
"""
soap_endpoints = [
    {
        "name" : "OpenUniversity",
        "wsdl_url" : "http://host.igsl.co.uk:7101/OU-webservice-context-root/xxpSoapHttpPort?WSDL",
        "operation" : "getOUCourses",
        "arguments" : ["ALL"]
    },
    
    {
        "name" : "LincolnshireTeenageServices",
        "wsdl_url" : "http://host.igsl.co.uk:7101/Lincs-webservice-context-root/xxpSoapHttpPort?WSDL",
        "operation" : "getLincsCourses",
        "arguments" : ["10011155", "10000812"]
    }
]

rest_endpoints = [
    {
        "name" : "AdamSmithCollege",
        "resource_url": "http://www.adamsmith.ac.uk/onlineresources/ictassets/xcri/cap.xml",
        "xcri_version" : "1.2"
    },
    
    {
        "name" : "Bradford College",
        "resource_url": "http://www2.bradfordcollege.ac.uk/bradfordcollege.xml",
        "xcri_version" : "1.1"
    },
    
    
]
"""