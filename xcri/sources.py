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
        "resource_url": "http://www.adamsmith.ac.uk/onlineresources/ictassets/xcri/cap.xml"
    }
]