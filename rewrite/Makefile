.PHONY: install_core install_java test

install:
	pip install -e rewrite-core/
	pip install -e rewrite-java/
	pip install -e rewrite-json/
	pip install -e rewrite-python/
	pip install -e rewrite-xml/
	pip install -e rewrite-yaml/

install_core:
	pip install -e rewrite-core/

install_json:
	pip install -e rewrite-json/

install_python:
	pip install -e rewrite-python/

install_xml:
	pip install -e rewrite-xml/

install_yaml:
	pip install -e rewrite-yaml/

test:
	pytest
