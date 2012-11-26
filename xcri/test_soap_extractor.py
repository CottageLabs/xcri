import unittest
import soap_extractor

class TestSoapExtractor(unittest.TestCase):
    def test_01_get_ou_data(self):
        wsdl_url = 'http://host.igsl.co.uk:7101/OU-webservice-context-root/xxpSoapHttpPort?WSDL'
        operation = "getOUCourses"
        argument = "ALL"
        result = soap_extractor.get_coursedata(wsdl_url, operation, argument)
        # for the moment, this just completing is the success test
        
