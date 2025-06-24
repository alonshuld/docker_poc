# Docker POC

## Description

A proof of concept to docker

### dimg Format

```py
Const HEADER
DELIMITER
Creation Date
DELIMITER
Amount of instructions
DELIMITER
Amount of dependencies
DELIMITER
Instruction 1
DELIMITER
Instruction 2
DELIMITER
...
DELIMITER
Dependency 1 name
DELIMITER_DEPENDENCY
Dependency 1 content
DELIMITER
Dependency 2 name
DELIMITER_DEPENDENCY
Dependency 2 content
...
```

## Dependencies

* Pydantic

## Authors and acknowledgment

Hanich 10 & Hanich 2

## Project status

Not finished
