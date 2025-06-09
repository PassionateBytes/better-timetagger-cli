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

Configuration Options
---------------------

* :code:`base_url`\*: The base URL of your TimeTagger instance. 
  If your using the commercial timetagger instance, set this to `https://timetagger.io/timetagger/`.
  In case you are self-hosting TimeTagger, set this to the URL of your instance, like `https://your-instance.com/timetagger/`.
* :code:`api_token`\*: Your API token for authenticating with the TimeTagger instance.
  Generate your API token on the TimeTagger web interface, on the `Account` page.
* :code:`ssl_verify`: Set to `true` to verify SSL certificates, or `false` to disable SSL verification, or specify a custom SSL certificate file.
  Disabling SSL verification is not recommended for production use, but may be useful for local testing or self-signed certificates.
  In case you are using a self-signed certificate, specify the path to your certificate file here.
* :code:`datetime_format`: Your preferred date and time format for displaying timestamps in the CLI.
  Use Python's `strftime format codes <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_ along with `rich style annotations <https://rich.readthedocs.io/en/stable/style.html>`_ to customize the output.
* :code:`weekday_format`: Your preferred format for displaying weekdays in the CLI.
  Use Python's `strftime format codes <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_ along with `rich style annotations <https://rich.readthedocs.io/en/stable/style.html>`_ to customize the output.
* :code:`running_records_search_window`: The default time window in weeks used to identify `running` records in the database.
  This parameter helps optimize the performance of the CLI when searching for running records.
  Set to `-1` to search all records, which is the most accurate method, but may result in slower performance (especially with large databases).
  Otherwise, set to the number of recent weeks to search for running records, which can improve performance for shorter tasks.

*\* Mandatory configuration options.*

Reset Configuration
-------------------

To reset the default configuration file, simply delete or move your existing configuration file,
then run the setup command again.
