# This file is part of Django-Crypta.
# 
# Django-Crypta is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
# 
# Django-Crypta is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
# 
# You should have received a copy of the GNU Lesser General Public License along
# with Django-Crypta.  If not, see <http://www.gnu.org/licenses/>.

BLUE='\033[0;34m'
NC='\033[0m'

BIND?=0.0.0.0:8000
VENV_NAME=crypta
WORKON_HOME?=$(realpath $$WORKON_HOME)
ON_VENV=. $(WORKON_HOME)/$(VENV_NAME)/bin/activate

default: bootstrap db_start

clean:
	@echo -e $(BLUE)Removing venv...$(NC)
	-rm -rf $(WORKON_HOME)/$(VENV_NAME)
	@echo -e $(BLUE)Removing database...$(NC)
	-rm -rf ./db.sqlite3

bootstrap: clean
	@echo -e $(BLUE)Creating venv...$(NC)
	virtualenv -p python3 $(WORKON_HOME)/$(VENV_NAME)
	@echo -e $(BLUE)Installing requirements...$(NC)
	$(ON_VENV); pip install --upgrade pip
	$(ON_VENV); pip install -r requirements.txt

db_start:
	$(ON_VENV); ./manage.py makemigrations
	$(ON_VENV); ./manage.py migrate
	$(ON_VENV); ./manage.py createdemousers

run:
	$(ON_VENV); ./manage.py runserver $(BIND)
