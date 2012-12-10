"""
Example:
<tr>
    <td>XXP</td>
    <td><a href="xcriinfo?fed_id=1049" >Yarborough School (14-19)</a></td>
    <td>SOAP</td>
    <td align="center">1.1</td>
    <td align="center" width="20px"><img src="images/tick.png" alt="XCRI-CAP data has passed validity/quality checks" title="XCRI-CAP data has passed validity/quality checks" height="16" width="16" /></td>
</tr>

<div id="content-container-2">
 <p class="header1">XCRI feed information for
    Cornwall College</p>             
  <div class="xxp-form">
      <fieldset>
        <legend>XCRI feed Details</legend>
        <table>
          <tr>
            <td>
              <label>Name:</label>
            </td>
            <td>
              <input  readonly="readonly" value="Cornwall College" style="width:300px;"/>
            </td>
          </tr>
          <tr>
            <td>
              <label>Feed ID:</label>
            </td>
            <td>
              <input  readonly="readonly" value="" style="width:300px;"/>
            </td>
          </tr>
          <tr>                      
            <td>
              <label>Description:</label>
            </td>
            <td >
              <textarea cols="100" rows="6" readonly="readonly"
                        style="width:300px;">Main XCRI Feed</textarea>
            </td>
          </tr>
          <tr>
            <td>
              <label>Data link: </label>
            </td>
            <td>
              <input  value="http://www.cornwall.ac.uk/XCRI.xml" readonly="readonly" style="width:300px;"/>
            </td>
          </tr>
          <tr>
            <td>
              <label >Website: </label>
            </td>
            <td>
              <input  readonly="readonly" value="www.cornwall.ac.uk" style="width:300px;"/>
            </td>
          </tr>                      
          <tr>
            <td>
              <label>Provider Email:</label>
            </td>
            <td>
              <input  readonly="readonly" value="mike.trebilcock@cornwall.ac.uk" style="width:300px;"/>
            </td>
          </tr>
          <tr>
            <td>
              <label>Technical support:</label>
            </td>
            <td>
              <input  readonly="readonly" value="" style="width:300px;"/>
            </td>
          </tr>                    
        <tr>
          <td>
            <label>Type:</label>
          </td>
          <td>
            <select disabled="disabled">
              <option value="W">SOAP</option><option value="R">RESTful</option><option value="F">FTP</option><option selected="selected" value="H">HTTP</option><option value="S">HTTPs</option>
            </select>
          </td>
        </tr> 
        <tr>
          <td>
            <label>XCRI-CAP version:</label>
          </td>
          <td>
            <select disabled="disabled">
              <option value="1.0">XCRI-CAP 1.0</option><option value="1.1">XCRI-CAP 1.1</option><option selected="selected" value="1.2">XCRI-CAP 1.2</option>
            </select>
          </td>
        </tr>
          <tr>
        <td colspan="2" style="text-align: center;">
         <br/><a href="#" id="back_2_list" class="ui-state-default ui-corner-all" >
        <span class="ui-icon ui-icon-arrowreturnthick-1-w"></span>Back</a>
        </td>
      </tr>
        </table>
      </fieldset>                 
  </div>
</div>

"""

import requests, re, json, sys

MODE = sys.argv[1]

if MODE == "directory":
    OUT_FILE = sys.argv[2]
    
    base_url = "http://xxp.igsl.co.uk/app/"
    resp = requests.get("http://xxp.igsl.co.uk/app/xcridirectory")
    rx = '<tr>.*?<td>.*?</td>.*?<td><a href=\"(xcriinfo\?fed_id=\d+)\" >(.*?)</a>.*?<td align=\"center\">(.*?)</td>.*?</tr>'
    ms = re.findall(rx, resp.text, re.DOTALL)
    out = []
    for m in ms:
        url = base_url + m[0]
        org = m[1]
        version = m[2]
        out.append({ "url": url, "version": version, "name": org })
    
    j = json.dumps(out, indent=4)
    
    with open(OUT_FILE, "wb") as f:
        f.write(j)

elif MODE == "sources":
    IN_FILE = sys.argv[2]
    OUT_FILE = sys.argv[3]
    
    j = json.load(open(IN_FILE, "r"))
    rx = "<div class=\"xxp-form\">.*?<label>Name:</label>.*?value=\"(.*?)\".*?<label>Data link: </label>.*?value=\"(.*?)\".*?<label >Website: </label>.*?value=\"(.*?)\".*?<label>Type:</label>.*?<option selected=\"selected\".*?>(.*?)</option>"
    
    print "Scraping " + str(len(j)) + " sources"
    
    for record in j:
        print record['url']
        resp = requests.get(record['url'])
        m = re.search(rx, resp.text, re.DOTALL)
        
        data = m.group(2)
        website = m.group(3)
        type = m.group(4)
        
        if type == "HTTP":
            type = "REST"
        if type == "RESTful":
            type = "REST"
        
        if type == "REST":
            record['resource_url'] = data
        elif type == "SOAP":
            record['wsdl_url'] = data
            record["operation"] = "getCourses"
            record["arguments"] = []
        
        record['website'] = website
        record['type'] = type
        print "...done\n"

    dump = json.dumps(j, indent=4)
    with open(OUT_FILE, "wb") as f:
        f.write(dump)
        
        
        