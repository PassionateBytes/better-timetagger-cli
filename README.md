# (Better) TimeTagger CLI

Track your time with [TimeTagger](https://timetagger.app/) from the command line.

TimeTagger is a (self-)hosted time tracking tool that helps you keep track of time spent on your tasks and projects.

This project provides a command-line interface (CLI) for the TimeTagger time tracking application, allowing you to manage your time entries directly from your terminal. It is a more feature-rich and ergonomic fork of the original `timetagger-cli <https://github.com/almarklein/timetagger_cli>`_ by `Almar Klein <https://github.com/almarklein>`_, adding a more user-friendly interface along with a number of new features, such as:

|                                     | **better-timetagger-cli** | timetagger-cli |
| ----------------------------------- | :-----------------------: | :------------: |
| Start / stop tasks                  |             ✅             |       ✅        |
| Resume previous tasks               |             ✅             |       ✅        |
| Display status update               |             ✅             |       ✅        |
| List records by timeframe           |             ✅             |       ✅        |
| Diagnose & fix database errors      |             ✅             |       ✅        |
| Natural language support date/time  |             ✅             |       ✅        |
| Easily tag records                  |             ✅             |       ❌        |
| Filter tasks by tags                |             ✅             |       ❌        |
| Summary per tag                     |             ✅             |       ❌        |
| Hide / restore records              |             ✅             |       ❌        |
| Export records to CSV               |             ✅             |       ❌        |
| Import records from CSV             |             ✅             |       ❌        |
| Preview records from CSV            |             ✅             |       ❌        |
| Color-code output and render tables |             ✅             |       ❌        |
| Output rounded record times         |             ✅             |       ❌        |
| Configurable date/time formats      |             ✅             |       ❌        |
| Command aliases                     |             ✅             |       ❌        |

## 🚀 Quickstart

### 1. Install the `better-timetagger-cli` package.

```bash
$ pipx install better-timetagger-cli
```

### 2. Update the configuration with your `base_url` and `api_token`.

```bash
$ t setup
```

### 3. Review CLI commands and options.

```bash
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
```

### 4. Manage your time with the command line interface.

```bash

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
```

## 📚 Documentation

For complete instructions, configuration details, and advanced features, visit the [full documentation on Read the Docs](https://better-timetagger-cli.readthedocs.io/).

## 🤝 Contributing

You are welcome to file **bug reports** and **feature requests** by opening a [github issue](https://github.com/PassionateBytes/better-timetagger-cli/issues) on this repository. If you’d like to contribute code, please consider starting with an issue to discuss the change before opening a pull request, to allow for a discussion of the intended change.

Pull requests (PRs) are appreciated and should reference a related bug report or feature request.
