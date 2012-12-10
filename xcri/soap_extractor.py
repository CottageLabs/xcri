from suds.client import Client

def get_coursedata(wsdl_url, operation, argument=None):
    # create a client instance around the wsdl
    client = Client(wsdl_url)
    
    # get the method to be run
    method = getattr(client.service, operation)
    
    # extract the results for the argument
    result = None
    if argument is None:
        result = method()
    else:
        result = method(argument)
    
    # return the result (which is just a massive string right now)
    return result



