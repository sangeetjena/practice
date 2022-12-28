from requests_html import HTMLSession

ISSN = "0897-4756"
address = "https://data.binance.vision/?prefix=data/spot/daily/trades/".format(ISSN)

hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

ses = HTMLSession()
response = ses.get(address, headers=hdr)
response.html.render() # render the javascript to load the elements in the table
tree = response.html.lxml # no need to import lxml.html because requests-html can do this for you

for html in response.html:
    print(html)
print(tree.xpath('//*[@id="listing"]/text()'))
# >> ['\n', '\n']

print(tree.xpath('//*[@id="listing"]/tr[2]/td[1]/a/text()'))
# >> ['ACS Publications', '1.905', 'No', '\n', '\n', '\n']


