"""
Shows basic usage of the Sheets API. Prints values from a Google Spreadsheet.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))

SPREADSHEET_ID = '1Hc6Us9pXghq0Phl4MCEx-2xxZUTRODBzK_mVpLVQlCY'
RANGE_NAME = 'Sheet1!A2:C5'
value_input_option= 'RAW';

def write_values(range_name, values):

	#values = [
    #[1,2,3],
    # Additional rows ...
    #[4,5,6]
	#]
	body = {
    	'values': values
	}
	result = service.spreadsheets().values().update(
	    spreadsheetId=SPREADSHEET_ID, range=range_name,
	    valueInputOption=value_input_option, body=body).execute()
	print('{0} cells updated.'.format(result.get('updatedCells')));


def read_values(range_name):
	# Call the Sheets API
	result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
	                                             range=RANGE_NAME).execute()
	values = result.get('values', [])
	if not values:
	    print('No data found.')
	else:
	    print('Name, Subscribers:')
	    for row in values:
	        # Print columns A and E, which correspond to indices 0 and 4.
	        print('%s, %s' % (row[0], row[1]))

#if __name__ == '__main__':
#	write_values(RANGE_NAME)
