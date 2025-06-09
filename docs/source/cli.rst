CLI Command Reference
=====================

.. note::
    The :code:`better-timetagger-cli` package installes two synonymous aliases: :code:`timetagger` and :code:`t`. |br|
    This documentation uses the longer alias :code:`timetagger` for clarity, but you can abbreviate it to :code:`t` in practice.

.. note::
    There are **command aliases** for most commands. |br|
    For example: :code:`t show` is synonymous with :code:`t display`, :code:`t list`, :code:`t ls`, and :code:`t d`. |br|
    Or :code:`t start` is synonymous with :code:`t in`, and :code:`t i` 

.. important::
    Review the help text for any command using the :code:`--help` of :code:`-h` flag.
    This will provide usage instructions along with a list of available options and arguments.

.. click:: better_timetagger_cli.cli:cli
    :prog: timetagger
    :nested: full
