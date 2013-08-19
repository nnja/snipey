Snipey
=====================
Snipey is an application that can be used to automatically RSVP to specific Meetup groups. It supports oauth authentication with Meetup.com, so any Meetup member can use it.


Current Functionality
-----------
You can add a subscription to any group you're currently a member of.

When you remove your subscription, any future snipes will be canceled.

Snipey supports both events that are open immediately, and events that have an RSVP open time in the future.

#### Add Subscriptions

![Add Subscriptions](https://raw.github.com/nnja/snipey/master/snipey/static/img/screenshot/add_sub.png)

#### View & Remove Subscriptions
![View & Remove Subscriptions](https://raw.github.com/nnja/snipey/master/snipey/static/img/screenshot/view_subs.png)


#### View pending, completed, and canceled snipes.
![View Snipes](https://raw.github.com/nnja/snipey/master/snipey/static/img/screenshot/view_snipes.png)


Limitations
-----
- Private groups are not supported.
- Meetups that require payment are not supported.

Requirements
------------
- Python 2.7	
	- Celery
	- sqlachemy
	- requests
	- Flask
		- Flask-SQLAlchemy
		- Flask-OAuth
		- Flask-Bootstrap
		- Flask-WTF
- RabbitMQ
- Postgres or sqlite

A full list of dependencies is listed in requirements.txt. Please see the installation section for more details.

Installation Instructions
-------------------------
1. Create a virtual environment, activate it.
2. `pip install -r requirements.txt`
3. install RabbitMQ
3. Create the environment variables specified in `config.py`
4. start rabbitmq `rabbitmq-server -detached`
5. start celery locally `celery worker --app=snipey.tasks -l debug`
6. start the web app and background worker `python web.py`

Support
-------
If you have any issues with this extension, open an issue on [GitHub](https://github.com/nnja/snipey/issues).

Contribution
------------
Any contribution is highly appreciated. The best way to contribute code is to open a [pull request on GitHub](https://help.github.com/articles/using-pull-requests).

Developer
---------
Nina Zakharenko  
[http://www.nnjas.net](http://www.nnjas.net)  
[@nnja](https://twitter.com/nnja)

License
-------
[OSL - Open Software Licence 3.0](http://opensource.org/licenses/osl-3.0.php)

Copyright
---------
(c) 2013 Nina Zakharenko
