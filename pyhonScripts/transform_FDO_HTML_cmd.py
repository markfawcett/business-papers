#!/usr/local/bin/python3

# module needed to parse command line arguments
import sys
# working with xml
from lxml import html  # type: ignore
# for working with dates
import datetime
# for working with paths
from os import path
from pathlib import Path

# output file name
output_file_name = 'futoral.html'


def html_transform(input_html, template_html,
                   published_date, prepared_date,
                   output_folder: str = '') -> Path:

    input_root = html.parse(input_html).getroot()
    output_tree = html.parse(template_html)
    output_root = output_tree.getroot()
    # template_root = html.parse(template_html).getroot()


    # ----------------- get the date in the forms we want --------------------
    publishing_date_obj = datetime.datetime.strptime(published_date, '%Y-%m-%d').date()
    publishing_date_long = publishing_date_obj.strftime('%A %d %B %Y').replace(' 0', ' ', 1)  # like Wednesday 8 November 2017
    prepared_date_obj = datetime.datetime.strptime(prepared_date, '%Y-%m-%d').date()
    prepared_date_long  = prepared_date_obj.strftime('%A %d %B %Y').replace(' 0', ' ', 1)


    # ----------------- massarge input html from InDesign --------------------

    # first remove some of the titles we dont need
    # first_heading  = input_root.xpath('body/div[@id="_idContainer000"]/*[@class="Headings_Heading3"]')
    second_heading = input_root.xpath('body/div[@id="_idContainer000"]/*[@class="Headings_Heading1"]')
    third_heading  = input_root.xpath('body/div[@id="_idContainer000"]/*[@class="Headings_Heading2"]')

    # if len(first_heading) > 0:
    #     first_heading[0].getparent().remove(first_heading[0])
    if len(second_heading) > 0:
        second_heading[0].getparent().remove(second_heading[0])
    if len(third_heading) > 0:
        third_heading[0].getparent().remove(third_heading[0])

    # remove all the gray lines from InDesign
    lines_to_remove = input_root.xpath(
        'body/div/p[@class="Lines_Line-After-Full-Longer"]|p[@class="Lines_Half-line-after"]|p[@class="Lines_Full-line-after"]'
    )
    for line in lines_to_remove: line.getparent().remove(line)

    # remove any spaces between T and the question numbers etc
    question_number_spans = input_root.xpath('//p[@class="questionContainer"]/span[1]')
    for q_num in question_number_spans:
        q_num.attrib['class'] = q_num.attrib['class'].replace(' _idGenBNMarker-1', '')
        q_num.text = q_num.text.replace('T ', 'T')

    # add Ids to the headings so that we can link to them
    all_h3s_to_link_to = input_root.xpath('body//h3[@class="target"]')
    for i, h3 in enumerate(all_h3s_to_link_to):
        if h3.text is not None:
            h3.set('id', 'fdo{}'.format(i + 1))




    # ----------------- prepare template html ------------------------
    # put date in head section
    head_title = output_root.find('head/title')
    if head_title is not None and head_title.text is not None:
        head_title.text += ' ' + publishing_date_long

    # put date in footer
    footer_date = output_root.find('.//div[@id="footerBlockDate"]/p')
    if footer_date is not None and footer_date.text is not None:
        footer_date.text += ' ' + prepared_date_long


    #  ---------------- put InDesign output html into a template. ---------
    # get handle in template file where we can put the html from InDesign
    # main_text_location = output_root.find('body/div/div/div[@id="mainTextBlock"]')
    # # append the html from InDesign
    # input_body = input_root.find('body')
    # for element in input_body:
    #     main_text_location.append(element)

    append_point = output_root.xpath('//div[@id="content-goes-here"]')
    if len(append_point) < 1:
        show_error('Script can\'t find <div id="content-goes-here"> in the template.'
                   ' This is needed as this is where we are going inject html from the input html')
        exit()
    else:
        append_point = append_point[0]

    input_body = input_root.find('body')
    for element in input_body:
        append_point.append(element)



    output_file_name = datetime.datetime.strptime(prepared_date, '%Y-%m-%d').strftime('%y%m%d')

    output_file_name = 'fdo' + output_file_name + '.html'

    if output_folder:
        output_file_Path = Path(output_folder).joinpath(output_file_name)
    else:
        # output_file_Path = path.join(base_path, output_file_name)
        output_file_Path = Path(input_html).parent.joinpath(output_file_name)

    output_tree.write(str(output_file_Path.resolve()),
                      doctype='<!DOCTYPE html>',
                      encoding='UTF-8',
                      method="html",
                      xml_declaration=False)

    print('Output file path: ', output_file_Path.resolve(), '\n')

    return output_file_Path


    # output_string = html.tostring(output_root).decode(encoding='UTF-8')
    # # add last closign div and doctype
    # output_string = '<!DOCTYPE html>' + output_string.replace(
    #     '<!-- leave extra closing div. It is for wrapper-->',
    #     '<!-- leave extra closing div. It is for wrapper-->\n</div>'
    # )
    # # get input file path
    # input_file_path = path.dirname(input_html)
    # output_file = open(
    #     path.join(input_file_path, output_file_name),
    #     'w'
    # )
    # output_file.write(output_string)
    # print('Output file is at: {}'.format(path.abspath(output_file.name)))
    # output_file.close()



def main():
    if len(sys.argv) != 5:
        print("\nThis script takes 4 arguments.\n",
              "1:\tthe path to the file you wish to process.\n",
              "2:\tthe path to the html template file.\n",
              "3:\tthe publishing date in the form YYYY-MM-DD.\n",
              "4:\tthe prepared date in the form YYYY-MM-DD.")
        exit()

    input_html = sys.argv[1]
    template_html  = sys.argv[2]
    published_date = sys.argv[3]  # expected in the form YYYY-MM-DD
    prepared_date  = sys.argv[4]  # expected in the form YYYY-MM-DD

    print('Input file is located at: ' + path.abspath(input_html))
    html_transform(input_html, template_html, published_date, prepared_date)
    print('\nAll Done Chum!')


def show_error(error_text):
    error_text = 'ERROR: ' + error_text
    print('\033[91m' + error_text + '\033[0m')
    # messagebox.showerror('ERROR', error_text)


if __name__ == "__main__": main()
