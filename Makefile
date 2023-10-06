install:
	pipenv sync

dist:
	pipenv run python -m build . --wheel

upload:
	pipenv run twine upload dist/*

clean:
	rm -rf dist build pyETA.egg-info
