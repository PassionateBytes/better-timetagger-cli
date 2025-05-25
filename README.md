# (Better) TimeTagger CLI

Track your time with TimeTagger from the command line.

This is a more feature-rich and ergonomic fork of the original [timetagger-cli](https://github.com/almarklein/timetagger_cli) by [Almar Klein](https://github.com/almarklein), providing additional features and improved ergonomics.

### What's new?

This project does everything that the original timetracker-cli did, but it adds some great features and usibility improvements - batteries included!  
See how they compare:

|                               |                                         **better-timetagger-cli**                                          | timetagger-cli |
| ----------------------------- | :--------------------------------------------------------------------------------------------------------: | :------------: |
| Start Tasks                   |                                ✅ <br> *adjustable time* <br> *and more...*                                 |       ✅        |
| Stop Tasks                    |                                ✅ <br> *adjustable time* <br> *and more...*                                 |       ✅        |
| Resume Tasks                  |           ✅ <br> *adjustable time* <br> *simplified UX for record selection* <br> *and more...*            |       ✅        |
| Display Status                |                                    ✅ <br> *includes breakdown per tag*                                     |       ✅        |
| Show Records                  | ✅  <br> *filter by tags* <br> *optional summary or summary-only* <br> *live monitoring* <br> *and more...* |       ✅        |
| Diagnose & Fix Record Errors  |                                                     ✅                                                      |       ✅        |
| Export to CSV                 |                                                     ✅                                                      |       ❌        |
| Import from CSV               |                            ✅ <br> *includes dry-run mode to validate CSV files*                            |       ❌        |
| Colored Output                |                                                     ✅                                                      |       ❌        |
| Natural language support      |                      ✅ <br> *use phrases like '5 min ago', 'last Friday' or 'May 12'*                      |       ❌        |
| Configurable date/time format |                                                     ✅                                                      |       ❌        |
| Command aliases               |                     ✅ <br> `t in` and `t out`, are an alias for `t start` and `t stop`                     |       ❌        |
| Command shortcuts             |                              ✅ <br> Abbreviate commands like `t out` to `t o`                              |       ❌        |

## Installation

The TimeTagger CLI requires **Python 3.10** or higher. Install with your favorite Python package manager, e.g.:

```bash
pipx install better-time-tagger
```

You can now use the CLI as either `timetagger` or simply `t`.

```bash
t --version
#  (Better) TimeTagger CLI, version X.X.X
```

### Migrating from `timetagger_cli`

This project is a drop-in replacement for the original `timetagger-cli` package. You should first remove the original package from your system, then install `better-timetagger-cli`.

```bash
pipx uninstall timetagger-cli
pipx install better-timetagger-cli
```

Then run the `setup` command, to automatically migrate your existing timetagger configuration.

```bash
t setup
#  Migrating legacy configuration to new format...
#  TimeTagger config file: /path/to/config.toml
```

## Configuration

Before using the CLI for the first time, you must configure the URL of your TimeTagger server, along with your API key.
To update the configuration, simply run:

```bash
t setup
```

This will open the configuration file in your default editor. The first time you  run this command, a default configuration file will be created automatically.
Also, if an exsting configuration file from the original `timetagger-cli` pacage is found, it is migrated automatically.

## Contribute

To report bugs or request features, please file a github issue on this repository.

Pull-Requests are welcome too. Please always file a github issue first.