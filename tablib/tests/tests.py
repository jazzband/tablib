import tablib

headers = ('first_name', 'last_name', 'gpa')

data = [
	('John', 'Adams', 4.0),
	('George', 'Washington', 2.6),
	('Henry', 'Ford', 2.3)
]

data = tablib.Dataset(*data, headers=headers)

data.append(['Kenneth' ,'Reitz', 4.3])

#print '***WITH HEADERS***'

#print 'First Names:\n',
#print data['first_name']

#print '\nYAML:'
#print data.yaml
#
#print 'JSON:'
#print data.json
#
#print '\nCSV:'
#print data.csv
#
#
#print '***AND WITHOUT HEADERS***'
#
#data.headers = None
#
#print '\nYAML:'
#print data.yaml
#
#print 'JSON:'
#print data.json
#
#print '\nCSV:'
#print data.csv

book = tablib.DataBook()
book.add_sheet(data)
book.add_sheet(data)

print book.json


