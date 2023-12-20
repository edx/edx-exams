edx_exams
=============================

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge|

Service providing access to exam information

Overview
--------

The exam service is meant to surface any and all information related to Open edX exams. The service
is meant to function in parallel to the existing in-platform plugin, edx-proctoring.

Documentation
-------------

(TODO: `Set up documentation <https://2u-internal.atlassian.net/wiki/spaces/DOC/pages/10489531/Publish+Documentation+on+Read+the+Docs>`_)

Development Workflow
--------------------

Local Development Set Up
~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block::

  # Clone the repository
  git clone git@github.com:edx/edx-exams.git
  cd edx-exams

  # Set up a virtualenv using virtualenvwrapper with the same name as the repo and activate it
  mkvirtualenv -p python3.8 edx-exams

  # Install/update the dev requirements
  make requirements

  # Start LMS in devstack from your local devstack directory
  make dev.up.lms

  # Return to the edx-exams repo directory and provision credentials:
  bash local-provision-edx-exams.sh

  # Run edx-exams locally
  python manage.py runserver localhost:18740 --settings=edx_exams.settings.local

Devstack Set Up
~~~~~~~~~~~~~~~
.. code-block::

  # Clone the repository
  git clone git@github.com:edx/edx-exams.git
  cd edx-exams

  # Start LMS in devstack from your local devstack directory
  make dev.up.lms

  # Return to the edx-exams repo directory and provision the edx-exams containers
  bash provision-edx-exams.sh

You can use the make targets defined in the ``Makefile`` to interact with the running ``edx-exams`` Docker containers.

Development Workflow
~~~~~~~~~~~~~~~~~~~~
.. code-block::

  # Activate the virtualenv
  workon edx-exams

  # Grab the latest code
  git checkout main
  git pull

  # Install/update the dev requirements
  make requirements

  # Run the tests and quality checks (to verify the status before you make any changes)
  make validate

  # Make a new branch for your changes
  git checkout -b <your_github_username>/<short_description>

  # Using your favorite editor, edit the code to make your change.
  vim …

  # Run your new tests
  pytest ./path/to/new/tests

  # Run all the tests and quality checks
  make validate

  # Commit all your changes
  git commit …
  git push

  # Open a PR and ask for review.

Event Bus Set Up
~~~~~~~~~~~~~~~~

The ``edx-exams`` service uses the Open edX event bus to publish events relating to the exam attempt lifecycle and
others important exam events. These Open edX events are emitted by the service and pushed onto the event bus. Downstream
services, like the LMS, receive these events and implement downstream effects of these events. For more details,
please see `Implementation of Event Driven Architecture for Exam Downstream Effects`_.

These focus of these instructions is on how to set up the Open edX event bus for use with ``edx-exams``. For more
documentation about the event bus in general, please see `How to start using the Event Bus`_.

Currently, the event bus is only supported in environments running Docker containers, like `devstack`_. This is because
the interactions between services on the event bus is implemented in the devstack networking layer.

In order to run the event bus locally, follow these steps. These steps assume that you both have `devstack`_ running and
that you are running the ``edx-exams`` Docker container, as described in the Devstack Set Up section. These steps
describe how to install and run the Kafka-based event bus.

1. In a ``requirements/private.txt`` file, add the following Python package. These requirements are necessary for the
   Kafka-based event bus. They are not included as a part of the standard set of requirements because installation of
   confluent_kafka poses issues for users of Tutor on M1 Macs, which includes many users in the Open edX community. 
   For more details, please see `Optional Import of Confluent Kafka`_.


  .. code-block::

    confluent_kafka[avro,schema-registry]

2. Install the application requirements to install ``confluent_kafka``.

  .. code-block::

    # Shell into the application Docker container
    make app-shell

    # Install requirements
    make requirements

3. Follow the `manual testing`_ instructions to set up the Kafka-based Open edX event bus in the service that contains
   the event handler(s) for your event(s) - for example, the LMS or Studio.

Producing Events
################

Events will be produced at key stages of the exam attempt lifecycle and other points in the special exam feature. If you
are using the local Kafka cluster, you will be able to see the topics and events there.

Consuming Events
################

In order to consume events off the event bus, you must run a management command that starts an infinite loop to read
from the event bus.

Shell into the application Docker container and run the following management command to start the loop. See the
`consume_events management command documentation`_ for a description of the arguments.

.. code-block::

  python3 manage.py consume_events -t <topic-name> -g <group-id>

Here is an example of a command to consume events from the ``learning-exam-attempt-lifecycle`` topic in the LMS.

.. code-block::

    python3 manage.py lms consume_events -t learning-exam-attempt-lifecycle -g dev-lms

When your event is successfully consumed, you should see logs like the following.

.. code-block::

  2023-10-04 15:50:17,508 INFO 554 [edx_event_bus_kafka.internal.consumer] [user None] [ip None] consumer.py:513 - Message received from Kafka: topic=dev-learning-exam-attempt-lifecycle, partition=0, offset=7, message_id=b71c735c-62cd-11ee-9064-0242ac120012, key=b'\x00\x00\x00\x00\x010course-v1:edX+777+2023FW', event_timestamp_ms=1696434617498

  2023-10-04 15:50:17,593 INFO 554 [edx_event_bus_kafka.internal.consumer] [user None] [ip None] consumer.py:393 - Message from Kafka processed successfully


.. _Implementation of Event Driven Architecture for Exam Downstream Effects: https://github.com/edx/edx-exams/blob/main/docs/decisions/0004-downstream-effect-events.rst
.. _How to start using the Event Bus: https://openedx.atlassian.net/wiki/spaces/AC/pages/3508699151/How+to+start+using+the+Event+Bus
.. _devstack: https://edx.readthedocs.io/projects/open-edx-devstack/en/latest/
.. _Optional Import of Confluent Kafka: https://github.com/openedx/event-bus-kafka/blob/main/docs/decisions/0005-optional-import-of-confluent-kafka.rst.
.. _manual testing: https://github.com/openedx/event-bus-kafka/blob/main/docs/how_tos/manual_testing.rst
.. _consume_events management command documentation: https://github.com/openedx/openedx-events/blob/7e6e92429485133bf16ae4494da71b5a2ac31b9e/openedx_events/management/commands/consume_events.py

Setting up an exam and proctoring tool
--------------------------------------

Instructions can be found in `this document <https://2u-internal.atlassian.net/wiki/spaces/PT/pages/256737327/Local+Development+LTI+Configuration>`_

This is a living document while this repo is in development and will be converterd to a public format on release.

License
-------

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

How To Contribute
-----------------

Contributions are very welcome.
Please read `How To Contribute <https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst>`_ for details.
Even though they were written with ``edx-platform`` in mind, the guidelines
should be followed for all Open edX projects.

The pull request description template should be automatically applied if you are creating a pull request from GitHub. Otherwise you
can find it at `PULL_REQUEST_TEMPLATE.md <.github/PULL_REQUEST_TEMPLATE.md>`_.

The issue report template should be automatically applied if you are creating an issue on GitHub as well. Otherwise you
can find it at `ISSUE_TEMPLATE.md <.github/ISSUE_TEMPLATE.md>`_.

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org.

Getting Help
------------

If you're having trouble, we have discussion forums at https://discuss.openedx.org where you can connect with others in the community.

Our real-time conversations are on Slack. You can request a `Slack invitation`_, then join our `community Slack workspace`_.

For more information about these options, see the `Getting Help`_ page.

.. _Slack invitation: https://openedx-slack-invite.herokuapp.com/
.. _community Slack workspace: https://openedx.slack.com/
.. _Getting Help: https://openedx.org/getting-help

.. |pypi-badge| image:: https://img.shields.io/pypi/v/edx-exams.svg
    :target: https://pypi.python.org/pypi/edx-exams/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/edx/edx-exams/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/edx/edx-exams/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/edx/edx-exams/coverage.svg?branch=main
    :target: https://codecov.io/github/edx/edx-exams?branch=main
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/edx-exams/badge/?version=latest
    :target: https://edx-exams.readthedocs.io/en/latest/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/edx-exams.svg
    :target: https://pypi.python.org/pypi/edx-exams/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/edx/edx-exams.svg
    :target: https://github.com/edx/edx-exams/blob/main/LICENSE.txt
    :alt: License
