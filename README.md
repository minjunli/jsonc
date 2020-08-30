# jsonc

`jsonc` ('c' for 'Config') extends the json syntax to make it serves better as a configuration langurage.

- C/JS-style comments support
  - single-line comment and inline comment started with `//` 
  - multi-line comment with `/* */`
- Expandable keyword support
  - Import data from other json / jsonc file by `"_include_json": "abslote_path_to_json"`

Jsonc package is built on python standard library, and provide the same functions call as python standard library. It can be imported by `import jsonc as json`, and keep the rest of the code that using json module unchanged.

## Examples

By default, duplicated key form sub jsonc files will be overwritten by the main jsonc file.

```jsonc
{
    // file /home/user/1.json
    "_include_json": "/home/user/2.json",
    "key1": 1,
    "dict1":
    {
        "_include_json": "/home/user/2.json",
        "key2": 2,
        "key4": 4,  // trailing comma is also allowed
    }
}

{
    // file /home/user/2.json
    // this key will be overwritten in 'dict1'
    "key2": 22,
    "key3": 23
}
```

```python
>>> import jsonc as json 
>>> print(json.dumps(json.load(open('1.json', 'r')), indent=4, sort_keys=True))
{
    "_include_json": "/home/minjunli/2.json",
    "dict1": {
        "_include_json": "/home/minjunli/2.json",
        "key2": 2,
        "key3": 23,
        "key4": 4
    },
    "key1": 1,
    "key2": 22,
    "key3": 23
}
```

## Tips

- VSCode users can set syntax highlight for jsonc files to built-in syntax 'Json with Comments'

## References

This repo is based on the following awesome projects:

- https://github.com/linjackson78/jstyleso
- https://github.com/reorx/json_include
