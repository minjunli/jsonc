"""
Json for config file. Added supports for comments and expandable keywords.
"""

import json
import copy

RECURRENT_OBJECT_TYPES = (dict, list)

# Identifier key to import another json file,
# work as prefix, allowing "INCLUDE_KEY_1", "INCLUDE_KEY_2"...
INCLUDE_KEY = '_include_json'

def _read_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

# There may be performance suffer backtracking the last comma
def _remove_last_comma(str_list, before_index):
    i = before_index - 1
    while str_list[i].isspace() or not str_list[i]:
        i -= 1

    # This is the first none space char before before_index
    if str_list[i] == ',':
        str_list[i] = ''

def _dispose_comments(json_str: str):
    """Clear C/JS-style comments like // and /**/ in json_str.

    Args:
        json_str (str): json string to clean up comment

    Returns:
        str: json_str without comments
    """
    result_str = list(json_str)
    escaped = False
    normal = True
    sl_comment = False
    ml_comment = False
    quoted = False

    a_step_from_comment = False
    a_step_from_comment_away = False

    former_index = None

    for index, char in enumerate(json_str):

        if escaped:  # We have just met a '\'
            escaped = False
            continue

        if a_step_from_comment:  # We have just met a '/'
            if char != '/' and char != '*':
                a_step_from_comment = False
                normal = True
                continue

        if a_step_from_comment_away:  # We have just met a '*'
            if char != '/':
                a_step_from_comment_away = False

        if char == '"':
            if normal and not escaped:
                # We are now in a string
                quoted = True
                normal = False
            elif quoted and not escaped:
                # We are now out of a string
                quoted = False
                normal = True

        elif char == '\\':
            # '\' should not take effect in comment
            if normal or quoted:
                escaped = True

        elif char == '/':
            if a_step_from_comment:
                # Now we are in single line comment
                a_step_from_comment = False
                sl_comment = True
                normal = False
                former_index = index - 1
            elif a_step_from_comment_away:
                # Now we are out of comment
                a_step_from_comment_away = False
                normal = True
                ml_comment = False
                for i in range(former_index, index + 1):
                    result_str[i] = ""

            elif normal:
                # Now we are just one step away from comment
                a_step_from_comment = True
                normal = False

        elif char == '*':
            if a_step_from_comment:
                # We are now in multi-line comment
                a_step_from_comment = False
                ml_comment = True
                normal = False
                former_index = index - 1
            elif ml_comment:
                a_step_from_comment_away = True
        elif char == '\n':
            if sl_comment:
                sl_comment = False
                normal = True
                for i in range(former_index, index + 1):
                    result_str[i] = ""
        elif char == ']' or char == '}':
            if normal:
                _remove_last_comma(result_str, index)

    #  To remove single line comment which is the last line of json
    if sl_comment:
        sl_comment = False
        normal = True
        for i in range(former_index, len(json_str)):
            result_str[i] = ""

    # Show respect to original input if we are in python2
    return ("" if isinstance(json_str, str) else u"").join(result_str)

def _json_walker(json_obj, **kwargs):
    """Expand sub jsonc files in jsonc object

    Args:
        json_obj (dict or list): json object loaded from files
    """
    # cache to update after walking finished
    to_update = []
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            # support multiple include suffix, e.g. "include_key1", "include_key2"...
            if k.startswith(INCLUDE_KEY):
                to_update.append(
                    _json_include(
                        _read_file(v),
                        inside_include=True,
                        **kwargs
                    )
                )
            elif isinstance(v, RECURRENT_OBJECT_TYPES):
                _json_walker(v, **kwargs)
    elif isinstance(json_obj, list):
        for i in json_obj:
            if isinstance(i, RECURRENT_OBJECT_TYPES):
                _json_walker(i, **kwargs)
    for i in to_update:
        json_obj.update(i)

def _update_walker(d: dict, u: dict):
    """Similar to dict update in python, but apply recursively

    Args:
        d (dict): dict to be updated
        u (dict): dict that apply to d

    Returns:
        dict: updated dict d
    """
    if isinstance(u, dict):
        assert isinstance(d, dict), 'Two dicts in _update should be the same type'
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = _update_walker(d.get(k, {}), v)
            elif isinstance(v, list):
                d[k] = _update_walker(d.get(k, []), v)
            else:
                d[k] = v
    if isinstance(u, list):
        assert isinstance(d, list), 'Two objects in _update should be the same type'
        for i, j in zip(d, u):
            _update_walker(i, j)
    return d

def _json_include(text: str, inside_include=False, keep_top_values=True, **kwargs):
    """Build jsonc object from text

    Args:
        text (str): loaded text from jsonc file
        inside_include (bool, optional): means this function is not top level _json_include call. Defaults to False.
        keep_top_values (bool, optional): duplicated sub json key will be overwritten. Defaults to True.

    Returns:
        dict: loaded jsonc dict
    """
    d = json.loads(_dispose_comments(text), **kwargs)
    d_orignal = {}

    if keep_top_values:
        # cache the original file to prevent included file modifing original values
        d_orignal = copy.deepcopy(d)
    
    if inside_include:
        assert isinstance(d, dict),\
            'The JSON file being included should always be a dict rather than a list'
    
    # update missing values from included files
    _json_walker(d)
    
    if keep_top_values:
        # recover the original values from top files
        _update_walker(d, d_orignal)
    
    return d

def _remove_include_key(json_obj):
    """Remove the INCLUDE_KEY in the loaded json object

    Args:
        json_obj (dict or list): jsonc object to be modified
    """
    to_del = []
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            if k.startswith(INCLUDE_KEY):
                to_del.append(k)
            elif isinstance(v, RECURRENT_OBJECT_TYPES):
                _remove_include_key(v)
    elif isinstance(json_obj, list):
        for i in json_obj:
            if isinstance(i, RECURRENT_OBJECT_TYPES):
                _remove_include_key(i)
    for i in to_del:
        del json_obj[i]

# Below are just some wrapper function around the standard json module,
# note that not all original kwargs are tested.
def loads(text, remove_include_key=False, **kwargs):
    d = _json_include(text, keep_top_values=True, **kwargs)
    if remove_include_key:
        _remove_include_key(d)
    return d

def load(fp, remove_include_key=False, **kwargs):
    return loads(fp.read(), remove_include_key=remove_include_key, **kwargs)

def dumps(obj, **kwargs):
    return json.dumps(obj, **kwargs)

def dump(obj, fp, **kwargs):
    json.dump(obj, fp, **kwargs)
