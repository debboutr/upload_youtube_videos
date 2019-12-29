# -*- coding: utf-8 -*-

#!/usr/bin/python

import http.client
import httplib2
import os
import random
import sys
import time
import logging
import getpass
import pandas as pd
from datetime import datetime as dt
from argparse import Namespace, ArgumentParser, RawDescriptionHelpFormatter

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

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

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
  http.client.IncompleteRead, http.client.ImproperConnectionState,
  http.client.CannotSendRequest, http.client.CannotSendHeader,
  http.client.ResponseNotReady, http.client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google API Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options):
  tags = None
  if options.keywords:
    tags = options.keywords.split(",")

  body=dict(
    snippet=dict(
      title=options.title,
      description=options.description,
      tags=tags,
      categoryId=options.category
    ),
    status=dict(
      privacyStatus=options.privacyStatus
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(list(body.keys())),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print("Uploading file...")
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
          print("Video id '%s' was successfully uploaded." % response['id'])
        else:
          exit("The upload failed with an unexpected response: %s" % response)
    except HttpError as e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print(error)
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print("Sleeping %f seconds and then retrying..." % sleep_seconds)
      time.sleep(sleep_seconds)

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
    args = Namespace(   auth_host_name='localhost',
                        auth_host_port=[8080, 8090],
                        category='28', # 28 is Sciecnce & Technology
                        description='bologna',
                        file='/a/bogus/path/to/file.mp4',
                        keywords='',
                        logging_level='ERROR',
                        noauth_local_webserver=False,
                        privacyStatus='unlisted',
                        title='testes')
    youtube = get_authenticated_service(args)
    for uid, row in tbl.iterrows():
        desc = TEXT.format(row[date_col].year if is_xl else row[date_col])
        args.description=desc
        args.file=row.Path
        args.title=row['Youtube name']
        print(args)
        try:
            initialize_upload(youtube, args)
        except HttpError as e:
            # this is where the 403 error was thrown and where the sleep will
            # have to go. mid-loop
            wait_time = (60*30) #extra half hour to be sure
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
            for chunk in range(50):
                print(chunk)
                time.sleep(wait_time)
            youtube = get_authenticated_service(args)
            initialize_upload(youtube, args)
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


    formatter_class = RawDescriptionHelpFormatter
    parser = ArgumentParser(prog='process_tables.py',
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



  # argparser.add_argument("--file", required=True, help="Video file to upload")
  # argparser.add_argument("--title", help="Video title", default="Test Title")
  # argparser.add_argument("--description", help="Video description",
  #   default="Test Description")
  # argparser.add_argument("--category", default="22",
  #   help="Numeric video category. " +
  #     "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
  # argparser.add_argument("--keywords", help="Video keywords, comma separated",
  #   default="")
  # argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
  #   default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
  # args = argparser.parse_args()

  # if not os.path.exists(args.file):
  #   exit("Please specify a valid file using the --file= parameter.")

  # youtube = get_authenticated_service(args)
  # try:
  #   initialize_upload(youtube, args)
  # except HttpError as e:
  #   print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
