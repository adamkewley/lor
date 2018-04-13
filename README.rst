Luigi on Rails
==============

|Build Status|

ALPHA BUILD: A framework for rapidly developing pipelines with Luigi

[`documentation <https://adamkewley.github.io/lor/>`_]

Features:

- Convention-over-configuration approach to Luigi projects
- Standard workspace creation (``lor new``)
- Configuration loading
- A workspace-centric command-line (``new``, ``explain``, ``ls``, ``run``, etc.)
- Utility tasks (e.g. ``EnsureExistsOnLocalFilesystemTask``)
- Other utilities for managing long-running subprocesses, building a CLI, etc.


Installation
------------

To install use pip:

    $ pip install lor


Or clone the repo:

    $ git clone https://github.com/adamkewley/lor.git

    $ python setup.py install


Usage
-----

Once installed, ``lor`` can be used from the command-line:

    $ lor new foo

This creates a ``lor`` workspace at ``foo/``. A ``lor`` workspace is a standard python3 pip project which depends on
``lor`` as a dependency (this can be removed if you don't need it). The ``lor`` command-line command can detect if the
terminal is in a ``lor`` workspace and provides convenience commands for working in a standard workspace.

Tasks written for ``lor`` are just standard Luigi tasks. The ``lor`` library provides various utility methods that a
typical project *might* find useful (all opt-in). For example, ``lor`` provides a ``props`` module that you can use to
load configuration properties at runtime:

.. code:: python

    # foo/tasks/bar

    import lor.props
    import luigi


    class BarTask(luigi.Task):
        output_path = luigi.Parameter()

        def run(self):
            with open(str(self.output_path), "w") as f:
                config_prop = lor.props.get("CONFIG_PROP")
                f.write(config_prop)

        def output(self):
            return luigi.LocalTarget(self.output_path)

The above is a standard Luigi task that uses ``lor`` to load a configuration property called ``CONFIG_PROP`` from the
workspace (held at ``etc/properties.yml`` in the workspace). The task is a standard Luigi task, so it can be ran from
Luigi directly:

    $ luigi --module foo.tasks.bar BarTask --output-path some/path

The ``lor run`` command can also be used to run the task:

   $ lor run --module foo.tasks.bar BarTask --output-path some/path

The ``lor run`` command runs ``luigi`` by proxy, so it effectively has the same interface. However, ``lor run`` also
adds useful functionality, such as the ability to override a variable's value at runtime:

   $ lor run --properties CONFIG_PROP=overridden --module foo.tasks.bar BarTask --output-path some/path

The task will then write "overridden" to the output file instead of whatever was loaded from the workspace's configuration
file. This is because ``lor run`` bootstraps the workspace global with the override before running Luigi.

TODO: This documentation is work in progress


.. |Build Status| image:: https://travis-ci.org/adamkewley/lor.svg?branch=master
   :target: https://travis-ci.org/adamkewley/lor
