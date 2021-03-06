XCRI
====

All our great demo stuff for XCRI-CAP course feeds, for the JISC XCRI-CAP course feeds demonstrator project

Directory Data Extractor
------------------------

The main directory of XCRI feeds is The XCRI Directory: [http://xxp.igsl.co.uk/app/xcridirectory](http://xxp.igsl.co.uk/app/xcridirectory).  This directory does not currently provide an API, so this code library provides a scraper which will obtain machine readable records for use in our course data extraction features.

To obtain a list of all the records in the directory, first scrape the directory home page:

    python scraper.py directory <directory scraper output file>
    
This will scrape all the records on the [http://xxp.igsl.co.uk/app/xcridirectory](http://xxp.igsl.co.uk/app/xcridirectory) page.  Note that as a user, this page only presents 10 records at a time, but this appears to be a javascript feature, and requesting the raw HTML of the page gives you all of the records.

Now we can augment the information obtained from the directory page, by scraping the individual record pages:

    python scraper.py sources <directory scraper output file> <output file>

This will scrape each individual record, and produce an augmented output file which contains almost enough detail to move on to extract the XCRI data itself.  Unfortunately, the last step requires manual intervention:

Open the [output file] created in the previous step, and work through it, visiting the website/record for each source and finding the SOAP method and optional method argument, and adding to the json record for the source.  For example, starting with:

    {
        "website": "http://www.xxp.org/getlincscourses.html", 
        "name": "Tennyson High School (14-19)", 
        "url": "http://xxp.igsl.co.uk/app/xcriinfo?fed_id=1046", 
        "wsdl_url": "http://host.igsl.co.uk:7101/Lincs-webservice-context-root/xxpSoapHttpPort?WSDL", 
        "version": "1.1", 
        "arguments": [], 
        "operation": "getCourses", 
        "type": "SOAP"
    }

Visit the "url", and verify the "operation" (in this case it should be getLincsCourses), and whether any "arguments" are required (in this case "10017033"), so the final record should become:

    {
        "website": "http://www.xxp.org/getlincscourses.html", 
        "name": "Tennyson High School (14-19)", 
        "url": "http://xxp.igsl.co.uk/app/xcriinfo?fed_id=1046", 
        "wsdl_url": "http://host.igsl.co.uk:7101/Lincs-webservice-context-root/xxpSoapHttpPort?WSDL", 
        "version": "1.1", 
        "arguments": ["10017033"], 
        "operation": "getLincsCourses", 
        "type": "SOAP"
    }

Once all the records have been augmented in this way, you can move on to the Course Data Extractor

Course Data Extractor
---------------------

In order to run the Course Data Extractor, you will need a source file containing json records for the SOAP and REST based endpoints.  These can be scraped from the XCRI Directory ([http://xxp.igsl.co.uk/app/xcridirectory](http://xxp.igsl.co.uk/app/xcridirectory)), using the scraper described in the previous section.

For SOAP web services, a record should look similar to the following:

    {
        "website": "http://www.xxp.org/getlincscourses.html", 
        "name": "Walton Girls High School (14-19)", 
        "url": "http://xxp.igsl.co.uk/app/xcriinfo?fed_id=1047", 
        "wsdl_url": "http://host.igsl.co.uk:7101/Lincs-webservice-context-root/xxpSoapHttpPort?WSDL", 
        "version": "1.1", 
        "arguments": ["10013314"], 
        "operation": "getLincsCourses", 
        "type": "SOAP"
    }
    
For REST web services, a record should look similar to the following:

    {
        "website": "http://llnmoodle.worc.ac.uk/portalmoodle/course/view.php?id=51", 
        "name": "University of Worcester", 
        "url": "http://xxp.igsl.co.uk/app/xcriinfo?fed_id=1054", 
        "version": "1.1", 
        "resource_url": "http://llnmoodle.worc.ac.uk/portalmoodle/file.php/51/final_uwxcr.xml", 
        "type": "REST"
    }

For each source, the obtain.py script will request either the resource_url (for a REST web service) or will run the "operation" against the SOAP web service for each "argument", and write the resulting XML out to a file.

To invoke the obtain.py script, just use:

    python obtain.py -s <sources json file> -o <output dir>

You can also find the full list of arguments supported by obtain.py, by using:

    python obtain.py --help

"output dir" is the directory you'd like to write the resulting files to.  File names will be of the form:

    <service name>[_<argument>].xml

So the above two examples would produce the following files:

    Walton Girls High School (14-19)_10013314.xml
    University of Worcester.xml

Each of these files will contain raw XCRI XML data.


Upgrading XCRI data to version 1.2
----------------------------------

Prior to attempting to convert the data to JSON for indexing, it is necessary to upgrade all XCRI 1.1 feeds to XCRI 1.2.  This can be done easily by running the upgrade.py script:

    python upgrade.py -d <original xml files directory> -o <1.2 xml files output directory>
    
This will read all XML files from the **original xml files directory** and - if necessary - apply an XSLT transformation to bring it up to XCRI 1.2.  It will then write the file (whether it has been upgraded or not) to the **1.2 xml files output directory**, which are then suitable for conversion to JSON.

When copied, the filename will remain the same, so if the -o option is omitted, the original version of the file will be overwritten.


Converting XCRI XML to XCRI JSON
--------------------------------

For the purposes of indexing the data, it can be convenient to have the data format in JSON rather than XML.  We have devised a basic JSON schema for XCRI which can be seen in the **xcri.json** file next to this README.

To convert from XML to JSON use the xcrixml2json.py script:

    python xcrixml2json.py -d <1.2 xml files output directory> -o <json output directory>

This will read all XML files from the **1.2 xml files output directory** and convert them to XCRI JSON suitable for indexing, placed in the **json output directory**.  Filenames are as they are in XML, but the .xml extension is replaced with .json.

*Note, this software uses a generic mapping tool from XML to JSON called **xmltojson**, which is included in this source code.  Please see **xmltojson.LICENSE** for licensing conditions.*

*Note, this software uses an XSLT transform taken from the XCRI Knowledge Base, which is included in this source code.  Please see **xcri-cap_xslt.README** for more details*


