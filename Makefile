clean:
	rm -rf dist/
	rm -rf build/
build:
	python3 setup.py bdist_wheel
upload:
	python3 -m twine upload dist/*
deploy:
	make clean
	make build
	make upload