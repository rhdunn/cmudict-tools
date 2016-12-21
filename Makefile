PYTHON=python
VIMDIR=/usr/share/vim/addons
VIMPLUGINDIR=/usr/share/vim/registry

.PHONY: vim

%.html: %.md _layouts/webpage.html
	kramdown --template _layouts/webpage.html $< > $@

%.rst: %.md
	pandoc --from=markdown --to=rst --output=$@ $<

all: docs build

docs: README.html

build: README.rst
	${PYTHON} setup.py build

install: vim_plugin README.rst
	${PYTHON} setup.py install

uninstall: README.rst
	${PYTHON} setup.py uninstall

clean:
	${PYTHON} setup.py clean

distclean: clean
	rm README.rst

check:
	PYTHON=${PYTHON} ./run_tests.sh

vim:
	mkdir -pv ${VIMDIR}/syntax
	cp -v vim/syntax/*.vim ${VIMDIR}/syntax
	mkdir -pv ${VIMDIR}/ftdetect
	cp -v vim/ftdetect/*.vim ${VIMDIR}/ftdetect

vim_plugin: vim
	mkdir -pv ${VIMPLUGINDIR}
	cp -v vim/registry/*.yaml ${VIMPLUGINDIR}
