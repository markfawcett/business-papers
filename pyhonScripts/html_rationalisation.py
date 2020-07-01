#!/usr/bin/env python3

from lxml import html  # type: ignore


REPLACES = [
    # list of 2 tupples of the form
    # ('class_to_be_replaced', 'replacemet_class')
    ('Master-and-Title-Page_OPDate', 'DateTitle'),
    ('VnP-Title', 'DocumentTitle'),

    # there are a buch of classes in the HTML from indesign of the form paraSomethingSomething
    # overkill me thinks
    ('paraAmendmentSponsor', 'AmendmentSponsor'),
    ('paraBusinessItemHeading', 'BusinessItemHeading'),
    ('paraBusinessItemHeading-bulleted', 'BusinessItemHeading-bulleted'),
    ('paraBusinessListItem', 'BusinessListItem'),
    ('paraBusinessSub-SectionHeading', 'BusinessSub-SectionHeading'),
    ('paraBusinessTodayChamberHeading', 'BusinessTodayChamberHeading'),
    ('paraChamberSummaryHeading', 'ChamberSummaryHeading'),
    ('paraFutureBusinessItemHeadingwithTiming', 'FutureBusinessItemHeadingwithTiming'),
    ('paraMinisterialStatement', 'MinisterialStatement'),
    ('paraMotionSponsor', 'Sponsor'),  # I think just Sponsor is sufficient
    ('paraMotionSub-Paragraph', 'MotionSub-Paragraph'),
    ('paraMotionSub-Sub-Paragraph', 'MotionSub-Sub-Paragraph'),
    ('paraMotionSub-Sub-Sub-Paragraph', 'MotionSub-Sub-Sub-Paragraph'),
    ('paraMotionText', 'MotionText'),  # I wonder if we need motion text at all...
    ('paraNotesTag', 'NotesTag'),
    ('paraNotesText', 'NotesText'),
    ('paraOrderofBusinessItemTiming', 'OrderofBusinessItemTiming'),
    ('paraSummaryAgendaItemTiming', 'SummaryAgendaItemTiming'),
]

def apply_all_fixes(html_element: html.Element) -> None:
    class_find_replace(html_element)
    remove_motion_text(html_element)
    fix_bold(html_element)


def class_find_replace(html_element: html.Element) -> None:
    """do a bunch of find and replaces on HTML classes"""
    for find, replace in REPLACES:
        for element in html_element.xpath(f'//*[contains(@class,"{find}")]'):
            element.classes.discard(find)
            element.classes.add(replace)


def remove_motion_text(html_element: html.Element) -> None:
    for element in html_element.xpath(f'//p[@class="paraMotionText"]|//p[@class="MotionText"]'):
        element.classes.discard('paraMotionText')
        element.classes.discard('MotionText')


def fix_bold(html_element: html.Element) -> None:
    """Rationalise bold elements to be <b>"""

    # element with the following tag names can be replaced with <b>
    b_tags = ['strong']

    # elements with these classes that can be replace with <b>
    b_classes = {'_5-Bold', 'Bold'}  # use set rarther than list

    xpath = ''

    for item in b_tags:
        xpath += f'//{item}|'

    for item in b_classes:
        xpath += f'//*[contains(@class,"{item}")]|'

    xpath = xpath.strip('|')

    print(xpath)

    for element in html_element.xpath(xpath):
        element.tag = 'b'
        element.classes -= b_classes
