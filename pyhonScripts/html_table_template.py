from typing import Union

from lxml import html
from lxml.etree import SubElement


table_markup: str = '<table class="table table-bordered table-responsive-md">' \
    '  <thead class="thead-light">' \
    '    <tr><th scope="col">Date</th>' \
    '    <th scope="col">New HTML files</th>' \
    '    <th scope="col">Original HTML files</th></tr>' \
    '  </thead>' \
    '  <tbody></tbody>' \
    '</table>'


def new_table() -> html.Element:
    return html.fromstring(table_markup)

def table_row(*args: Union[str, html.Element]) -> html.Element:

    tds = []

    for arg in args:
        td = html.Element('td')
        if isinstance(arg, str):
            td.text = arg
        else:
            SubElement(td, arg)
        tds.append(td)

    # create tr element
    tr = html.Element('tr')
    tr.extend(tds)

    return tr
