# Docker POC

## Description

A proof of concept to docker

### dimg Format

```JSON``` file that has been compressed with ```gzip```

```json
{
    "name": "test_image",
    "creation_date": "2025-06-28 19:12:37",
    "dockerfile": "CMD echo hello world\nCMD echo goodbye world",
    "dependencies": [
        {
            "name": "dependency1",
            "data": "data1"
        },
        {
            "name": "dependency2",
            "data": "data2"
        },
    ]
}
```

## Dependencies

* Pydantic

## Authors and acknowledgment

Alon Shuldiner

## Project status

Not finished
