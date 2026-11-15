"""Keyed Dataset joins."""

from .exceptions import HeadersNeeded, InvalidDatasetType


def _headers(dataset):
    headers = dataset.headers
    if headers is None:
        raise HeadersNeeded()
    if any(not isinstance(name, str) or not name for name in headers):
        raise ValueError('Join headers must be nonempty strings')
    if len(set(headers)) != len(headers):
        raise ValueError('Join headers must be unique')
    return list(headers)


def _columns(selector, headers):
    if isinstance(selector, str):
        selector = [selector]
    if not isinstance(selector, (list, tuple)) or not selector:
        raise ValueError('Join keys must be a name or nonempty list or tuple of names')
    if any(not isinstance(name, str) or name not in headers for name in selector):
        raise ValueError('Join key does not name a column')
    if len(set(selector)) != len(selector):
        raise ValueError('Join key columns must be distinct')
    return [headers.index(name) for name in selector]


def _index(rows, columns, unique):
    keys = []
    index = {}
    for position, row in enumerate(rows):
        key = tuple(row[column] for column in columns)
        # Validate every cell, including null-containing keys and unmatched rows.
        hash(key)
        if any(cell is None for cell in key):
            keys.append(None)
            continue
        matches = index.setdefault(key, [])
        if unique and matches:
            raise ValueError('Join cardinality requires unique keys')
        matches.append(position)
        keys.append(key)
    return keys, index


def _pairs(left_keys, right_keys, left_index, right_index, how):
    if how == 'right':
        for right, key in enumerate(right_keys):
            matches = left_index.get(key, ()) if key is not None else ()
            if matches:
                for left in matches:
                    yield left, right
            else:
                yield None, right
        return

    matched_right = set()
    for left, key in enumerate(left_keys):
        matches = right_index.get(key, ()) if key is not None else ()
        if matches:
            for right in matches:
                matched_right.add(right)
                yield left, right
        elif how in ('left', 'outer'):
            yield left, None
    if how == 'outer':
        for right in range(len(right_keys)):
            if right not in matched_right:
                yield None, right


def _output_headers(left, right, suffixes):
    if (not isinstance(suffixes, (tuple, list)) or len(suffixes) != 2
            or any(not isinstance(suffix, str) for suffix in suffixes)):
        raise ValueError('Join suffixes must be two strings')
    overlap = set(left) & set(right)
    names = [name + suffixes[0] if name in overlap else name for name in left]
    names += [name + suffixes[1] if name in overlap else name for name in right]
    if any(not name for name in names) or len(set(names)) != len(names):
        raise ValueError('Join output headers are not unique nonempty names')
    return names


def join(left, right, on, left_on, right_on, how, suffixes, validate):
    from .core import Dataset

    if not isinstance(right, Dataset):
        raise InvalidDatasetType()
    left_headers, right_headers = _headers(left), _headers(right)
    if how not in ('inner', 'left', 'right', 'outer'):
        raise ValueError('Unknown join mode')
    if validate not in ('one_to_one', 'one_to_many', 'many_to_one', 'many_to_many'):
        raise ValueError('Unknown join cardinality')
    if on is not None:
        if left_on is not None or right_on is not None:
            raise ValueError('Use on or paired left_on and right_on')
        left_on = right_on = on
    left_columns = _columns(left_on, left_headers)
    right_columns = _columns(right_on, right_headers)
    if len(left_columns) != len(right_columns):
        raise ValueError('Join keys must have equal lengths')
    right_payload = [i for i in range(len(right_headers)) if i not in right_columns]
    headers = _output_headers(
        left_headers, [right_headers[i] for i in right_payload], suffixes)
    left_keys, left_index = _index(
        left._data, left_columns, validate in ('one_to_one', 'one_to_many'))
    right_keys, right_index = _index(
        right._data, right_columns, validate in ('one_to_one', 'many_to_one'))

    result = Dataset(headers=headers, title=left.title)
    for left_position, right_position in _pairs(
            left_keys, right_keys, left_index, right_index, how):
        left_row = left._data[left_position] if left_position is not None else None
        right_row = right._data[right_position] if right_position is not None else None
        values = list(left_row) if left_row is not None else [None] * len(left_headers)
        if right_row is not None:
            if left_row is None:
                for left_column, right_column in zip(left_columns, right_columns):
                    values[left_column] = right_row[right_column]
            values.extend(right_row[column] for column in right_payload)
        else:
            values.extend([None] * len(right_payload))
        tags = []
        for row in (left_row, right_row):
            if row is not None:
                for tag in row.tags:
                    if tag not in tags:
                        tags.append(tag)
        result.append(values, tags=tags)
    return result
