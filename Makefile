PYTHON ?= python
PREFIX ?= /usr/local
VIMDIR ?= $(PREFIX)/share/vim/addons
VIMPLUGINDIR ?= $(PREFIX)/share/vim/registry
PYTHON_VERSION = $(shell $(PYTHON) -c 'import sys; print("%s.%s" % sys.version_info[0:2])')
PYTHONPATH ?= $(PREFIX)/lib/python$(PYTHON_VERSION)/site-packages/

.PHONY: vim

%.html: %.md _layouts/webpage.html
	kramdown --template _layouts/webpage.html $< > $@

%.rst: %.md
	pandoc --from=markdown --to=rst --output=$@ $<

all: docs build

docs: README.html

build: README.rst
	PYTHONPATH="$(PYTHONPATH)" "${PYTHON}" setup.py build

install: vim_plugin README.rst
	mkdir -p $(PYTHONPATH)
	PYTHONPATH="$(PYTHONPATH)" "${PYTHON}" setup.py install --prefix=$(PREFIX)

uninstall: README.rst
	PYTHONPATH="$(PYTHONPATH)" "${PYTHON}" setup.py uninstall --prefix=$(PREFIX)

clean:
	PYTHONPATH="$(PYTHONPATH)" "${PYTHON}" setup.py clean

distclean: clean
	rm README.rst

check:
	PYTHONPATH="$(PYTHONPATH)" PYTHON="${PYTHON}" ./run_tests.sh

vim:
	mkdir -pv "$(VIMDIR)/syntax"
	cp -v vim/syntax/*.vim "$(VIMDIR)/syntax"
	mkdir -pv "$(VIMDIR)/ftdetect"
	cp -v vim/ftdetect/*.vim "$(VIMDIR)/ftdetect"

vim_plugin: vim
	mkdir -pv "$(VIMPLUGINDIR)"
	cp -v vim/registry/*.yaml "$(VIMPLUGINDIR)"

