"""
ADD DESCRIPTION
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function


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


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

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
                    "what is next race."
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

def get_latest_race():
    # CALL ENDPOINT TO RETRIEVE LATEST RACE
    return

def get_race_info(intent, session):
    session_attributes = session.get('attributes', {})
    reprompt_text = None
    should_end_session = False

    latest_race = get_latest_race()
    speech_output = "The next race is race number {}. " \ 
                    "It starts at {} and ends at {}".format(latest_race['race_number'],
                                                            latest_race['start_time'],
                                                            latest_race['end_time'])

    seesion_attributes["latestRace"] = latest_race
    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def get_horse_info(intent, session):
    return

def get_horse_odds(intent, session):
    return

def place_bet(intent, session):
    session_attributes = session.get('attributes', {})
    should_end_session = False
    if 'Amount' not in intent['slots']:
        speech_output = "I'm not sure what amount you are trying to bet. " \
                        "Please try again."
        reprompt_text = "I'm not sure what amount you are trying to bet. " \
                        "You can place a bet by saying, " \ 
                        "Place two ethereum on horse three and race five."
    elif 'Horse' not in intent['slots']:
        speech_output = "I'm not sure what horse you are trying to bet on. " \
                        "Please try again."
        reprompt_text = "I'm not sure what horse you are trying to bet on. " \
                        "You can place a bet by saying, " \ 
                        "Place two ethereum on horse three and race five."
    elif 'Race' not in intent['slots']:
        speech_output = "I'm not sure what race you are trying to bet on. " \
                        "Please try again."
        reprompt_text = "I'm not sure what race you are trying to bet on. " \
                        "You can place a bet by saying, " \ 
                        "Place two ethereum on horse three and race five."
    else:
        amount = intent['slots']['Amount']['value']
        horse = intent['slots']['Horse']['value']
        race = intent['slots']['Race']['value']
        session_attributes["currentBet"] = {"amount": amount, "horse": horse, "race": race}
        speech_output = "Placing {} ethereum on horse {} and race {}."
        reprompt_text = None
        # Store bet in database, or Place bet on the smart contract

        # speech_output = "Are you sure you want to place {} ethereum on horse {} and race {}?"
        # reprompt_text = "Are you sure you want to place {} ethereum on horse {} and race {}? " \
        #                 "Say Yes to confirm."
        # TODO: implement confirmation step for security
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

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PlaceBetIntent":
        return place_bet(intent, session)
    elif intent_name == "RaceInfoIntent":
        return get_race_info(intent, session)
    elif intent_name == "HorseInfoIntent":
        return get_horse_info(intent, session)
    elif intent_name == "HorseOddsIntent":
        return get_horse_odds(intent, session)
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