# TODO: Add an appropriate license to your skill before publishing.  See
# the LICENSE file for more information.

# Below is the list of outside modules you'll be using in your skill.
# They might be built-in to Python, from mycroft-core or from external
# libraries.  If you use an external library, be sure to include it
# in the requirements.txt file so the library is installed properly
# when the skill gets installed later by a user.

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG

# Each skill is contained within its own class, which inherits base methods
# from the MycroftSkill class.  You extend this class as shown below.

class SendSerialPacketSkill(MycroftSkill):

    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(SendSerialPacketSkill, self).__init__(name="SendSerialPacketSkill")
        
        # Initialize working variables used within the skill.
        # PYTHON_NOTE: Arrays do not exist within python, instead a data
        # structure known as a "list" has similar functionality.
        #
        self.payload = []               # Message payload
        self.payload_size = 10          # Size of the payload in bytes
        self.comm_protocol = []         # User-selected communication protocol identifier
        self.port = []                  # User or system selected port to transmit data

        self.sync_bytes = []            # Sync bytes (if necessary)
        self.sync_loop_control = 0

        self.str_to_int = 0              # Variable used to convert string input to integer values

        self.serial_packet = []         # Complete data packet to send

    # The "handle_xxxx_intent" function is triggered by Mycroft when the
    # skill's intent is matched.  The intent is defined by the IntentBuilder()
    # pieces, and is triggered when the user's utterance matches the pattern
    # defined by the keywords.  In this case, the match occurs when one word
    # is found from each of the files:
    #    vocab/en-us/Hello.voc
    #    vocab/en-us/World.voc
    # In this example that means it would match on utterances like:
    #   'Hello world'
    #   'Howdy you great big world'
    #   'Greetings planet earth'

    @intent_handler(IntentBuilder("ProtocolIntent").require("Protocols").require("Format"))
    def handle_select_protocol_intent(self, message):
        if message.data["Format"] == "spi":
            self.comm_protocol = [0,2]
        elif message.data["Format"] == "uart":
            self.comm_protocol = [0,1]
        elif message.data["Format"] == "i squared c":
            self.comm_protocol = [0,3]
        else:
            self.comm_protocol = [0,0]
        self.speak_dialog("selected.protocol", data={"comm_protocol": self.comm_protocol})

    @intent_handler(IntentBuilder("SyncBytesIntent").require("Sync").require("HexNum"))
    def handle_sync_byte_intent(self, message):
        while self.sync_loop_control < 4:
            self.str_to_int = int(message.data["HexNum"],16)
            self.sync_bytes.append(hex(self.str_to_int))
            self.sync_loop_control += 1
            self.speak_dialog("extend.sync", data={"sync_loop_control": self.sync_loop_control})
        self.speak_dialog("complete.sync", data={"sync_bytes": self.sync_bytes})

    # @intent_handler(IntentBuilder("").require("Data").require("Packet"))
    # def handle_serial_intent(self, message):

    #    self.speak_dialog("send.serial.data")
    # The "stop" method defines what Mycroft does when told to stop during
    # the skill's execution. In this case, since the skill's functionality
    # is extremely simple, there is no need to override it.  If you DO
    # need to implement stop, you should return True to indicate you handled
    # it.
    #
    def stop(self):
        return True

# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return SendSerialPacketSkill()
