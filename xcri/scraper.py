"""
Example:
<tr>
    <td>XXP</td>
    <td><a href="xcriinfo?fed_id=1049" >Yarborough School (14-19)</a></td>
    <td>SOAP</td>
    <td align="center">1.1</td>
    <td align="center" width="20px"><img src="images/tick.png" alt="XCRI-CAP data has passed validity/quality checks" title="XCRI-CAP data has passed validity/quality checks" height="16" width="16" /></td>
</tr>
"""

import requests, re, json, sys

OUT_FILE = sys.argv[1]

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

j = json.dumps(out)

with open(OUT_FILE, "wb") as f:
    f.write(j)
