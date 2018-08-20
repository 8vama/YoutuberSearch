
# -*- coding: utf-8 -*-

import os
import json
import codecs
import google.oauth2.credentials

import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

from googleSheetsAPISample import write_values
from extractEmail import get_emails
from extractEmail import containsMusic
from collections import defaultdict

import ssl

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

newDict = {10 : "Music"}
test = ["electronic","electronic 2018","electronic gems","electronic supersonic","electronic sounds","electronica","electronic music","electronic songs","electronic drums"]
musicKeywords = ["edm music", "edm concert", "edm live","edm trap", "edm bass","edm beats","dubstep","dubstep drops", "dubstep mix", "dubstep music", "dubstep 2018", "dubstep gaming", "edm gaming", "dubstep and trap","house music","house music 2018","house music artists"]

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

def videos_list_by_id(client, **kwargs):
  # See full sample for function

  try: 
    kwargs = remove_empty_kwargs(**kwargs)

    response = client.videos().list(
      **kwargs
    ).execute()

    if len(response) > 0 :
      return response["items"][0]
    else:
      print "unable to find video by id"
      return 

  except ssl.SSLError:
    print "ssl.SSLError"
    return

def search_list_by_keyword(client, id_cat_dict, cat, id_email, **kwargs):
  # return nextPageToken
  # updates name_id_dict


  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.search().list(
    **kwargs
  ).execute()


  # add this page's query to name_id_dict
  filter_and_append_to_id_dict(response, id_cat_dict, cat, id_email )

  #return
  if "nextPageToken" in response.keys():
    return response["nextPageToken"]

  return None


def filter_and_append_to_id_dict(data, id_cat_dict, cat, id_email):
  # updates name_id_dict
  result_lst = data["items"]

  for item in result_lst:

    # check if description contains the keyword music
    vid_id = item["id"]["videoId"]

    response = videos_list_by_id(client,
      part='snippet',
      id=vid_id)

    if response != None: 

      description = response["snippet"]["description"].lower()
      
      if containsMusic(description) != None :

        channel_id = item["snippet"]["channelId"]

        id_cat_dict[channel_id]= cat

        # check if the video contains email
        id_email[channel_id] += get_emails(description)



def id_to_channel_url(id_str):
  channel_temp = u"https://www.youtube.com/channel/"
  result_str = u""

  url = channel_temp + id_str + u"/about"
  result_str += url
  result_str.encode('utf-8')
  return result_str



def print_dict(dict):
  for key,value in dict.items():
    print key, value



def query_channel(client, **kwargs):
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.channels().list(
    **kwargs
  ).execute()

  return response["items"]



def get_key_data(id_cat_dictionary, id_email):
  """
  Check if the youtubers has >10k <250k followers, if so get all the info 

  input: name_id_dict: a dictionary of all eligible youtubers we get from the youtube video database query
  return: key_data- a list of list
    where each sublist is [name, id, subscriber_count, url, email, category, bio ]
  """

  key_data = []


  for youtuber_id, categoryName in id_cat_dictionary.items():

    response = query_channel(client, part= "snippet, statistics", id = youtuber_id)

    if len(response) > 0:

      response = response[0]

      # Check if the youtubers has >1k followers
      subscribers = int(response["statistics"]["subscriberCount"])

      if (subscribers >= 250 and subscribers <= 10000): # 250 - 10M
        #print "yesss"
        name, bio = response["snippet"]["title"], response["snippet"]["description"]
        url = id_to_channel_url(youtuber_id)
        id_email[youtuber_id] += get_emails(bio.lower())


        email= unique_emails(id_email[youtuber_id])

        youtuber_info=[name, youtuber_id, subscribers, url, email ,categoryName, bio]
        key_data.append(youtuber_info)

  return key_data

def unique_emails(email_str):
  line_break = "\n"
  email_list = list(set(email_str.split("\n")))
  return line_break.join(email_list)


def main():

  id_cat_dict = {}
  id_email = defaultdict(str)

  id_dict_size = 0

  for keyword in test:
      # initialize next page token

      next_page_token=''

      before_cat = id_dict_size

      for i in range(20):

        next_page_token = search_list_by_keyword(client,
          
          id_cat_dict,
          "Music",
          id_email,
          part='snippet',
          maxResults=50,
          pageToken = next_page_token,
          publishedAfter='2017-12-11T00:00:00Z',
          q=keyword,
          type='video',
          videoCategoryId=10)

        new_dict_size = len(id_cat_dict.keys())

        print i, new_dict_size - id_dict_size

        id_dict_size = new_dict_size

      print "TOTAL UNDER THE KEYWORD "+ keyword +" IS "+str(new_dict_size - before_cat)

      print "================="


  #print "after video query:"
  #print_dict(id_cat_dict)

  print "size before testing >250 <10k " + str(len(id_cat_dict.keys()))

  data = get_key_data(id_cat_dict, id_email)

  print "final data size:" + str(len(data))

  write_values('Sheet1!A1100:G', data)






# main program

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification. When
  # running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  client = get_authenticated_service()


  main()





  