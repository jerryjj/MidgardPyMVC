Midgard Python MVC
==================

Installation and development setup
==================================

First create virtualenv for Python somewhere ie. in your home -dir. This script installs virtualenv with Pylons:

	curl http://pylonshq.com/download/0.9.7/go-pylons.py | python - midgard_pylons

Activate the virtual environment:

	source midgard_pylons/bin/activate
	
Next go back to ``midgardmvc`` folder and run the following to download all dependencies

	python setup.py develop

Symlink MVC schemas to Midgard schema folder

	(sudo) ln -s /PATH_TO_MIDGARDMVC/config/midgardmvc_core.xml /usr/share/midgard2/schema/midgardmvc_core.xml

Next configure your Midgard configuration in midgard.local.ini (Defaults can be found in midgard.ini)

Then setup simple Midgard site with default Midgard objects

	paster setup-app development.ini

Production
==========

Make a config file as follows:

    paster make-config midgardmvc production.ini

Tweak the config file as appropriate and then setup the application:

    paster setup-app production.ini

Running with paster
===================

Using the --reload switch allows you to develop without restarting the server after code changes

	paster serve --reload development.ini
