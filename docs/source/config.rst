Configuration
=============

Configuration File
------------------

Before using the CLI for the first time, you must configure the **Base URL** of your TimeTagger instance, along with your **API Token**.
Additional configuration values are provided in the default configuration file, along with descriptive comments.

Open the configuration toml file with:

.. code-block:: bash

    $ t setup
    # TimeTagger config file: /path/to/timetagger_cli/config.toml

Migrate from original timetagger-cli
------------------------------------

If you previously used the original :code:`timetagger-cli` your old configuration will be migrated to the new format automatically.
The :code:`t setup` command recognizes the existing configuration and autmatically fetches its values when creating the new config file.
This does *not* modify or remove the legacy configuration file, so you can keep using it if you need to.

Reset Configuration
-------------------

To reset the default configuration file, simply delete or move your existing configuration file,
then run the setup command again.
