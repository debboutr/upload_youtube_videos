Here's how I built the environment with Anaconda...
	
	-- conda create -n ytb pandas xlrd python=3.6
	-- activate ytb
	-- pip install --upgrade google-api-client google-auth-oauthlib google-auth-httplib2 oauthclient
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

