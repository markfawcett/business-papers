#!/usr/local/bin/python3

# module needed to parse command line arguments
import sys

# working with file paths
from os import path
import datetime
import urllib.request
import ssl



fileextension = '.xml'
portal_url = 'http://services.orderpaper.parliament.uk/businessitems/tableditemswithdate.xml?'\
             'key=e16ca3cd-8645-4076-aaba-3f1f31028da1&fromDate={}&toDate={}&type=effectives'


def get_xml_from_portal_to_publish(date, output_folder):
    # makesure the date is a proper date
    try:
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
    except:
        print('\nERROR:\tLooks like the sitting date, {}, is in the wrong format. The date should be in the form YYYY-MM-DD.'.format(date))
        return
    # since the date is correct we can create the output file name
    outputfile_name = f'OP{date_obj.strftime("%y%m%d")}{fileextension}'
    # put the date into the url
    url = portal_url.format(date, date)

    print('\nGetting XML (for publications.parliament) from:',
          '  ' + url, sep='\n')

    try:
        # ignore the ssl certificate
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(portal_url, context=context)
    except:
        print('\nERROR:\tCan\'t get the XML from:\n{}\nCheck the url is right.'.format(url))
        return
    data = response.read()      # a `bytes` object

    # write out the output html files
    outputfile_location = path.join(output_folder, outputfile_name)

    output_file = open(outputfile_location, 'wb')
    output_file.write(data)
    output_file_path = path.abspath(output_file.name)
    output_file.close()
    print('\nXML to upload to publications.parliament is saved at:\n{}'.format(output_file_path))



def main():
    if len(sys.argv) < 3:
        print("\nThis script takes 2 argument.",
              "  1. The sitting date in the for the Order Paper. " \
              "Please use the form YYYY-MM-DD, i.e.'2016-09-12'\n",
              "  2. The path to the folder you would like the output to be saved into",
              sep='\n')
        exit()

    input_date = sys.argv[1]
    output_folder = sys.argv[2]

    get_xml_from_portal_to_publish(input_date, output_folder)


if __name__ == "__main__": main()
