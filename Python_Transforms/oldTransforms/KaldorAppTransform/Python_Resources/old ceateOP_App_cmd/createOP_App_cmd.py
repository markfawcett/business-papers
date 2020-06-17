#!/usr/local/bin/python3

# module needed to parse command line arguments
import sys
# stuff needed for parsing and manipulating XML
# this moduel does not come with python and needs to be installed with pip
from lxml import etree, html
# stuff needed for working with file paths
import os
# stuff for copying an entire directory of stuff and other high level file stuff
import shutil
# module for dates
from datetime import date, datetime
# deep copy stuff
from copy import deepcopy
# needed to make the png image
try:
    from PIL import ImageFont
    from PIL import Image
    from PIL import ImageDraw
except:
    print('ERROR: No PIL. Looks like you need to install pillow. Type "pip install Pillow"')
    exit()

# some variables used throughout
doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
fileextension = '.htm'
max_entries_in_opds = 30


def main():
    if len(sys.argv) != 5:
        print("\nThis script takes 4 arguments.\n",
              "1:\tthe path to the file you wish to process.\n",
              "2:\tthe path to the last opds.xml file.\n",
              "3:\tthe sitting date in the form YYYY-MM-DD.\n",
              "4:\tthe Number of this order paper e.g. 139")
        # "2:\tthe path to the app-templates Folder.\n",
        exit()

    infilename     = sys.argv[1]
    # app_templates  = sys.argv[2]
    last_opds_file = sys.argv[2]
    sitting_date   = sys.argv[3]
    number         = sys.argv[4]
    print('Input file is located at: {}\n'.format(os.path.abspath(infilename)))
    # create_app(infilename, app_templates, last_opds_file, sitting_date, number)
    create_app(infilename, last_opds_file, sitting_date, number)
    print('\nAll Done Chum!\n')


# def create_app(infilename, app_templates_path, opds_path, sitting_date, number):
def create_app(infilename, opds_input_path, sitting_date, number):

    # First set up dates and OP number
    Dates.set_up(sitting_date)  # dates
    create_html_section.set_number(number)  # OP number

    # PATHS
    # absolute path to app_templates_path
    app_templates_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    # get the path to the infile containing folder. This is where we will store all the outputs
    input_folder    = os.path.abspath(infilename)
    app_folder_path = os.path.dirname(input_folder)  # one level up
    # app_folder_path = os.path.join(app_folder_path, 'app')

    # app-static-files path
    app_static_files_path = os.path.join(app_templates_path, 'app-static-files')

    # path to for -for-ipad folder (e.g. OP180116-for-ipad)
    for_ipad_path = os.path.join(
        app_folder_path, 'OP{}-for-ipad'.format(Dates.sitting_date_compact))

    # path to the package folder. This will be zipped eventually
    package_path = os.path.join(for_ipad_path, Dates.sitting_date_compact, 'package')

    # html folder
    html_path = os.path.join(package_path, 'html')

    # manifest folder path
    maifest_folder = os.path.join(package_path, 'maifest')

    # path to the base cover image
    base_cover_img_path = os.path.join(app_templates_path, 'base_cover_img.png')

    # path to the app-html-section-templates folder
    app_html_section_templates = os.path.join(app_templates_path, 'app-html-section-templates')

    # path to opds export file
    opds_output_path = os.path.join(for_ipad_path, 'opds.xml')

    # paths to individual templates
    index_temp_path = os.path.join(app_html_section_templates, 'index-template.htm')
    sa_temp_path    = os.path.join(app_html_section_templates, 'sa-template.htm')
    btc_temp_path   = os.path.join(app_html_section_templates, 'btc-template.htm')
    btwh_temp_path  = os.path.join(app_html_section_templates, 'btwh-template.htm')
    wms_temp_path   = os.path.join(app_html_section_templates, 'wms-template.htm')
    com_m_temp_path = os.path.join(app_html_section_templates, 'com_meetings-template.htm')
    com_r_temp_path = os.path.join(app_html_section_templates, 'com_reports-template.htm')
    an_temp_path    = os.path.join(app_html_section_templates, 'announcements-template.htm')
    info_temp_path  = os.path.join(app_html_section_templates, 'info-template.htm')
    part2_temp_path = os.path.join(app_html_section_templates, 'part2-template.htm')


    # create directory structure
    # remove this directory if it exits
    if os.path.exists(for_ipad_path):
        shutil.rmtree(for_ipad_path)

    # copy the static file...
    try:
        shutil.copytree(app_static_files_path, package_path)
    except:
        input(
            '''Error. Can\'t copy {}. Make sore the folder doesnt have any perminsions issues.
            You may want to try copying the folder to your desktop and rerunning the script.
            Press any key to exit.'''.format(app_static_files_path)
        )
        exit()

    # add the html folder
    if not os.path.exists(html_path):
        os.makedirs(html_path)

    # add path to class
    create_html_section.html_path = html_path

    # add the maifest folder
    if not os.path.exists(maifest_folder):
        os.makedirs(maifest_folder)
    print('{}. Created folder structure.\n'.format(Counter.count()))


    # create the icon
    create_html_section.make_icon(for_ipad_path, base_cover_img_path)
    print('{}. Created icon.\n'.format(Counter.count()))
    print('{}. Creating html sections...'.format(Counter.count()))

    input_root = parse_clean_up(infilename, app_folder_path, Dates.sitting_date_compact)

    # first set up the headings_filename dictionary
    create_html_section.set_up_headings(input_root)
    # create_index_file(input_root)

    sa_file = create_sa_file(
        input_root, sa_temp_path, 'Summary Agenda', 'sa')

    # Create business chamber today section
    business_today = create_html_section(
        input_root, btc_temp_path, 'Business Today: Chamber', 'btc')
    business_today.split_on_headings('CHAMBER', 'BUSINESS TODAY: CHAMBER')


    # Create business westminseter hall section
    business_today_WH = create_html_section(
        input_root, btwh_temp_path, 'Business Today: Westminseter Hall', 'btwh')
    business_today_WH.split_on_headings('WESTMINSTER HALL', 'BUSINESS TODAY: WESTMINSTER HALL')


    # Create_written statements section
    written_statements = create_html_section(
        input_root, wms_temp_path, 'Written Statements', 'wms')
    written_statements.split_on_headings('WRITTEN STATEMENTS')


    # Create Committees meeting today section
    com_meeting = create_html_section(
        input_root, com_m_temp_path, 'Committee Meetings Today', 'com_meetings')
    com_meeting.split_on_headings('COMMITTEES MEETING TODAY')


    # Create Committee reports meeting today
    com_reports = create_html_section(
        input_root, com_r_temp_path, 'Committee Reports', 'com_reports')
    # ocasionally the heading here 'COMMITTEE REPORTS TO BE PUBLISHED'
    # or COMMITTEE REPORTS PUBLISHED etc.
    com_reports.split_on_headings(
        'COMMITTEE REPORTS PUBLISHED TODAY',
        'COMMITTEE REPORTS',
        'COMMITTEE REPORTS TO BE PUBLISHED',
        'COMMITTEE REPORTS PUBLISHED'
    )

    # Create announcements section
    announcements = create_html_section(
        input_root, an_temp_path, 'Announcements', 'announcements')
    announcements.split_on_headings('ANNOUNCEMENTS')


    # Create Furter info section
    further_info = create_html_section(
        input_root, info_temp_path, 'Further Infomation', 'info')
    further_info.split_on_headings('FURTHER INFORMATION')


    # create Part 2 section and store in memeory
    part2 = create_html_section(
        input_root, part2_temp_path, 'Part 2: Future Business', 'part2_')


    # split
    sa_file.sort_internal_links()
    sa_file.output_html_file()

    business_today.sort_internal_links()
    business_today.output_html_file()

    business_today_WH.sort_internal_links()
    business_today_WH.output_html_file()

    written_statements.sort_internal_links()
    written_statements.output_html_file()

    com_meeting.sort_internal_links()
    com_meeting.output_html_file()

    com_reports.sort_internal_links()
    com_reports.output_html_file()

    announcements.sort_internal_links()
    announcements.output_html_file()

    further_info.sort_internal_links()
    further_info.output_html_file()
    part2.output_part2()

    # index has to come last
    index_file = Create_index_file(
        input_root, index_temp_path, 'Contents', 'index', part2)
    index_file.output_html_file()


    # need to rearange files_produced
    if create_html_section.files_produnced[-1][1] == 'Contents':
        # move element to the frount
        create_html_section.files_produnced.insert(
            0, create_html_section.files_produnced.pop(-1)
        )
    # output the manifest file
    create_html_section.output_manifest_file(maifest_folder)
    # output the atom file
    create_html_section.output_atom_file(package_path)
    # update the opds file
    create_html_section.update_opds_file(opds_input_path, opds_output_path)
    # create the zip file
    create_html_section.zip_files_package_xml(os.path.join(
        for_ipad_path, Dates.sitting_date_compact))


class Dates:
    @classmethod
    def set_up(cls, sitting_date):

        # make a python date objects for sitting and creation dates
        cls.sitting_date_iso = sitting_date
        sitting_date = sitting_date.split('-')
        cls.sitting_date = date(int(sitting_date[0]), int(sitting_date[1]), int(sitting_date[2]))

        # siting date in the form Monday 12 September 2016
        cls.sitting_date_long = cls.sitting_date.strftime('%A %d %B %Y')

        # sitting date in the form 6 September 2016
        cls.sitting_date_medium = cls.sitting_date.strftime('%d %B %Y')
        # remove leading 0
        if(cls.sitting_date_medium[0] == '0'):
            cls.sitting_date_medium = cls.sitting_date_medium[1:]

        # set the sitting date in the form 170425
        cls.sitting_date_compact = cls.sitting_date.strftime('%y%m%d')

        # set up the update datetime for the atom xml file
        # cls.update_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        cls.update_datetime = datetime.utcnow().isoformat('T', 'milliseconds')
        # add the Z for zolo time needed for opds file
        cls.update_datetime = cls.update_datetime + 'Z'
        # set up the update datetime for the atom xml file
        cls.update_date = datetime.now().strftime('%Y-%m-%d')


class create_html_section:
    # CLASS VARIABLES
    # path
    html_path = ''
    # a class variable for all the files produced
    files_produnced = []
    # class variable for all the headings in the input
    headings = {}
    # internal hyperlinks dictionary
    internal_links = {}
    # the order paper number
    op_number = 0

    def __init__(self, input_root, path_to_template_file, file_title, filename):
        self.input_root = input_root
        self.template_root = etree.parse(path_to_template_file).getroot()
        self.file_title = file_title
        # output file name
        self.filename = filename + Dates.sitting_date_compact + fileextension
        # if the file is found not to exist change to False
        self.section_exists = True

        # add the order paper number to the subbanner
        subbanner_element = self.template_root.find('./body/div/div/div[@id="subbanner"]')
        subbanner_element.text = subbanner_element.text.replace('XXX', str(self.op_number))
        # change the date in the subbanner
        subbanner_element.find('span').text = Dates.sitting_date_long
        # sort the date in the head section
        self.template_root.find(
            './head/meta[@name="Date"]').set('content', Dates.sitting_date_long)
        # sort the filename in the head section
        temp_filename = 'Filename: sa{}{}'.format(Dates.sitting_date_compact, fileextension)
        self.template_root.find('./head/meta[@name="Identifier"]').set('content', temp_filename)
        # sort the title in the head section
        self.template_root.find('./head/title').text += Dates.sitting_date_long


    def get_input_root(self):
        return self.input_root

    def get_template_root(self):
        return self.template_root

    def split_on_headings(self, *heading_texts):
        # outputfile_name = kwargs['filename']
        insert_point = self.template_root.find('body/div/div/div/div[@id="mainTextBlock"]/div')
        # h2_headings = self.input_root.xpath('body/div/p[@class="paraBusinessTodayChamberHeading"]')
        for heading_text in heading_texts:
            if heading_text in create_html_section.headings:
                heading_of_interest = create_html_section.headings[heading_text]
                all_following_paras = heading_of_interest.xpath('following-sibling::*')
                insert_point.append(heading_of_interest)
                for para in all_following_paras:
                    if para.attrib.get('class') in ('paraBusinessTodayChamberHeading', 'paraChamberSummaryHeading', 'DocumentTitle'):
                        break
                    insert_point.append(para)
                # add internam link destinations to internal links
                # get all the links
                links = insert_point.xpath('//a')
                for link in links:
                    if link.get('id') is not None and '_idTextAnchor' in link.get('id'):
                        create_html_section.internal_links[link.get('id')] = self.filename
                return
        print('  WARNING:  Can\'t find section with heading(s) {}'.format(heading_texts))
        self.section_exists = False

    def output_part2(self):
        # outputfile_name = kwargs['filename']
        insert_point = self.template_root.find('body/div/div/div/div[@id="mainTextBlock"]/div')
        Summary_headings = self.input_root.xpath('body/div/h2[@class="paraChamberSummaryHeading"]')
        for hading in Summary_headings:
            if hading.text_content().upper() == 'FUTURE BUSINESS':
                all_following_paras = hading.xpath('following-sibling::*')
                insert_point.append(hading)
                for para in all_following_paras:
                    # add a business item separator before the dark gray headings in part2
                    if para.get('class', default=None) == 'paraBusinessTodayChamberHeading':
                        insert_point.append(html.fromstring(
                            '<p class="paraBusinessItemSeparator">&nbsp;</p>'))
                    # also change the class on paraFutureBusinessWHItemHeadingwithTiming
                    if para.get('class') == 'WHItemTiming':
                        para.set('class', 'paraFutureBusinessWHItemHeadingwithTiming')
                    insert_point.append(para)
                # also add links to each heading in future business
                gray_headings = insert_point.xpath('//*[@class = "paraBusinessTodayChamberHeading"]|//*[@class = "paraBusinessSub-SectionHeading"]')
                for i, heading in enumerate(gray_headings):
                    heading.set('id', 'heading{}'.format(i))
                # output to a file
                self.output_html_file()


    def sort_internal_links(self):
        root = self.template_root
        links = root.xpath('//a[@href]')
        for link in links:
            if '_idTextAnchor' in link.get('href'):
                link_text = link.get('href')
                link_text = link_text[link_text.find('#') + 1:]
                # find what file that link is in in the internal_links dictionary
                if link_text in create_html_section.internal_links:
                    destination_file = create_html_section.internal_links[link_text]
                    link_text = '{}#{}'.format(destination_file, link_text)
                    link.set('href', link_text)
                else:
                    link.set('href', '')


    def output_html_file(self):
        # first check that this section was found
        if self.section_exists is True:
            # output to a file
            outputfile_name = os.path.join(create_html_section.html_path, self.filename)
            outputfile = open(outputfile_name, 'w')
            outputfile.write(xml_declaration + '\n' + doctype + '\n')
            outputfile.write(html.tostring(self.template_root).decode(encoding='UTF-8'))
            outputfile.close()
            # add output file name to files produced list
            create_html_section.files_produnced.append([outputfile_name, self.file_title])
            print(' {}:\n   {}'.format(self.file_title, outputfile_name))


    @classmethod
    def set_number(cls, number):
        # global op_number
        try:
            cls.op_number = int(number)
        except ValueError:
            print('\nError:\tLooks like the OP number wasnt a real number. Please try again.')
            exit()


    @classmethod
    def set_up_headings(cls, input_root):
        if cls.headings == {}:
            temp_headings = input_root.xpath(
                'body/div/p[@class="paraBusinessTodayChamberHeading"]')
            for heading in temp_headings:
                heading_text = ''
                if heading.text is not None:
                    heading_text += heading.text
                if len(heading) > 0 and heading[-1].tail is not None:
                    heading_text += heading[-1].tail
                if heading_text != '':
                    cls.headings[heading_text.upper()] = heading


    @classmethod
    def output_manifest_file(cls, file_location):
        outputfile = open(os.path.join(
            file_location, '{}.manifest'.format(Dates.sitting_date_compact)), 'w')
        outputfile.write('CACHE MANIFEST\n# Files in House of Commons pack for: {}\n'.format(
            Dates.sitting_date_compact))
        for item in cls.files_produnced:
            outputfile_name = item[0]
            outputfile.write('../html/{}\n'.format(os.path.basename(outputfile_name)))
        outputfile.close()
        print('\n{}. Crated manifest file.\n'.format(Counter.count()))

    @classmethod
    def output_atom_file(cls, file_location):
        # first change the name of the attom file
        # atom file location
        # atom_file_location = os.path.join(file_location, 'atom.xml')
        new_atom_file_location = os.path.join(
            file_location, 'atom{}.xml'.format(Dates.sitting_date_compact))
        # os.rename(atom_file_location, new_atom_file_location)
        # # read in the template file as XML
        # input_root = etree.parse(new_atom_file_location).getroot()

        atom_xml = etree.fromstring(
            '<feed xmlns:dcterms="http://purl.org/dc/terms/" xmlns:atom="http://www.w3.org/2005/Atom" xmlns="http://www.w3.org/2005/Atom"></feed>')
        atom_xml.append(etree.fromstring('<title type="text">House of Commons</title>'))
        atom_xml.append(etree.fromstring('<subtitle type="text">Document Bundle Feeds</subtitle>'))
        atom_xml.append(etree.fromstring(
            '<updated>{}</updated>'.format(Dates.update_datetime)
        ))
        atom_xml.append(etree.fromstring(
            '<id>ipad-{}+:pubs</id>'.format(Dates.sitting_date_iso)
        ))
        atom_xml.append(etree.fromstring(
            '<id>ipad-{}+:pubs-ipad-{}-atom{}.xml</id>'.format(
                Dates.sitting_date_iso, Dates.sitting_date_compact, Dates.sitting_date_compact)
        ))
        atom_xml.append(etree.fromstring(
            '<link rel="self" type="application/atom+xml" href="http://www.publications.parliament.uk/ipad/{}/atom{}.xml" />'.format(
                Dates.sitting_date_compact, Dates.sitting_date_compact)
        ))
        atom_xml.append(etree.fromstring(
            '<link rel="related" type="text/cache-manifest" href="manifest/{}.manifest" />'.format(
                Dates.sitting_date_compact)
        ))
        atom_xml.append(etree.fromstring(
            '<link rel="alternate" type="text/html" href="html/index{}.htm" />'.format(
                Dates.sitting_date_compact)
        ))
        atom_xml.append(etree.fromstring('<author><name>user</name></author>'))

        for item in cls.files_produnced:
            outputfile_name = os.path.basename(item[0])
            file_title = item[1]
            # create an entry element
            entry = etree.Element('entry')
            entry.append(etree.fromstring(
                '<title>{}</title>'.format(file_title)
            ))
            entry.append(etree.fromstring(
                '<link rel="alternate" type="text/html" href="html/{}"/>'.format(outputfile_name)
            ))
            entry.append(etree.fromstring(
                '<id>html-{}</id>'.format(outputfile_name)
            ))
            entry.append(etree.fromstring(
                '<published>{}</published>'.format(Dates.sitting_date_iso)
            ))
            entry.append(etree.fromstring(
                '<updated>{}</updated>'.format(Dates.update_datetime)
            ))
            entry.append(etree.fromstring(
                '<summary>{}</summary>'.format(file_title)
            ))
            atom_xml.append(entry)

        outputfile = open(new_atom_file_location, 'w')
        outputfile.write(xml_declaration + '\n')
        outputfile.write(etree.tostring(atom_xml, pretty_print=True).decode(encoding='UTF-8'))
        outputfile.close()
        print('{}. Created atom file.\n'.format(Counter.count()))

    @classmethod
    def update_opds_file(cls, file_location, output_file_location):
        # opds_root = etree.parse(os.path.join(file_location, 'opds2.xml')).getroot()
        opds_root = etree.parse(file_location).getroot()
        # update the head section
        opds_root.find('{http://www.w3.org/2005/Atom}id').text = 'ipad-{}+:pubs'.format(Dates.update_date)
        opds_root.find('{http://www.w3.org/2005/Atom}updated').text = Dates.update_datetime
        # first look for any entries with the id as this
        xpath_string = '//x:id[./text() = "ipad-{}:atom-feed"]/..'.format(Dates.sitting_date_compact)
        # print(xpath_string)
        # print('./entry/id[./text() = "ipad-{}:atom-feed"]'.format(cls.sitting_date_compact))
        existing_entry = opds_root.xpath(xpath_string, namespaces={'x': 'http://www.w3.org/2005/Atom'})
        if len(existing_entry) > 0:
            # update the updated element
            existing_entry[0].find('{http://www.w3.org/2005/Atom}updated').text = Dates.update_datetime
        else:
            # create a new element
            # new_entry = etree.Element('entry')
            new_entry = etree.fromstringlist([
                '<entry xmlns:dcterms="http://purl.org/dc/terms/">',
                '<title>{}</title>'.format(Dates.sitting_date_medium),
                '<id>ipad-{}:atom-feed</id>'.format(Dates.sitting_date_compact),
                '<updated>{}</updated>'.format(Dates.update_datetime),
                '<dcterms:issued>{}</dcterms:issued>'.format(Dates.sitting_date_iso),
                '<summary type="text">A Day in the Commons</summary>',
                '<link rel="http://opds-spec.org/image" href="coverImages/cover{}.png" type="image/png"/>'.format(
                    Dates.sitting_date_compact),
                '<link rel="http://opds-spec.org/acquisition" type="application/pugpigpkg+xml" href="{}/package.xml"/>'.format(
                    Dates.sitting_date_compact),
                '<link rel="alternate" type="application/pugpigpkg+xml" href="{}/package.xml"/>'.format(
                    Dates.sitting_date_compact),
                '</entry>'
            ])
            # also remove the first entry if more than 1 entry
            entries = opds_root.findall('{http://www.w3.org/2005/Atom}entry')
            # remove first entry in opds file if greater that max_entries_in_opds
            if len(entries) >= max_entries_in_opds:
                entry_to_remove = entries[0]
                entry_to_remove.getparent().remove(entry_to_remove)
            opds_root.append(new_entry)
        # output the file
        # outputfile = open('opds{}.xml'.format(cls.sitting_date_compact), 'w')
        # outputfile = open(file_location, 'w')
        outputfile = open(output_file_location, 'w')
        outputfile.write(xml_declaration + '\n')
        outputfile.write(etree.tostring(opds_root, pretty_print=True).decode(encoding='UTF-8'))
        outputfile.close()
        print('{}. Updated opds.xml file.\n'.format(Counter.count()))


    @classmethod
    def zip_files_package_xml(cls, file_location):
        package_xml = etree.fromstringlist([
            '<package xmlns:atom="http://www.w3.org/2005/Atom" root="atom{}.xml">'.format(
                Dates.sitting_date_compact),
            '<part name="edition" src="package.zip" modified="{}"/>'.format(Dates.update_datetime),
            '</package>'])
        # zip up file
        package_location = os.path.join(file_location, 'package')
        shutil.make_archive(package_location, 'zip', package_location)
        # delete the folder from wich the zip file was made
        shutil.rmtree(package_location)
        # get the size of the zip file
        size_of_zip = os.path.getsize(os.path.join(file_location, 'package.zip'))
        package_xml[0].set('size', '{}'.format(size_of_zip))
        # export the xml
        outputfile = open(os.path.join(file_location, 'package.xml'), 'w')
        outputfile.write(xml_declaration + '\n')
        outputfile.write(etree.tostring(package_xml, pretty_print=True).decode(encoding='UTF-8'))
        outputfile.close()
        print('{}. Created Zip file and package.xml file.\n  {}\n'.format(Counter.count(), file_location))


    @classmethod
    def make_icon(cls, file_location, base_cover_img):
        # get the weekday in the form Tuesday
        weekday = Dates.sitting_date.strftime('%A')
        # get the day in the month e.g. 09
        day_in_month = Dates.sitting_date.strftime('%d')
        #  get the month and year in the form Apr 2017
        month_year = Dates.sitting_date.strftime('%b %Y')
        # now make the icon
        # check the script is running on windows
        if os.name == 'nt':
            verdana_27 = ImageFont.truetype('verdanab', 27)
            verdana_108 = ImageFont.truetype('verdanab', 108)
        else:
            verdana_27 = ImageFont.truetype('/Library/Fonts/Verdana Bold.ttf', 27)
            verdana_108 = ImageFont.truetype('/Library/Fonts/Verdana Bold.ttf', 108)
        cover_image_file = open(base_cover_img, 'rb')
        cover_image = Image.open(cover_image_file)
        draw = ImageDraw.Draw(cover_image)
        draw.text((90, 6), weekday, (255, 255, 255), font=verdana_27)
        draw.text((32, 101), day_in_month, (0, 0, 0), font=verdana_108)
        draw.text((42, 226), month_year, (0, 0, 0), font=verdana_27)
        draw = ImageDraw.Draw(cover_image)
        cover_image.save(os.path.join(file_location, 'cover' + Dates.sitting_date_compact + '.png'))


# new way create index
class Create_index_file(create_html_section):
    def __init__(self, input_root, path_to_template_file, file_title, filename, part2):
        super().__init__(input_root, path_to_template_file, file_title, filename)

        template_root = self.get_template_root()
        part2_root = part2.template_root
        # get a handle in the output root where we can add our info
        table_to_append_to = template_root.find('.//div[@id="mainTextBlock"]/div/div/table/tr/td[@id="appendPoint"]')

        # now append the next row that has all the other items in it
        for item in create_html_section.files_produnced:
            outputfile_name = os.path.basename(item[0])
            contents_item_text = item[1]

            if contents_item_text != 'Part 2: Future Business':
                output_paragraph = html.fromstring('<p class="paraContentsItem" style="margin-left : 4.8%; margin-right : 4.8%; padding-left : 2.1em; text-indent : -2.1em;"> <a href="{}" style="text-decoration : none; color : black;"> <span style="display : block; float : left; width : 2.1em; height : 1em;"> <img alt="OP button" src="../static/OPbutton.gif" style="display : inline; margin : 0;"/> </span>{}</a></p>'
                    .format(outputfile_name, contents_item_text))
            else:
                output_paragraph = html.fromstring('<p class="paraPartContentsHeading" style="margin-left : 4.8%; margin-right : 4.8%; "><a href="{}" style="text-decoration : none; color : black;">Part 2: Future Business</a></p>'.format(outputfile_name))

            table_to_append_to.append(output_paragraph)

        if part2.section_exists is True:
            # now add additional FB links
            bulk_item = html.fromstring(
                '<p class="paraOrderOfBusinessItemTiming" style="margin-left : 4.8%; margin-right : 4.8%; padding-left : 2.1em; margin-top : 0; margin-bottom : 0.5em;"></p>'
            )
            for heading in part2_root.xpath('//*[@class = "paraBusinessTodayChamberHeading"]|//*[@class = "paraBusinessSub-SectionHeading"]'):
                if heading.get('class') == 'paraBusinessTodayChamberHeading':
                    output_paragraph = html.fromstring('<p class="paraContentsItem" style="margin-left : 4.8%; margin-right : 4.8%; padding-left : 2.1em; text-indent : -2.1em;"> <a href="{}" style="text-decoration : none; color : black;"> <span style="display : block; float : left; width : 2.1em; height : 1em;"> <img alt="OP button" src="../static/OPbutton.gif" style="display : inline; margin : 0;"> </span>{}</a> </p>'.format(part2.filename + '#' + heading.get('id'), heading.text))
                    table_to_append_to.append(output_paragraph)
                    table_to_append_to.append(deepcopy(bulk_item))
                elif heading.get('class') == 'paraBusinessSub-SectionHeading':
                    if heading.text is not None:
                        link_text = heading.text.strip().replace(
                            ' ', '&nbsp;').replace(
                            'Monday',    '').replace(
                            'Tuesday',   '').replace(
                            'Wednesday', '').replace(
                            'Thursday',  '').replace(
                            'Friday',    '')
                        link_text += ' | '
                        link_href = part2.filename + '#' + heading.get('id')
                        output_paragraph = html.fromstring(
                            '<a href="{}" style="text-decoration : none; color : black; font-weight : bold; font-size : 0.8em;">{}</a>'.format(link_href, link_text))
                        table_to_append_to[-1].append(output_paragraph)
        # add the xmlns back to the html element
        template_root.set('xmlns', 'http://www.w3.org/1999/xhtml')


def parse_clean_up(inputfile_name, app_folder_path, sitting_date_compact):
    # parse and build up a tree for the input file
    input_root = html.parse(inputfile_name).getroot()

    for bullet_point in input_root.xpath('//span[@class="pythonFindBullet"]'):
        bullet_point.attrib.pop('class')
        bullet_point.set('style', 'display : block; float : left; width : 2.1em; height : 1em;')
        bullet_point.append(etree.fromstring(
            '<img alt="OP button" src="../static/OPbutton.gif" style="display : inline; margin : 0;"/>'))
        bullet_point.text = None

    for oral_question in input_root.xpath('//p[@class="paraQuestion"]/strong|//p[@class="paraQuestion"]/span[@class="Bold"]'):
        oral_question.tag = 'span'
        oral_question.attrib.pop('class')
        oral_question.set('style', 'display : block; float : left; width : 2.1em; height : 1em;')
        oral_question_number = oral_question.text.strip()
        oral_question.text = None
        oral_question.append(etree.fromstring(
            '<span class="charBallotNumber">' + oral_question_number + '</span>'))

    # sort out numbers in written statements
    for statement_span in input_root.xpath('//p[@class="paraMinisterialStatement"]/span[@class="Bold"]'):
        statement_span.set('style', 'display : block; float : left; width : 2.1em; height : 1em;')
        span_text = statement_span.text
        statement_span.append(etree.fromstring(
            '<span class="charItemNumber">{}</span>'.format(span_text)))
        statement_span.text = None

    # change class MotionAmmendmentSponsor to paraAmendmentSponsor
    ammendment_sponsors = input_root.xpath('//p[@class="MotionAmmendmentSponsor"]')
    for sponsor in ammendment_sponsors:
        sponsor.set('class', 'paraAmendmentSponsor')

    # sort motion sponsor groups
    sponsor_groups = input_root.xpath('//p[@class="paraMotionSponsorGroup"]|//p[@class="MotionAmmendmentSponsorGroup"]')
    for sponsor_group in sponsor_groups:
        # split text on the tab character
        sponosr_names = sponsor_group.text.split('\u0009')
        sponsor_group.text = None
        for sponosr_name in sponosr_names:
            if sponosr_name == '':
                continue
            sponsor_span = html.fromstring(
                '<span style="display : block; float : left; width : 16em; height : 1.4em;"></span>')
            sponsor_span.text = sponosr_name
            sponsor_group.append(sponsor_span)

    # sort out the h2 heading elements
    for h2_heading in input_root.xpath('body/div/h2[@class="paraBusinessTodayChamberHeading"]'):
        if h2_heading.text is not None or h2_heading[0].tail is not None:
            h2_heading.insert(0, etree.fromstring(
                '<span style="display : block; float : left; width : 4.7%; height : 1em;"> </span>'))
        h2_heading.tag = 'p'
        # change the text in this h2_heading to all caps
        # if len(h2_heading) > 0:
        #     # print(etree.tostring(h2_heading))
        #     if h2_heading[-1].text is not None:
        #         h2_heading[-1].text = h2_heading[-1].text.upper()
        #     if h2_heading[-1].tail is not None:
        #         h2_heading[-1].tail = h2_heading[-1].tail.upper()
        # if h2_heading.text is not None:
        #     h2_heading.text = h2_heading.text.upper()

    # sort out the h3 heading elements
    for h3_heading in input_root.xpath('body/div/h3[@class="paraBusinessSub-SectionHeading"]'):
        # .text_content():
        # Returns the text content of the element, including the text content of its children, with no markup.
        # heading_text = h3_heading.text_content().upper()
        # print(heading_text)
        # h3_heading.text = None
        h2_span = etree.fromstring(
            '<span style="display : block; float : left; width : 1.2%; height : 1em;"> </span>')
        # print(etree.tostring(h2_span))
        # h2_span.tail = heading_text
        h3_heading.append(h2_span)
        h3_heading.tag = 'p'

    # sort out paraFutureBusinessItemHeadingwithTiming spacing
    for span in input_root.xpath('body/div/p[@class="paraFutureBusinessItemHeadingwithTiming"]/*[@class="Bold"]'):
        span.attrib.pop('class')
        span.set('style', 'display : block; float : left; width : 5.7em; height : 1em;')

    # also sort out the paacing aroung WHItemTiming
    for span in input_root.xpath('body/div/p[@class="WHItemTiming"]/*[@class="Bold"][1]'):
        span.tag = 'span'
        span_text = span.text
        span.text = None
        span.set('style', 'display : block; float : left; width : 5.7em; height : 1em;')
        span.append(etree.fromstring(
            '<span class="charFutureBusinessItemTiming">{}</span>'.format(span_text)))

    # output to a file
    filepath = os.path.join(
        app_folder_path, 'amended-input' + sitting_date_compact + '.htm')
    outputfile = open(filepath, 'w')
    outputfile.write(xml_declaration + '\n' + doctype + '\n')
    outputfile.write(html.tostring(input_root).decode(encoding='UTF-8'))

    # return the input xml root element
    return input_root


class create_sa_file(create_html_section):
    def __init__(self, input_root, path_to_template_file, file_title, filename):
        super().__init__(input_root, path_to_template_file, file_title, filename)

        # add the table for the chamber summary agenda
        sa_table = etree.fromstring(
            '<table cellpadding="0" cellspacing="0" width="96%"> <col width="24%" /> <col width="76%" /></table>')
        table_divs = self.template_root.xpath('//div[@id="mainTextBlock"]/div/div[@class="table"]')
        # print(table_divs)
        input_table_bodys = self.input_root.xpath('body/div/table[@class="Front-Page-Table"]/tbody')

        # now change the chamber heading if it exists
        summary_headings = self.input_root.xpath('body/div/h2[@class="paraChamberSummaryHeading"]')
        # if len(summary_headings) == 1 or len(summary_headings) == 2:
        if len(summary_headings) >= 1 and summary_headings[0].text_content().upper() in ('SUMMARY AGENDA: CHAMBER', 'SUMMARY AGENDA: WESTMINSTER HALL'):
            summary_heading_text = summary_headings[0].text
            # put this text into the output
            self.template_root.find(
                './/p[@class="paraChamberSummaryHeading"]').text = summary_heading_text
            # start putting stuff in the table
            tbody = create_sa_file.set_up_table(input_table_bodys[0])
            chamber_table = deepcopy(sa_table)
            for tr in tbody:
                chamber_table.append(tr)
            table_divs[0].append(chamber_table)
            # print(etree.tostring(table_divs[0]))

        if len(summary_headings) >= 2 and summary_headings[1].text_content().upper() in ('SUMMARY AGENDA: WESTMINSTER HALL', 'WESTMINSTER HALL'):
            summary_heading_text = summary_headings[1].text
            # put this text into the output
            self.template_root.find(
                './/p[@class="paraWestminsterHallSummaryHeading"]').text = summary_heading_text
            tbody = create_sa_file.set_up_table(input_table_bodys[1])
            wh_table = deepcopy(sa_table)
            for tr in tbody:
                wh_table.append(tr)
            table_divs[1].append(wh_table)

    @staticmethod
    def set_up_table(tbody):
        for tr in tbody:
            tr.attrib.pop('class')
            for td in tr:
                td.attrib.pop('class')
                td.set('valign', "top")
            tr[0].set('style', "border-right-style : solid;&#xA;border-right-width : 1px;&#xA;border-padding-right : 0pt;&#xA;border-right-color : #000000;&#xA;background-color : #FFFFFF;&#xA;padding-left : 0%;&#xA;padding-right : 1.4%;&#xA;padding-top : 0%;&#xA;padding-bottom : 0%;&#xA;")
            # give paras a class of paraSummaryAgendaItemTiming in first col
            for paragraph in tr.findall('td[1]/p'):
                paragraph.set('class', "paraSummaryAgendaItemTiming")
            tr[1].set('style', "border-left-style : solid;&#xA;border-left-width : 1px;&#xA;border-padding-left : 0pt;&#xA;border-left-color : #000000;&#xA;background-color : #FFFFFF;&#xA;padding-left : 1.4%;&#xA;padding-right : 0%;&#xA;padding-top : 0%;&#xA;padding-bottom : 0%;&#xA;")
            # give paras a class of paraSummaryAgendaItemText in second col
            for paragraph in tr.findall('td[2]/p'):
                paragraph.set('class', "paraSummaryAgendaItemText")
        return tbody


# helper class to count in print functions
class Counter():
    counter = 0

    @classmethod
    def count(cls):
        cls.counter += 1
        return str(cls.counter)


if __name__ == "__main__":
    main()
