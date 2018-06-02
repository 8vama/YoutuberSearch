
# -*- coding: utf-8 -*-

import os
import json
import codecs
import google.oauth2.credentials

import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def print_response(response):
  print(response)

# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.
def build_resource(properties):
  resource = {}
  for p in properties:
    # Given a key like "snippet.title", split into "snippet" and "title", where
    # "snippet" will be an object and "title" will be a property in that object.
    prop_array = p.split('.')
    ref = resource
    for pa in range(0, len(prop_array)):
      is_array = False
      key = prop_array[pa]

      # For properties that have array values, convert a name like
      # "snippet.tags[]" to snippet.tags, and set a flag to handle
      # the value as an array.
      if key[-2:] == '[]':
        key = key[0:len(key)-2:]
        is_array = True

      if pa == (len(prop_array) - 1):
        # Leave properties without values out of inserted resource.
        if properties[p]:
          if is_array:
            ref[key] = properties[p].split(',')
          else:
            ref[key] = properties[p]
      elif key not in ref:
        # For example, the property is "snippet.title", but the resource does
        # not yet have a "snippet" object. Create the snippet object here.
        # Setting "ref = ref[key]" means that in the next time through the
        # "for pa in range ..." loop, we will be setting a property in the
        # resource's "snippet" object.
        ref[key] = {}
        ref = ref[key]
      else:
        # For example, the property is "snippet.description", and the resource
        # already has a "snippet" object.
        ref = ref[key]
  return resource

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.iteritems():
      if value:
        good_kwargs[key] = value
  return good_kwargs

def search_list_by_keyword(client, f, name_id_dict, **kwargs):
  # return nextPageToken
  # updates name_id_dict


  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.search().list(
    **kwargs
  ).execute()


  # updates name_id_dict
  get_video_url(response, name_id_dict )

  #return
  if "nextPageToken" in response.keys():
    return response["nextPageToken"]

  return None


def get_video_url(data, name_id_dict):
  # updates name_id_dict
  result_lst = data["items"]

  for item in result_lst:
    youtuber_name = item["snippet"]["channelTitle"]
    channel_id = item["snippet"]["channelId"]

    name_id_dict[youtuber_name]= channel_id 



def filter_by_subscriber_count(name_id_dict):
  # add the entries w followers between 10k and 100k to the result string

  channel_temp = u"https://www.youtube.com/channel/"
  result_str = u""


  for key, value in name_id_dict.items():

    subscriberCount = subscribers_count_by_channel_id(client, 
      part='statistics',
      id=value)

    #print(subscriberCount)

    if int(subscriberCount) >= 10000 and int(subscriberCount) <= 100000:

      url = channel_temp + value + u"/about"
      result_str += key + u"," + subscriberCount + u"," + url + u"\n"

  result_str.encode('utf-8') 

  return result_str


def subscribers_count_by_channel_id(client, **kwargs):
  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.channels().list(
    **kwargs
  ).execute()

  return response["items"][0]["statistics"]["subscriberCount"]


def print_dict(dict):
  for key,value in dict.items():
    print key, value



# main program

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification. When
  # running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  client = get_authenticated_service()

  next_page_token=''
  f = codecs.open('test', encoding='utf-8', mode='w')
  final_result = ''
  name_id_dict = {}


  for i in range(20):
      print(i)
  
      next_page_token = search_list_by_keyword(client,
        f, 
        name_id_dict,
        part='snippet',
        maxResults=50,
        order= 'viewCount',
        pageToken = next_page_token,
        publishedAfter='2018-04-25T00:00:00Z',
        type='video',
        videoCategoryId=20)


  #print(name_id_dict)

  final_result += filter_by_subscriber_count(name_id_dict)

  final_result.encode('utf-8') 

  f.write(final_result)



  