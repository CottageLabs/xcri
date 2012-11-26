XCRI
====

All our great demo stuff for XCRI-CAP course feeds, for the JISC XCRI-CAP course feeds demonstrator project

SOAP Web Service Course Data Extractor
--------------------------------------

There are a large number of SOAP based web services providing course data, documented in The XCRI Directory: [http://xxp.igsl.co.uk/app/xcridirectory](http://xxp.igsl.co.uk/app/xcridirectory).

In order to extract the XCRI data included therein, we provide some useful scripts here.

First, configure the sources.py file with your desired sources (as the project goes along, we'll fill this up ourselves), giving each source a record like the following:

    {
        "name" : "LincolnshireTeenageServices",
        "wsdl_url" : "http://host.igsl.co.uk:7101/Lincs-webservice-context-root/xxpSoapHttpPort?WSDL",
        "operation" : "getLincsCourses",
        "arguments" : ["10011155", "10000812"]
    }

This gives us the name of the service (up to us what to call it) tells us where the WSDL is located, which SOAP operation to carry out to get the XCRI course data, and the arguments that need to be used.

For each argument, the obtain.py script will run a request against the SOAP server and write the resulting XML out to a file.

To invoke the obtain.py script, just use:

    python obtain.py <outdir>
    
Where <outdir> is the directory you'd like to write the resulting files to.  File names will be of the form:

    <service name>_<argument>.xml
    
So the above example would give us two files:

    <outdir>/LincolnshireTeenageServices_10011155.xml
    <outdir>/LincolnshireTeenageServices_10000812.xml
    
