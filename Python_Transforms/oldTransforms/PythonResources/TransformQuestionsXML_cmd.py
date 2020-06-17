#!/usr/local/bin/python3

# module needed to parse command line arguments
import sys
# stuff needed for parsing and manipulating XML
# this moduel does not come with python and needs to be installed with pip
from lxml import etree
# stuff needed for working with file paths
from os import path

# some variables used throughout
fileextension = 'Questions_4_ID.xml'


def transform_xml(inputfile):
    # parse and build up a tree for the input file
    input_root = etree.parse(inputfile).getroot()  # LXML element object for the root
    # create an output root element
    output_root = etree.Element('root')

    target_groups = input_root.xpath('//TargetGroup')

    for target_group in target_groups:
        # find the target head for each group
        target_head = target_group.find('TargetHead')
        # add timeing info to the output if exits in the input
        if len(target_group.xpath('./Time')) != 0:
            times_tag = etree.Element('Times')
            times_tag.text = 'At ' + target_group.findtext('Time', default='').replace(' ', '').replace(':', '.').replace('12.00pm', '12 noon')
            times_tag.tail = '\n'
            output_root.append(times_tag)
        # create an element for the bulleted questions title
        bullet_tag = etree.Element('Bulleted')
        bullet_tag.tail = '\n'
        output_root.append(bullet_tag)

        # find all the questions in this target group and store them in a list
        questions = target_group.findall('OralQn')
        # default question tag
        Question_tag_name = 'Question'
        # default question number prefix
        number_prefix = ''
        # first do ordinary oral questions
        if target_head.get('IsTopical') == 'N' and target_head.text != 'the Prime Minister':
            bullet_tag.text = 'Oral Questions to ' + target_head.text
            Question_tag_name = 'Question'
            number_prefix = ''

        # next to topical questions
        elif target_head.get('IsTopical') == 'Y':
            # add the questions to bullet point
            bullet_tag.text = 'Topical Questions to ' + target_head.text
            Question_tag_name = 'TopicalQuestion'
            number_prefix = 'T'

        # finaly do Prime Ministers Questions
        elif target_head.get('IsTopical') == 'N' and target_head.text == 'the Prime Minister':
            # add the questions to bullet point
            bullet_tag.text = 'Oral Questions to the Prime Minister'
            Question_tag_name = 'PMQ'
            number_prefix = 'Q'

        else:
            print('Error: check the input file contains TargetHead elements and that these elements all have\
             the attribute "IsTopical" and that the value of the IsTopical attribute is either an "Y" or an "N"\
             and if there are PMQs that the text of the TargetHead element is "the Prime Minister".')
            exit()
        for i in range(len(questions)):
            # make sure questions start at 1
            if i == 0:
                if Question_tag_name != 'PMQ':
                    restart = 'Restart'
            else:
                restart = ''
            # create different Question parent element depending on type of q
            Question_Element     = etree.Element(Question_tag_name + restart)
            # create child elements needed
            # number_element       = etree.Element('BoldNum')
            Member_Element       = etree.Element('Member')
            Constituency_Element = etree.Element('Constit')
            uin_Element          = etree.Element('UIN')
            # append elements to parent
            # Question_Element.append(number_element)
            Question_Element.append(Member_Element)
            Question_Element.append(Constituency_Element)
            Question_Element.append(uin_Element)
            # put in the question number in an attribute. This is not nessesary for InDesign.
            Question_Element.set('number', number_prefix + str(i + 1))
            # build up member name element from constiuent parts
            member_Title_text  = questions[i].findtext('Member/Title', default='').strip()
            member_Fnames_text = questions[i].findtext('Member/Fnames', default='').strip()
            member_Sname_text  = questions[i].findtext('Member/Sname', default='').strip()
            Member_Element.text = member_Title_text + " " + member_Fnames_text + " " + member_Sname_text
            # strip space from beginign added if the member does not have a title
            Member_Element.text = Member_Element.text.strip()

            # constituency element and UIN
            Constituency_Element.text = ' (' + questions[i].findtext('Member/Constit', default='').strip() + ')'
            uin_Element.text          = ' (' + questions[i].findtext('UIN', default='').strip() + ')'
            # get the QnText element from the input question
            qn_text = questions[i].find('QnText')
            if qn_text.get('PrintText') == 'Y':
                Constituency_Element.tail = u'\u2028' + qn_text.text.strip()
            Question_Element.tail = '\n'
            output_root.append(Question_Element)


    # get the path to input file
    pwd = path.dirname(path.abspath(inputfile))
    # write out the file
    filename = path.basename(inputfile).split('.')[0]
    filepath = path.join(pwd, filename)
    et = etree.ElementTree(output_root)
    try:
        et.write(filepath + fileextension)  # , pretty_print=True
        print('Output file is located at: ', filepath + fileextension)
        # outputfile = open(filepath, 'w')
    except:
        # make sure it works even if we dont have permision to modify the file
        try:
            et.write(filename + fileextension)
            print('\nOutput file is located at: ', path.abspath(filename + fileextension))
        except:
            et.write(filename + 1 + fileextension)
            print('\nOutput file is located at: ', path.abspath(filename + 1 + fileextension))


def main():
    if len(sys.argv) != 2:
        print("\nThis script takes 1 argument.\n",
              "1:\tthe path to the file you wish to process.\n",)
        exit()

    infilename = sys.argv[1]
    print('Input file is located at: ' + path.abspath(infilename))
    transform_xml(infilename)
    print('\nAll Done Chum!')


if __name__ == "__main__": main()
