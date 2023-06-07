# RRDP Historian

## What

A quick and dirty RRDP downloader that keeps history of all deltas pointed by a given notification.xml file, and commits the downloaded deltas to a local git repository.

Each delta is downloaded every time the script is run, as the goal is to detect unwanted changes in the deltas.

## Usage

### Download a repository

```
poetry run ./rh.py download --rir <rir name> --baseurl --<url to notification.xml>
```

### Create the hash file

```
poetry run ./rh.py hash --rir <rir name> --session-id=<session-id>
```

If session-id is set to 0 it will default to the first session-id found inside the "rir" directory.

### Perform git commands inside the local repository

The git sub-command can be used to run most git commands inside the local repository without the need to cd to the directory.

For example, to view the differences between the current and last version of the hashes file it's possible to run:

```
poetry run ./rh.py git --rir lacnic --session-id=0 diff HEAD~ HEAD 3b0046c3-9077-4a70-b743-ca551aed4d53-hashes.txt
```

Substitute rir and session-id for the correct ones.

## Improvements

- parse TAL files so there is no need to use the notification.xml url
