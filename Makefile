publish:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_wheel upload
