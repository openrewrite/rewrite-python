.PHONY: all install-deps build

# Default target
all: install-deps build

# Define a target to install dependencies for all projects
install-deps:
	echo "Installing dependencies";\
	poetry install;\

# Define a target to build all projects
build:
	echo "Building project";\
	poetry build;\

test:
	pytest
