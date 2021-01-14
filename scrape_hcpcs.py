from datetime import datetime
from doltpy.core import Dolt
import mysql.connector
import urllib.request
import re
from html.parser import HTMLParser

class SectionParser(HTMLParser):
    def __init__(self):
        self.output = [] 
        super().__init__()
    def handle_any(self, data, attrs=None):
        pass
    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        if tag == 'a':
            for x,y in attrs:
                if x == "href":
                    self.output.append(y)
        self.handle_any(tag, attrs)
    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        self.handle_any(tag)
    def handle_data(self, data):
        #print("Encountered some data  :", data)
        self.handle_any(data)

class CodeParser(HTMLParser):
    def __init__(self):
        self.count = 0
        self.trigger = -1
        self.output = dict()
        super().__init__()
    def handle_any(self, data, attrs=None):
        if "Long description:" in data:
            self.capture = "long_description"
            self.count = 0
            self.trigger = 4
        elif "Short description:" in data:
            self.capture = "short_description"
            self.count = 0
            self.trigger = 4
        elif "HCPCS Pricing indicator" in data:
            self.capture = "pricing_indicator"
            self.count = 0
            self.trigger = 11
        elif "Multiple pricing indicator" in data:
            self.capture = "multiple_pricing_indicator"
            self.count = 0
            self.trigger = 11
        elif "Coverage code" in data:
            self.capture = "coverage_code"
            self.count = 0
            self.trigger = 10
        elif "BETOS" in data:
            self.capture = "betos_code"
            self.count = 0
            self.trigger = 14
        elif "Type of service" in data:
            self.capture = "type_of_service"
            self.count = 0
            self.trigger = 12
        elif "Effective date" in data:
            self.capture = "effective_date"
            self.count = 0
            self.trigger = 9
        elif "Date added" in data:
            self.capture = "date_added"
            self.count = 0
            self.trigger = 9
        if self.count == self.trigger:
            if self.capture not in self.output:
                self.output[self.capture] = data.strip()
            if self.capture == "pricing_indicator":
                self.count = 0
                self.trigger = 2
                self.capture = "pricing_indicator_desc"
            elif self.capture == "multiple_pricing_indicator":
                self.count = 0
                self.trigger = 2
                self.capture = "multiple_pricing_indicator_desc"
            elif self.capture == "coverage_code":
                self.count = 0
                self.trigger = 2
                self.capture = "coverage_code_desc"
            elif self.capture == "betos_code":
                self.count = 0
                self.trigger = 2
                self.capture = "betos_code_desc"
            else:
                self.trigger = -1
        self.count += 1
    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        self.handle_any(tag, attrs)

    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        self.handle_any(tag)

    def handle_data(self, data):
        #print("Encountered some data  :", data)
        self.handle_any(data)
    def clean(self):
        for key in ["pricing_indicator_desc", "multiple_pricing_indicator_desc", "coverage_code_desc", "betos_code_desc", "type_of_service"]:
            if key in self.output and self.output[key][:2] == '- ':
                self.output[key] = self.output[key][2:]
            key = "effective_date"
        if key in self.output:
            try:
                temp = datetime.strptime(self.output[key], 'Effective %b %d, %Y')
                self.output[key] = temp.strftime('%Y-%m-%d')
            except ValueError:
                self.output[key] = None
        key = "date_added"
        if key in self.output:
            try:
                temp = datetime.strptime(self.output[key], 'Added %b %d, %Y')
                self.output[key] = temp.strftime('%Y-%m-%d')
            except ValueError:
                self.output[key] = None

def dump_code(data):
    connection = mysql.connector.connect(user='root',
                                     host="127.0.0.1",
                                     port=3307,
                                     database='hospital_transparency_data')
    cursor = connection.cursor(buffered=True)
    cursor.execute('SET @@autocommit = 1')
    items = data.items()
    keys = ','.join([x[0] for x in items])
    formats = ','.join(['%s' for x in items])
    values = [x[1] for x in items]
    query = "INSERT INTO hcpcs ({0}) VALUES ({1})".format(keys, formats)
    cursor.execute(query, values)
home = 'https://hcpcs.codes'
#url = 'https://hcpcs.codes/a-codes/A0021/'
for i in range(22):
    y = chr(97+i)
    if y not in {'d','f','i','n','o'}:
        subdir = '{0}-codes'.format(y)
        urls = []
        oldLen = -1
        j = 1
        while oldLen < len(urls):
            oldLen = len(urls)
            url = 'https://hcpcs.codes/{0}/?page={1}'.format(subdir, j)
            with urllib.request.urlopen(url) as f:
                text = f.read().decode()
                parser = SectionParser()
                parser.feed(text)
                for x in [x for x in parser.output if subdir in x]:
                    m = re.match(r'/'+subdir+'/[A-Z]\\d{4}/', x)
                    if m:
                        urls.append(m.group(0))
            j += 1
        for x in urls:
            with urllib.request.urlopen(home+x) as f:
                text = f.read().decode()
                parser = CodeParser()
                parser.feed(text)
                parser.clean()
                parser.output['code'] = x.split('/')[-2]
                print(parser.output)
                dump_code(parser.output)
