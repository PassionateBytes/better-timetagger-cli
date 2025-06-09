Quickstart
==========

**1.** Install the :code:`better-timetagger-cli` package.

.. code-block:: bash

    $ pipx install better-timetagger-cli

**2.** Update the configuration with your :code:`base_url` and :code:`api_token`.

.. code-block:: bash

    $ t setup
    # TimeTagger config file: /path/to/timetagger_cli/config.toml

**3.** Review CLI commands and options.

.. code-block:: bash

    $ t --help
    # Usage: t [OPTIONS] COMMAND [ARGS]...
    #
    # Options:
    #   ...
    #
    # Commands:
    #   ...

    $ t start --help
    # Usage: t start [OPTIONS] [TAGS]...
    #
    # Options:
    #   ...


**4.** Manage your time with the command line interface.

.. code-block:: bash

    $ t start client-a
    #         Started             Stopped             Duration   Description
    # ──────────────────────────────────────────────────────────────────────
    #   Tue   27-May-2025 08:15   ...                       0m   #client-a

    $ t stop -a "in 15 minutes"
    #         Started             Stopped             Duration   Description
    # ──────────────────────────────────────────────────────────────────────
    #   Tue   27-May-2025 08:15   27-May-2025 08:30        15m   #client-a

    $ t show -s yesterday
    #         Started             Stopped             Duration   Description
    # ──────────────────────────────────────────────────────────────────────
    #   Tue   27-May-2025 08:15   27-May-2025 08:30        15m   #client-a
    #   Mon   26-May-2025 13:20   26-May-2025 17:57     4h 37m   #client-b
    #   Mon   26-May-2025 09:34   26-May-2025 12:40     3h  6m   #client-b

    $ t export -s "monday 8am" -e "friday 6pm" -o records.csv
    # Exported 3 records to 'records.csv'.
