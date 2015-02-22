PYTHON=python

%.html: %.md _layouts/webpage.html
	kramdown --template _layouts/webpage.html $< > $@

all: docs

docs: README.html

check:
	PYTHON=${PYTHON} ./run_tests.sh
