Here's how I built the environment with Anaconda...

	-- conda create -n ytb pandas xlrd python=3.6
	-- activate ytb
	-- pip install --upgrade google-api-python-client google-auth-oauthlib google-auth-httplib2 oauthclient
then, you're good to go.


In order to obtain the "client_secrets.json" file you will need to sign into google as the
US EPA Water Survey and then navigate to this URL:

	-- https://console.developers.google.com/apis/dashboard

from here you will see a credentials tab on the left, go there, and then you should see a list of project
names that also show the clientID, at the far right side of the row for a given project you can click on
the download symbol which will DL the file which you

	MUST NAME THE FILE
	-- "client_secrets.json"

you can also click on the project name and at the top of the page there is the same link to "DOWNLOAD JSON"

th first upload that I made today was the first_run.csv and one of the vids was already on 3,210 calls after this from 2, like I say though, one video was already up. Just ran with a single video and here's what I get. 4,815. So, roughly 1,605 calls for a file that is 32.8 MB.

1,605 calls for the video <span05_08_camB.mp4> to be loaded! Dang!
3,210 - 1,605 for the video <fren05_18_camB.mp4> to be loaded! looks like they are the same numbe of calls.
# below is error from too many calls / day.
(ytb) rick@dingus:~/projects/youtube_upload$ python process_table.py '/home/rick/projects/youtube_upload/GREATLAKES/first_run.csv'
  NewforMapViewer  ...                           YouTubeName
0             yes  ...  DVR100621_1247_001_Lake_Michigan.mp4
1             yes  ...  DVR100622_1205_001_Lake_Michigan.mp4

[2 rows x 18 columns]
Uploading file...
An HTTP error 403 occurred:
b'{\n "error": {\n  "errors": [\n   {\n    "domain": "youtube.quota",\n    "reason": "quotaExceeded",\n    "message": "The request cannot be completed because you have exceeded your \\u003ca href=\\"/youtube/v3/getting-started#quota\\"\\u003equota\\u003c/a\\u003e."\n   }\n  ],\n  "code": 403,\n  "message": "The request cannot be completed because you have exceeded your \\u003ca href=\\"/youtube/v3/getting-started#quota\\"\\u003equota\\u003c/a\\u003e."\n }\n}\n'
0
Uploading file...
An HTTP error 403 occurred:
b'{\n "error": {\n  "errors": [\n   {\n    "domain": "youtube.quota",\n    "reason": "quotaExceeded",\n    "message": "The request cannot be completed because you have exceeded your \\u003ca href=\\"/youtube/v3/getting-started#quota\\"\\u003equota\\u003c/a\\u003e."\n   }\n  ],\n  "code": 403,\n  "message": "The request cannot be completed because you have exceeded your \\u003ca href=\\"/youtube/v3/getting-started#quota\\"\\u003equota\\u003c/a\\u003e."\n }\n}\n'
0
