[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fsedders123%2Fphial.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fsedders123%2Fphial?ref=badge_shield)

phial
=====

|Documentation Status| |CircleCI| |Coverage Status| |PyPi|

    A simple framework for building slack bots

Phial is a slack bot framework, modelled loosely on
`flask <https://github.com/pallets/flask/>`__.


Table of Contents
-----------------

-  `Usage <#usage>`__
-  `Install <#install>`__
-  `Contribute <#contribute>`__
-  `Licenses <#licenses>`__

Usage
-----

Python:
~~~~~~~

.. code:: python

    from phial import Phial, command, Response

    bot = Phial('---slack token here---')

    @bot.command('greet <name>')
    def greet(name):
        '''Simple command with argument which replies to a message'''
        return "Hello {0}".format(name)

    bot.run()

Slack:
~~~~~~

By default the bot requires a prefix of ``!`` before its commands. This
can be changed in the config.

::

    youruser:
    > !greet jim
    bot:
    > Hello Jim

Features:

-  Simple command definition
-  Send messages to slack
-  Reply to messages in a thread
-  Reply to messages with a reaction
-  Upload Files

Examples of commands utilising these features can be found in the
`examples <examples/>`__ folder

Install
-------

::

      $ pip install phial-slack

Contribute
----------

If a feature is missing, or you can improve the code please submit a PR
or raise an Issue

Licenses
--------

phial - MIT © 2017 James Seden Smith

Erlenmeyer Flask by Iconic from the Noun Project - `CC BY
3.0 <https://creativecommons.org/licenses/by/3.0/>`__ (used in
`examples/phial.png <examples/phial.png>`__)

.. |Documentation Status| image:: https://readthedocs.org/projects/phial/badge/?version=develop
   :target: http://phial.readthedocs.io/en/develop/
.. |CircleCI| image:: https://circleci.com/gh/sedders123/phial.svg?style=svg
   :target: https://circleci.com/gh/sedders123/phial
.. |Coverage Status| image:: https://coveralls.io/repos/github/sedders123/phial/badge.svg?branch=develop
   :target: https://coveralls.io/github/sedders123/phial?branch=develop
.. |PyPi| image:: https://badge.fury.io/py/phial-slack.svg
    :target: https://badge.fury.io/py/phial-slack


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fsedders123%2Fphial.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fsedders123%2Fphial?ref=badge_large)