from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time 
import pyttsx3
import playsound
import speech_recognition as sr
import pytz
import subprocess


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
DAY_EXTENSIONS = ["nd", "rd", "th", "st"]

def speak(text):
	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()

def get_audio():
	r = sr.Recognizer()
	with sr.Microphone() as source:
		audio = r.listen(source)
		said = ""

		try:
			said = r.recognize_google(audio)
			print(said)
		except Exception as e:
			print("Exception: " + str(e))

	return said.lower()		


def authenticate_google():

	creds = None

	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)

	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)

		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('calendar', 'v3', credentials=creds)

	return service

def get_events(day, service):    

	date = datetime.datetime.combine(day, datetime.datetime.min.time())
	end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
	utc = pytz.UTC
	date = date.astimezone(utc)
	end_date = end_date.astimezone(utc)

	events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(), singleEvents=True, orderBy='startTime').execute()
	events = events_result.get('items', [])

	if not events:
		print('No upcoming events found.')
	else:
		speak(f"You have {len(events)} events on this day.")	

		for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))
			print(start, event['summary'])
			start_time = str(start.split("T")[1].split("-")[0])
			if int(start_time.split(":")[0]) < 12:
				start_time = start_time + "am"
			else:
				start_time = str(int(start_time.split(":")[0])-12) + start_time.split(":")[1]
				start_time = start_time + "pm"	

			speak(event["summary"] + " at " + start_time)

