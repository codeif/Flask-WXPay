# -*- coding: utf-8 -*-
import random
import string
import hashlib
import xml.etree.ElementTree as ElementTree

from .compat import str, numeric_types, bytes


def xml_to_data(xml):
    if isinstance(xml, str):
        xml = xml.encode('utf-8')
    data = {}
    root = ElementTree.fromstring(xml)
    for child in root:
        value = child.text
        if value:
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            data[child.tag] = value
    return data


def data_to_xml(data):
    xml = ['<xml>']
    for k, v in data.items():
        if isinstance(v, (int, numeric_types)) or v.isdigit():
            xml.append('<{0}>{1}</{0}>'.format(k, v))
        else:
            xml.append('<{0}><![CDATA[{1}]]></{0}>'.format(k, v))
    xml.append('</xml>')
    return ''.join(xml)


def gen_random_str(size=16):
    """生成随机字符串"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def md5(origin):
    """返回小写的32位16进制的md5值"""
    if isinstance(origin, str):
        origin = origin.encode('utf-8')
    return hashlib.md5(origin).hexdigest()
