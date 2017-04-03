import os
import time
from slackclient import SlackClient


# starterbot's ID as an environment variable
BOT_ID = "U4LBC0EJX"

# constants
AT_BOT = "<@" + BOT_ID + ">"
ENCODE = "encode"
DECODE = "decode"
TELEGRAM = 'C4L8VHVL3'

# instantiate Slack & Twilio clients
slack_client = SlackClient('xoxb-156386014643-xF3CiORsVzhnkgoNxCrjf2WP')

TABLE = {'A': '.-',     'B': '-...',   'C': '-.-.',
        'D': '-..',    'E': '.',      'F': '..-.',
        'G': '--.',    'H': '....',   'I': '..',
        'J': '.---',   'K': '-.-',    'L': '.-..',
        'M': '--',     'N': '-.',     'O': '---',
        'P': '.--.',   'Q': '--.-',   'R': '.-.',
        'S': '...',    'T': '-',      'U': '..-',
        'V': '...-',   'W': '.--',    'X': '-..-',
        'Y': '-.--',   'Z': '--..',
        '0': '-----',  '1': '.----',  '2': '..---',
        '3': '...--',  '4': '....-',  '5': '.....',
        '6': '-....',  '7': '--...',  '8': '---..',
        '9': '----.', ' ': '/', '.' : '.-.-.-',
        ',' : '--..--', ':' : '---...', '?' : '..--..',
	"'" : '.----.', '-' : '-....-', '/' : '-..-.',
   	'@' : '.--.-.', '=' : '-...-'
        }

def encode(message):

	message = (message.replace("encode ", "", 1)).upper()
        encodedMessage = ""
	
	for char in message[:]:
		if char in TABLE:
			encodedMessage += TABLE[char] + " "

        return "`" + encodedMessage + "`"

def decode(message):
	
	message = message.replace("decode ", "", 1)
        decodedMessage = ""
	results = message.split(' ')

	for x in range(len(results)):	
		for alpha, code in TABLE.items():
			if code == results[x]:
				decodedMessage += alpha
	
	if len(decodedMessage) > 0:
        	return "`" + (decodedMessage.lower()) + "`"
	else:
		return "`Try giving me something I can decode!`"

def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    sent = 0
    response = "Not sure what you mean...\n"\
		"Use the *" + ENCODE + "* <phrase> command to encode a phrase\n"\
		"Use the *" + DECODE + "* <phrase> command to decode a phrase\n"\
		"To make your message secret to this room, DM me the command!"
    
    if command.startswith(ENCODE):
        response = "From " + user + " " + encode(command)
	slack_client.api_call("chat.postMessage", channel=TELEGRAM,
                          text=response, as_user=True)
	sent = 1
    elif command.startswith(DECODE):
        response = decode(command)
	slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
	sent = 1

    if sent is not 1:
	slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], output['user']
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
		person = slack_client.api_call("users.info", user=user)
		name = person['user']['name']
                handle_command(command, channel, name)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
