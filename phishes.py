import os
import time
import re
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# phishes's user ID in Slack: value assigned after bot starts
phishes_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
START_COMMAND = "hello"

MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns none.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == phishes_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (in the beginning) in message message text and
        returns the user ID which was mentioned. If there is no direct mention, returns none.
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if command is known or gives help suggestions
    """
    # default response is help text for the user
    default_response = "Not sure what you mean. Start with a 'hello'!".format(START_COMMAND)

    # finds and executes the given command, filling in response
    response = None

    # IMPLEMENT MORE COMMANDS HERE
    if command.startswith(START_COMMAND):
        response = "Hello! Meet Phiona by Phishes. Phiona will train, inform, and warn you of the potential security risks while using Slack."

    # sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel = channel,
        text = response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state = False):
        print("Phishes is connected and running")
        # read bot's user ID by calling Web API method 'auth.test'
        phishes_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            # determines if event contains command
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                # determines what to do with command
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed")