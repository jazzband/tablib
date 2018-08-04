test:
	python test_tablib.py
publish:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_wheel --universal upload
