
import os
import sys
import pandas as pd
from subprocess import call

tbl = pd.read_excel('O:/PRIV/MED_Videos/VideoMapViewer/Map Viewer Videos List.xlsx')
print(tbl.head())


tbl = tbl.loc[tbl.NewforMapViewer == 'yes']
tbl.set_index('UID', inplace=True)

tbl.UID.is_unique
tbl.index.is_unique
tbl.Path.is_unique
tbl.Filename.is_unique
tbl.Filename.loc[tbl.Filename.duplicated()]
tbl.loc[tbl.index.duplicated()].index
for uid in tbl.loc[tbl.index.duplicated()].index:
    print(tbl.loc[uid].Path[0])
    print(tbl.loc[uid].Path[1])

for uid, location in tbl.Path.iteritems():
    if not os.path.exists(location):
        print (f"UID: {uid} doesn't exist in the given location:{os.linesep}{location}")
        sys.exit()





call(['python','--version'])
for idx, row in tbl.iterrows():
    print(idx)
    call(['python','upload_video.py','--file',row.filename,'--description',
        row.description,'--title',row.title])

if __name__ == '__main__':
    print (sys.argv)
    # TODO: make checks for how this script fails!
    
    