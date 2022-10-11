# CDC Event Code

This repository is a continuous scrape of CDC event codes / value set from public health information network (PHIN)'s notifiable event disease condition.

## Resources

[PHIN ValueSet](https://phinvads.cdc.gov/vads/ViewValueSet.action?id=34ED25E7-F582-EC11-81AA-005056ABE2F0)

## Latest Version

You can find the list of updates [here](/data/README.md).

For a programmatic readable version of updates, go [here](/data/event_code_files.json).

## Setup

- Simple Setup

```python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Adding a new library

```python
pip freeze > requirements.txt
```
