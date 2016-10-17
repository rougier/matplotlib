# -----------------------------------------------------------------------------
# Proof of concept for markup text in matplotlib
# Nicolas P. Rougier https://github.com/rougier
# -----------------------------------------------------------------------------
import re
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib import transforms


def process(markup, tag, name, value):
    """
    This function update given markup from tag, name & value
    """
    if tag == 'i':
        markup["style"] = "italic"
    elif tag == 'b':
        markup["weight"] = "bold"
    elif tag == 'span':
        if name in ["foreground", "fgcolor", "color"]:
            markup["foreground"] = value
        elif name in ["background", "bgcolor"]:
            markup["background"] = value
        elif name in ["font_family", "family", "face"]:
            markup["family"] = value
        elif name in ["font_stretch", "stretch"]:
            markup["stretch"] = value
        elif name in ["font_variant", "variant"]:
            markup["variant"] = value
        elif name in ["font_style", "style"]:
            markup["style"] = value
        elif name in ["font_size", "size"]:
            markup["size"] = value
        elif name in ["font_weight", "weight"]:
            markup["weight"] = value
    return markup


def markup_text(x, y, text, ax=None, **kwargs):
    """
    """

    # Create default markup based on kwargs
    default = {"foreground": "black",
               "background": None,
               "alpha": 1.0,
               "size": "medium",
               "stretch": "normal",
               "variant": "normal",
               "style": "normal",
               "family": "sans",
               "weight": "medium"}

    # Update default markup
    keys = []
    for key in kwargs.keys():
        if key in default.keys():
            default[key] = kwargs[key]
            keys.append(key)

    # Remove updated values from kwargs
    kwargs = {key: value for key, value in kwargs.items() if key not in keys}

    # Regular expression for tagged or raw text
    re_markup = (
        '''<(?P<tag>[^\s]*)(?P<attributes>[^<]*)>(?P<text1>[^<]*)</(?P=tag)>|'''
        '''(?P<text2>[^<]*)''')
    # Regular epxression for attribute of the form name=value
    re_attribute = (
        '''(?P<name>[^\s]*)\s*=\s*'''
        '''((?P<value1>[^\s]*)|\"(?P<value2>[^\"]*)\")''')

    # Parse text as a list of (subtext, markup) tuples
    items = []
    for match in re.finditer(re_markup, text):
        tag = match.group("tag")
        attributes = match.group("attributes")
        string = match.group("text1") or match.group("text2")
        markup = dict(default)
        if attributes is not None and len(attributes.strip()):
            for attribute in re.finditer(re_attribute, attributes):
                name = attribute.group("name")
                value = attribute.group("value1") or attribute.group("value2")
                markup = process(markup, tag, name, value)
        elif tag is not None:
            markup = process(markup, tag, None, None)
        if len(string):
            items.append((string, markup))

    if ax is None:
        ax = plt.gca()
    t = ax.transData
    canvas = ax.figure.canvas

    for (string, markup) in items:
        text = ax.text(x, y, string, transform=t,
                       color=markup["foreground"],
                       weight=markup["weight"],
                       alpha=markup["alpha"],
                       style=markup["style"],
                       family=markup["family"],
                       variant=markup["variant"],
                       stretch=markup["stretch"],
                       size=markup["size"],
                       **kwargs)
        text.draw(canvas.get_renderer())
        ex = text.get_window_extent()
        t = transforms.offset_copy(text._transform, x=ex.width, units='dots')

markup_text(0.10, 0.50, 
            """<b>Bold</b> <i>italic</i>"""
            """<span color=blue>Blue</span>"""
            """<span color=red>Red</span>"""
            """<span color=green>Green</span>"""
            """<span size=xx-small>xx-small</span>"""
            """<span size=x-small>x-small</span>"""
            """<span size=x-large>x-large</span>"""
            """<span size=xx-large>xx-large</span>""")
plt.show()
