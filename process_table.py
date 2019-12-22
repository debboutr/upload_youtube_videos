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
import logging
import getpass
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


def main(fn):
    if fn.split('.')[-1] == 'xlsx':
        tbl = pd.read_excel(fn)
    if fn.split('.')[-1] == 'csv':
        tbl = pd.read_csv(fn)
    uid_col = 'UID'
    path_col = 'Path'
    # print(tbl.head())
    columns = [
                 'NewforMapViewer',
                 'UID',
    ]

    tbl = tbl.loc[tbl.NewforMapViewer == 'yes']
    
    try: # check column for uniqueness, fail gracefully if not.
        assert tbl[uid_col].is_unique
    except AssertionError as e:

        logging.critical('%s column is not unique. FAIL!', uid_col)
        print (f'{uid_col} column is not unique. FAIL!')
        sys.exit()
    try: # check column for uniqueness, fail gracefully if not.
        assert tbl[path_col].is_unique
    except AssertionError as e:
        logging.critical('%s column is not unique. FAIL!', path_col)
        print (f'{path_col} column is not unique. FAIL!')
        sys.exit()
    tbl.set_index('UID', inplace=True, drop=False)

        
    # tbl.index.is_unique
    # tbl.Path.is_unique
    # tbl.Filename.is_unique
    # tbl.Filename.loc[tbl.Filename.duplicated()]
    # tbl.loc[tbl.index.duplicated()].index
    
    # for uid in tbl.loc[tbl.index.duplicated()].index:
    #     print(tbl.loc[uid].Path)
    #     print(tbl.loc[uid].Path)

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


    # logging.info(' %s ', EXEC_TIME)
    # logging.warning(' %s ', EXEC_TIME)
    # logging.error('this is an error!')
    # logging.critical('this is an error!')

year = 2222
# formatted description
(f"---------\n\nPublished on { dt.now().strftime('%B %d, %Y') }"
"NOTE: No captions are provided because all sound is underwater or background"
f"noise.\n\n\nThis video was collected in { year } as part of the EPA Environmental "
"Assessment Research Programs.\n\n\nFor more information about EPA: "
"http://www.epa.gov/ We accept comments according to out comment policy: "
"http://blog.epa.gov/blog/comment-policy/")

'''
---------


{ dt.now().strftime("%B %d, %Y") }
Published on December 19, 2019

NOTE: No captions are provided because all sound is underwater or background noise.



This video was collected in 2017 as part of the EPA Environmental Assessment Research Programs.

For more information about EPA: http://www.epa.gov/ We accept comments according to out comment policy: http://blog.epa.gov/blog/comment-policy/



------------
'''
    # call(['python','--version'])
    # for idx, row in tbl.iterrows():
    #     print(idx)
    #     call(['python','upload_video.py','--file',row.filename,'--description',
    #         row.description,'--title',row.title])

def is_valid_file(parser, arg):
    if not os.path.isfile(arg):
        parser.error(f"The file {arg} does not exist!")
    ft = arg.split('.')[-1]
    if ft not in ['csv','xlsx']:
        parser.error(f"This script doesn't support this filetype: .{ft}")
    return arg

if __name__ == '__main__':

    if os.sep in  sys.argv[0]:
        print ('Please run this file in the directory where it is located!\n'
               'so that the .logging/ directory can be found if needed later!')
        sys.exit()
    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(prog='process_tables.py',
            formatter_class=formatter_class,
            description=(DESCRIPTION + os.getcwd() + '/.logging/'),
             epilog=EPILOG)
    parser.add_argument("file", help="path/to/xl/or/csv/table.xlsx",
                        type=lambda x: is_valid_file(parser, x))
    args = parser.parse_args()
    EXEC_TIME = dt.now()
    if not os.path.exists('./.logging'):
        os.mkdir('./.logging')
    script_name = sys.argv[0].split('.')[0].split(os.sep)[-1]
    fn = ( f".logging/{script_name}_{EXEC_TIME.strftime('%s')}.log" )
    logging.basicConfig(level=logging.INFO,
                         filename=fn, format='%(levelname)s: %(message)s')
    logging.info('DATE: %s', EXEC_TIME)
    logging.info('This script was run by: %s', getpass.getuser())
    logging.info('FILE_ARG: %s', sys.argv[1])
    main(args.file)








