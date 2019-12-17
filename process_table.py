import pandas as pd
from subprocess import call

tbl = pd.read_csv('table.csv')
print(tbl.head())

call(['python','--version'])
for idx, row in tbl.iterrows():
    print(idx)
    call(['python','upload_video.py','--file',row.filename,'--description',
        row.description,'--title',row.title])
