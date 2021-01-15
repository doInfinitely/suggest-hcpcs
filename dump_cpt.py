from doltpy.core import Dolt
import mysql.connector
import csv

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
    query = "INSERT INTO cpt_hcpcs ({0}) VALUES ({1})".format(keys, formats)
    cursor.execute(query, values)

with open('cpt_codes_70.tsv') as csvfile:
    spamreader = csv.reader(csvfile, delimiter='\t')
    for row in spamreader:
        print(', '.join(row))
        output = {"code":row[1].strip(), "long_description":row[0].strip()}
        dump_code(output)
