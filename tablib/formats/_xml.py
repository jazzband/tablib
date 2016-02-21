# -*- coding: utf-8 -*-

""" Tablib - XML Support
"""

from __future__ import unicode_literals

import sys
import tablib

from collections import *
from xml.dom.minidom import *
import xml.etree.ElementTree as ElementTree
import datetime

title = 'xml'
extensions = ('xml',)


def export_set(dataset):
    """Returns XML representation of Dataset."""
    return to_xml(dataset.dict)


def import_set(dset, in_stream):
    """Returns dataset from XML stream."""
    dset.wipe()
    dict = to_dict(in_stream)
    dict = harmonize(dict)
    dset.dict = dict


def detect(stream):
    """Returns True if given stream is valid XML."""
    try:
        parse(stream)
        return True
    except (xml.parsers.expat.ExpatError, TypeError):
        return False


def create_content(content, root, tag):
    if isinstance(content, Mapping):
        if tag is None:
            node = root
        else:
            node = root.ownerDocument.createElement(tag)
            root.appendChild(node)
        for key, value in content.items():
            create_content(value, node, key)
    else:
        if isinstance(content, Set) or isinstance(content, list):
            for item in content:
                create_content(item, root, tag)
        else:
            node = root.ownerDocument.createElement(tag)
            if isinstance(content, datetime.datetime):
                sub_node = root.ownerDocument.createTextNode(content.isoformat())
            else:
                sub_node = root.ownerDocument.createTextNode(str(content))
            node.appendChild(sub_node)
            root.appendChild(node)


def to_xml(content, root_tag='root', row_tag='row'):
    doc = Document()
    root_node = doc.createElement(root_tag)
    doc.appendChild(root_node)
    create_content(content, root_node, row_tag)
    return doc.toprettyxml()


def xml_tree_walk(root):
    dictionary = {}
    tag = root.tag
    if root.text:
        if root.text.strip() == '':
            dictionary[tag] = {}
        else:
            dictionary[tag] = root.text
    children = list(root)
    if children:
        subdictionary = {}
        for child in children:
            for k,v in xml_tree_walk(child).items():
                if k in subdictionary:
                    if isinstance(subdictionary[k], list):
                        subdictionary[k].append(v)
                    else:
                        subdictionary[k] = [subdictionary[k], v]
                else:
                    subdictionary[k] = v
        if dictionary.get(tag):
            dictionary[tag] = [dictionary[tag], subdictionary]
        else:
            dictionary[tag] = subdictionary
    if root.attrib:
        attribs = {}
        for k,v in root.attrib.items():
            attribs[k] = v
        if dictionary.get(tag):
            dictionary[tag] = [dictionary[tag], attribs]
        else:
            dictionary[tag] = attribs
    return dictionary


def get_keys(structure):
    key_list = [list(item) for item in structure]
    key_list = [item for sublist in key_list for item in sublist]
    return set(key_list)


def harmonize(structure):
    structure = structure[list(structure)[0]]
    structure = structure[list(structure)[0]]
    keys = get_keys(structure)
    structure = [add_keys(record, keys) for record in structure]
    return structure


def add_keys(dict, keys):
    diff = keys - set(list(dict))
    if diff:
        for key in diff:
            dict[key] = None
    return dict


def to_dict(xml_file):
    tree = ElementTree.parse(xml_file)
    root = tree.getroot()
    result = xml_tree_walk(root)
    return result
