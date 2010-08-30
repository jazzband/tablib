import tablib

headers = ('first_name', 'last_name', 'gpa')

data = [
	('John', 'Adams', 4.0),
	('George', 'Washington', 2.6),
	('Henry', 'Ford', 2.3)
]

data = tablib.Dataset(*data, headers=headers)

#print data[1]
data.append(['kenneth' ,'reitz', 4.3])


#print data.digest()

#print data.yaml
#print data.json

data.headers = None
#print data.csv
print data.xls
#print data.yaml
#print data.json