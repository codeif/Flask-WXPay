# -*- coding: utf-8 -*-
import hashlib
import random
import string
import xml.etree.ElementTree as ElementTree
from datetime import datetime

from .compat import bytes, numeric_types, str


def xml_to_dict(xml):
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


def dict_to_xml(*args, **kwargs):
    """参数形式参照flask.jsonify"""
    data = dict(*args, **kwargs)
    xml = ['<xml>']
    for k, v in data.items():
        if isinstance(v, numeric_types):
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


def now_str(format='%Y%m%d%H%M%S%f'):
    """当前时间的字符串形式, 例如：20170310165231887517"""
    return datetime.now().strftime(format)
