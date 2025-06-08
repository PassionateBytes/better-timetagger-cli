=========
|project|
=========

Track your time with `TimeTagger <https://timetagger.app/>`_ from the command line.

TimeTagger is a (self-)hosted time tracking tool that helps you keep track of time spent on your tasks and projects.

This project provides a command-line interface (CLI) for the TimeTagger time tracking application, allowing you to manage your time entries directly from your terminal. It is a more feature-rich and ergonomic fork of the original `timetagger-cli <https://github.com/almarklein/timetagger_cli>`_ by `Almar Klein <https://github.com/almarklein>`_, adding a more user-friendly interface along with a number of new features, such as:

===================================== ===================== ================
Features                              better-timetagger-cli timetagger-cli
===================================== ===================== ================
Start / stop tasks                    .. centered:: ✅      .. centered:: ✅
Resume previous tasks                 .. centered:: ✅      .. centered:: ✅
Display status update                 .. centered:: ✅      .. centered:: ✅
List records by timeframe             .. centered:: ✅      .. centered:: ✅
Diagnose & fix database errors        .. centered:: ✅      .. centered:: ✅
Natural language support date/time    .. centered:: ✅      .. centered:: ✅
Easily tag records                    .. centered:: ✅      .. centered:: ❌
Filter tasks by tags                  .. centered:: ✅      .. centered:: ❌
Summary per tag                       .. centered:: ✅      .. centered:: ❌
Hide / restore records                .. centered:: ✅      .. centered:: ❌
Export records to CSV                 .. centered:: ✅      .. centered:: ❌
Import records from CSV               .. centered:: ✅      .. centered:: ❌
Preview records from CSV              .. centered:: ✅      .. centered:: ❌
Color-code output and render tables   .. centered:: ✅      .. centered:: ❌
Output rounded record times           .. centered:: ✅      .. centered:: ❌
Configurable date/time formats        .. centered:: ✅      .. centered:: ❌
Command aliases                       .. centered:: ✅      .. centered:: ❌
===================================== ===================== ================

Demo
====

.. asciinema:: source/demo.cast
   :autoplay: true
   :controls: true
   :cols: 81
   :rows: 25

.. toctree::
   :hidden:
   :maxdepth: 1

   source/quickstart
   source/install
   source/config
   source/cli
