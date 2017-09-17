"""
ADD DESCRIPTION
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import urllib2
import urllib
import json
import dateutil.parser

url = "http://a7fcd589.ngrok.io"

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_speechlet_response_with_directive_no_intent():
    return {
        'outputSpeech': None,
        'card': None,
        'reprompt': None,
        "directives" : [ {"type" : "Dialog.Delegate"} ],
        'shouldEndSession': False
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def validate_user(session):
    user = session['user']['userId']
    content = urllib2.urlopen(url + "/profile?user_id="+str(user)).read()
    print(content)


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Horse Bet Manager. " \
                    "You can ask for horse races information, " \
                    "and place bets on upcoming races."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask me what the next race is by saying, " \
                    "what is the next race."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using the Horse Bet Manager. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def get_race_info(intent, session):
    session_attributes = session.get('attributes', {})
    reprompt_text = None
    should_end_session = False

    next_race = json.load(urllib2.urlopen(url + "/next_race"))

    parsed_start = dateutil.parser.parse(next_race['start_time'])
    hour = parsed_start.hour
    minute = parsed_start.minute

    if 1 <= int(minute) <= 10:
        speech_output = "The next race is race number {}. It starts at {} oh {}.".format(next_race['id'],
            hour, minute)
    elif int(minute) == 0:
        speech_output = "The next race is race number {}. It starts at {} oh clock.".format(next_race['id'],
            hour)
    else:
        speech_output = "The next race is race number {}. It starts at {} {}.".format(next_race['id'],
            hour, minute)

    session_attributes["nextRace"] = next_race
    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def get_horse_info(intent, session):
    session_attributes = session.get('attributes', {})
    reprompt_text = None
    should_end_session = False

    race_number = session_attributes["nextRace"]['id']
    horse_response = json.load(urllib2.urlopen(url+"/races/"+str(race_number)+"/horses"))


    speech_output = "For race number {}, the horses are ".format(race_number)

    for horse in horse_response:
        speech_output = speech_output + "number {}. {} with {} odds. ".format(horse['id'],horse['name'],horse['odds'])

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def get_profit_info(intent, session):
    session_attributes = session.get('attributes', {})
    should_end_session = False
    reprompt_text = None
    user = session['user']['userId']
    data = urllib.urlencode({'user_id': user})
    print(data)
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    http_request = urllib2.Request(url + "/profile", data=data)
    http_request.get_method = lambda: 'PUT'
    content = opener.open(http_request).read()
    profit = json.loads(content)["profit"]
    speech_output = "Your profit is {} ether".format(profit)

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def place_bet(request, session):
    session_attributes = session.get('attributes', {})
    should_end_session = False
    intent = request['intent']
    if request['dialogState'] == 'STARTED':
        return build_response(session_attributes,
         build_speechlet_response_with_directive_no_intent())
    if request['dialogState'] != 'COMPLETED':
        return build_response(session_attributes,
         build_speechlet_response_with_directive_no_intent())
    amount = intent['slots']['Amount']['value']
    horse = intent['slots']['Horse']['value']
    race = intent['slots']['Race']['value']
    session_attributes["currentBet"] = {"amount": amount, "horse": horse, "race": race}
    speech_output = "Placing {} ethereum on horse {} and race {}.".format(amount, horse, race)
    reprompt_text = None
    # Store bet in database, or Place bet on the smart contract
    endpoint = url + "/races/"+str(race)+"/bets"
    user = session['user']['userId']
    data = urllib.urlencode({'horse_id': horse, 'user_id': user, 'amount': amount})
    print(endpoint)
    print(data)
    content = urllib2.urlopen(url=endpoint, data=data).read()
    print(content)
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def get_results(intent, session):
    session_attributes = session.get('attributes', {})
    reprompt_text = None
    should_end_session = False

    race_number = intent['slots']['Race']['value']
    races = json.load(urllib2.urlopen(url+"/races"))
    try:
        results = json.load(urllib2.urlopen(url+"/races/"+str(race_number)+"/horses?results=t"))
    except:
        speech_output = "Race {} is not over yet".format(str(race_number))
        return build_response(session_attributes, build_speechlet_response(
            intent['name'], speech_output, reprompt_text, should_end_session))
    speech_output = "The results of race {} are.".format(str(race_number))
    for result in results:
        speech_output = speech_output + " {} came number {}.".format(result['name'],result['finish'])
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    validate_user(session)
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PlaceBetIntent":
        return place_bet(intent_request, session)
    elif intent_name == "RaceInfoIntent":
        return get_race_info(intent, session)
    elif intent_name == "HorseInfoIntent":
        return get_horse_info(intent, session)
    elif intent_name == "WhatResultsIntent":
        return get_results(intent, session)
    elif intent_name == "ProfitIntent":
        return get_profit_info(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
