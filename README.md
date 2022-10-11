# CDC Event Code

This repository is a continuous scrape of CDC event codes from public health information network (PHIN)'s notifiable event disease condition.

## Resources

[PHIN ValueSet](https://phinvads.cdc.gov/vads/ViewValueSet.action?id=34ED25E7-F582-EC11-81AA-005056ABE2F0)

## Latest Version

The latest version is Version 35 and can be found [here](/data/raw/ValueSets%5CPHVS_NotifiableEvent_Disease_Condition_CDC_NNDSS_V35.txt).

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
