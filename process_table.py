#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 19:34:19 2019

This script is used to bulk upload videos to YouTube based on an .xlsx or .csv
file. There needs to be exception handling because some of the videos have been
uploaded by hand and YouTube won't allow for the same video to be uploaded
twice. Logging output will be written into a log file that gets timestamped
with the epoch timestamp in the filename. This will illustrate the upload
process through these errors and allow for the script to continue to run
through every row in the table that is iterated over.

@author: rick
"""

import os
import sys
import getpass
import logging
import argparse
import pandas as pd
from subprocess import call
from datetime import datetime as dt

DESCRIPTION = '''
    Reads in a table that describe each video recorded that will be uploaded
    to YouTube. Currently, there is no standard on which columns are needed
    so the script will likely need adjustment there for future runs. There is
    also a logging file with a epoch timestamp in the title that will be saved
    here:\n\n\t'''

EPILOG = '''Example:
     $ python process_table.py /home/rick/projects/youtube_upload/table.xlsx'''

# text in the caption, args to format are drawn in from the table
TEXT = (f"Published on { dt.now().strftime('%B %d, %Y') }\n\n"
"NOTE: No captions are provided because all sound is underwater or background"
"noise.\n\n\nThis video was collected in {0} as part of the EPA Environmental "
"Assessment Research Programs.\n\n\nFor more information about EPA: "
"http://www.epa.gov/ We accept comments according to out comment policy: "
"http://blog.epa.gov/blog/comment-policy/")


def process(fn):

    if fn.split('.')[-1] == 'xlsx':
        is_xl = True
        tbl = pd.read_excel(fn)

    if fn.split('.')[-1] == 'csv':
        is_xl = False
        tbl = pd.read_csv(fn)
        tbl.DateCollected = tbl.DateCollected.str.slice(stop=4)

    uid_col = 'UID'
    path_col = 'Path'
    date_col = 'DateCollected'
    tbl = tbl.loc[tbl.NewforMapViewer == 'yes']

    validate_column_uniqueness([uid_col, path_col], tbl)

    tbl.set_index('UID', inplace=True, drop=False)
    for uid, location in tbl.Path.iteritems():
        miss = 0
        # print ('HERE:', location)
        if not os.path.exists(location):
            print (f"UID: <{uid}> doesn't exist in the given location:")
            print ('\t' + f"{location}")
            miss += 1
    if miss:
        print ('Either find these files and update, '
               'or remove them from the table''')
        logging.critical('Failed due to videos missing from where '
                         'they were stated to be!')
        sys.exit()
    print ('Table validation passed, begin calling YouTube API...')
    for uid, row in tbl.iterrows():

        # csv format won't be read-in as datetime objects like excel
        desc = TEXT.format(row[date_col].year if is_xl else row[date_col])
        response = call(['python', 'upload_video.py',
                          '--file',row.Path,
                          '--description', desc,
                          '--title', f'{row.StudyName} -- {row.UID}',
                          '--privacyStatus','unlisted'])
        print (response)
        logging.info('%s -- UID: %s successfully uploaded.', dt.now(), row.UID)

def is_valid_file(parser, arg):
    '''
    Check that the file exists and that it is of the right type for processing.

    Parameters
    ----------
    parser : ArgumentParser
        instance of argparse.ArgumentParser.
    arg : string
        Absolute path to CSV or Excel file.

    Returns
    -------
    arg : string
        Absolute path to CSV or Excel file.
    '''
    if not os.path.isfile(arg):
        parser.error(f"The file {arg} does not exist!")
    ft = arg.split('.')[-1]
    if ft not in ['csv','xlsx']:
        parser.error(f"This script doesn't support this filetype: .{ft}")
    return arg

def validate_column_uniqueness(cols, df):
    '''
    Checks that each column in the iterable is unique in the table. Will fail
    gracefully with print statements and additions to the log file if not.

    Parameters
    ----------
    cols : iterable
        Titles of columns in the df to be checked for uniqueness.
    df : DataFrame
        Table of data.

    Returns
    -------
    None.

    '''
    for col in cols:
        try:
            assert df[col].is_unique
        except AssertionError:
            logging.critical('%s column is not unique. FAIL!', col)
            print (f'{col} column is not unique. FAIL!')
            sys.exit()

if __name__ == '__main__':

    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(prog='process_tables.py',
            formatter_class=formatter_class,
            description=(DESCRIPTION + os.getcwd() + '/.logging/'),
             epilog=EPILOG)
    parser.add_argument("file", help="path/to/xl/or/csv/table.xlsx",
                        type=lambda x: is_valid_file(parser, x))
    args = parser.parse_args()
    if not os.path.exists('./.logging'):
        os.mkdir('./.logging')
    script_name = sys.argv[0].split('.')[0].split(os.sep)[-1]
    fn = ( f".logging/{script_name}_{dt.now().strftime('%s')}.log" )
    logging.basicConfig(level=logging.INFO,
                         filename=fn, format='%(levelname)s: %(message)s')
    logging.info('DATE: %s', dt.now())
    logging.info('This script was run by: %s', getpass.getuser())
    logging.info('FILE_ARG: %s', sys.argv[1])
    if os.sep in  sys.argv[0]:
        logging.critical('Failed due to running from the wrong directory.')
        print ('Please run this file in the directory where it is located!\n'
                'so that the .logging/ directory can be found if needed later!')
        sys.exit()
    process(args.file)
    logging.info('Script finished successfully')
