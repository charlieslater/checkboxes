From parent directory, run:

google_appengine/dev_appserver.py --host 0.0.0.0 checkboxes

The main app.yaml file is for "Listathon" and uses list.py, but there are 3 other app.yaml files:

app.generated - generated checkboxes 
app.checkboxes - static html.
app.orderedlists - store in Google NDB.  Display as numbered lists.
