# This file is part of Django-Crypta.
#
# Django-Crypta is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Django-Crypta is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with Django-Crypta.  If not, see <http://www.gnu.org/licenses/>.

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PYTEST?=
BIND?=0.0.0.0:8000
VENV_NAME=crypta-dev
WORKON_HOME?=$(realpath $$WORKON_HOME)
ON_VENV=. $(WORKON_HOME)/$(VENV_NAME)/bin/activate
ISORT="isort $$(find $(PWD)/allauth -not -path '*/migrations/*' -type f -name '*.py' -not -name '__init__.py' -print)"

deafault: bootstrap test

clean: clean-src clean-setup
	@echo -e $(RED)Removing venv...$(NC)
	-rm -rf $(WORKON_HOME)/$(VENV_NAME)

clean-src:
	@echo -e $(RED)Cleaning python compiled files and folders...$(NC)
	-find . -type d -name "__pycache__" | xargs -I% rm -rf %
	-find . -type f -name "*.pyc" | xargs -I% rm -rf %
	-rm -rf crypta/migrations/*

clean-setup:
	@echo -e $(RED)Cleaning setup.py files...$(NC)
	-./setup.py clean
	rm -rf ./django_crypta.egg-info ./build ./dist ./.tox ./.eggs

bootstrap: clean
	@echo -e $(BLUE)Creating venv...$(NC)
	virtualenv -p python3 $(WORKON_HOME)/$(VENV_NAME)
	@echo -e $(BLUE)Installing requirements...$(NC)
	$(ON_VENV); pip install --upgrade pip
	$(ON_VENV); pip install -r requirements/dev.txt
	$(ON_VENV); ./manage.py makemigrations crypta

shell:
	$(ON_VENV); ./manage.py shell_plus

test:
	@echo -e $(BLUE)Running test suite...$(NC)
	$(ON_VENV); pytest $(PYTEST)

watch-test:
	@echo -e $(BLUE)Running test suite on watch mode...$(NC)
	$(ON_VENV); ptw

lint:
	@echo -e $(BLUE)Linting project...$(NC)
	@-flake8 || true

build:
	@echo -e $(BLUE)Building...$(NC)
	@echo -e $(RED)TODO...$(NC)

isort:
	@echo -e $(BLUE)Sorting imports from project...$(NC)
	$(ISORT)

example:
	@echo -e $(BLUE)Building example...$(NC)
	cd example; make
	make run-example

run-example:
	@echo -e $(BLUE)Running example...$(NC)
	cd example; make run $(BIND)

shell-example:
	@echo -e $(BLUE)Running example...$(NC)
	. $(WORKON_HOME)/crypta-dev/bin/activate; ./example/manage.py shell_plus

.PHONY: deafault clean bootstrap test lint isort example
