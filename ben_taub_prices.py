from openpyxl import load_workbook
from doltpy.core import Dolt
import json
import sys
import mysql.connector

def dump_prices(price, hospital, cpt):
    connection = mysql.connector.connect(user='root',
                                     host="127.0.0.1",
                                     port=3307,
                                     database='hospital_price_transparency')
    cursor = connection.cursor(buffered=True)
    cursor.execute('SET @@autocommit = 1')
    query = 'select count(*) from hospitals where npi_number="{0}"'
    query = query.format(hospital['npi_number'])
    cursor.execute(query)
    results = cursor.fetchall()
    if results[0][0] == 0:
        items = hospital.items()
        keys = ','.join([x[0] for x in items])
        formats = ','.join(['%s' for x in items])
        values = [x[1] for x in items]
        query = "INSERT INTO hospitals ({0}) VALUES ({1})".format(keys, formats)
        cursor.execute(query, values)

    query = 'select count(*) from cpt_hcpcs where code="{0}"'
    query = query.format(cpt['code'])
    cursor.execute(query)
    results = cursor.fetchall()
    if results[0][0] == 0:
        items = cpt.items()
        keys = ','.join([x[0] for x in items])
        formats = ','.join(['%s' for x in items])
        values = [x[1] for x in items]
        query = "INSERT INTO cpt_hcpcs ({0}) VALUES ({1})".format(keys, formats)
        cursor.execute(query, values)

    items = price.items()
    keys = ','.join([x[0] for x in items])
    formats = ','.join(['%s' for x in items])
    values = [x[1] for x in items]
    query = "INSERT INTO prices ({0}) VALUES ({1})".format(keys, formats)
    try:
        cursor.execute(query, values)
    except mysql.connector.errors.DatabaseError:
        pass



wb = load_workbook(filename = '2020-12-31 CDM Transparency FY21.xlsx')
sheet_ranges = wb['Sheet1']

hospital = {'npi_number':'1164807624',
            'name':'BEN TAUB GENERAL HOSPITAL',
            'url': 'https://www.harrishealth.org/SiteCollectionDocuments/financials/charge%20description%20master/2020-12-31%20CDM%20Transparency%20FY21.zip',
            'street_address': '1504 TAUB LOOP',
            'city': 'HOUSTON',
            'state': 'TX',
            'zip_code': '77030-1608'
            'publish_date': '2020-12-31'}
for i in range(2, 9867):
    cpt = dict()
    price = dict()
    try:
        price['price'] = float(sheet_ranges['D'+str(i)].value)
    except ValueError:
        continue
    price['code'] = sheet_ranges['B'+str(i)].value
    price['npi_number'] = hospital['npi_number']
    price['payer'] = 'CASH'
    cpt['code'] = price['code']
    cpt['short_description'] = sheet_ranges['A'+str(i)].value
    print(price)
    dump_prices(price, hospital, cpt)
