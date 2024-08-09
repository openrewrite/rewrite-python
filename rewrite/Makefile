.PHONY: all install-deps build

# List of project directories
PROJECTS= rewrite-core rewrite-java rewrite-json rewrite-python rewrite-xml rewrite-yaml

# Default target
all: install-deps build

# Define a target to install dependencies for all projects
install-deps:
	@for project in $(PROJECTS); do\
	  echo "Installing dependencies for $$project";\
	  cd $$project && poetry install;\
	  cd -;\
	done

# Define a target to build all projects
build:
	@for project in $(PROJECTS); do\
	  echo "Building project $$project";\
	  cd $$project && poetry build;\
	  cd -;\
	done

test:
	pytest
