# (Better) TimeTagger CLI

Track your time with TimeTagger from the command line.

This is a more feature-rich and ergonomic fork of the original [timetagger-cli](https://github.com/almarklein/timetagger_cli) by [Almar Klein](https://github.com/almarklein).

### What's new?

This project does everything that the original timetracker-cli did, but it adds some great features and usibility improvements.  
See how they compare:

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

## Installation

The TimeTagger CLI requires **Python 3.10** or higher. Install with your favorite Python package manager, e.g.:

```bash
pipx install better-timetagger-cli
```

You can now use the CLI as either `timetagger` or simply `t`.

```bash
t --version
#  (Better) TimeTagger CLI, version X.X.X
```

## Configuration

Before using the CLI for the first time, you must configure the URL of your TimeTagger server, along with your API key.
To update the configuration, simply run:

```bash
t setup
```

### Migrating from `timetagger-cli`

If you previously had the original `timetagger-cli` package installed, your old configuration will be migrated to the new format automatically.
The `t setup` command recognizes the existing configuration autmatically and fetches its configuration values when creating the new configuration file.
This does not modify or remove the legacy configuration file, so you can keep using it if you need to.

```bash
t setup
#  Migrating legacy configuration to new format...
#  TimeTagger config file: /path/to/config.toml
```


This will open the configuration file in your default editor. The first time you  run this command, a default configuration file will be created automatically.
Also, if an exsting configuration file from the original `timetagger-cli` pacage is found, it is migrated automatically.

## Contribute

To report bugs or request features, please file a github issue on this repository.

Pull-Requests are welcome too. Please always file a github issue first.