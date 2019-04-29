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
import serial

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
        self.payload = ''               # Message payload
        self.payload_size = 10          # Size of the payload in bytes
        self.payload_loop_control = 0
        self.comm_protocol = ''         # User-selected communication protocol identifier
        self.port = '01'                  # User or system selected port to transmit data

        self.sync_bytes = ''            # Sync bytes (if necessary)
        self.sync_loop_control = 0

        self.str_to_int = 0              # Variable used to convert string input to integer values

        self.serial_packet = []         # Complete data packet to send
        self.ser = serial.Serial()

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
            self.comm_protocol = '02'
        elif message.data["Format"] == "uart":
            self.comm_protocol = '01'
        elif message.data["Format"] == "i squared c":
            self.comm_protocol = '03'
        else:
            self.comm_protocol = '00'
        self.speak_dialog("selected.protocol", data={"comm_protocol": self.comm_protocol})

    @intent_handler(IntentBuilder("SyncBytesIntent").require("Sync").require("HexNum"))
    def handle_sync_byte_intent(self, message):
        if self.sync_loop_control < 4:
            self.str_to_int = int(message.data["HexNum"],16)
            if self.str_to_int > 9:
                self.speak_dialog("nibble.prompt")
            else:
                self.sync_loop_control += 1
                self.sync_bytes = self.sync_bytes + hex(self.str_to_int).lstrip("0x")
            self.speak_dialog("extend.sync", data={"sync_loop_control": self.sync_loop_control})
        self.speak_dialog("complete.sync", data={"sync_bytes": self.sync_bytes})
    
    @intent_handler(IntentBuilder("PortSelectIntent").require("PortName"))
    def handle_port_select_intent(self, message):
        self.ser.baudrate = 9600
        self.ser.port = 'COM1'
        self.speak_dialog("port.config", data={"port_name": self.ser.name})

    @intent_handler(IntentBuilder("PayloadConfigIntent").require("Payload").require("HexByte"))
    def handle_payload_select_intent(self, message):
        self.str_to_int = 0
        if self.payload_loop_control < self.payload_size:
            self.payload_loop_control += 1
            self.str_to_int = int(message.data["HexByte"],16)
            self.payload = self.payload + hex(self.str_to_int).lstrip("0x")
            self.speak_dialog("extend.payload", data={"payload_loop_control": self.payload_loop_control})
        self.speak_dialog("complete.payload", data={"payload": self.payload})
    
    @intent_handler(IntentBuilder("BuildSerialPacketIntent").require("BuildSerial"))
    def handle_build_serial_packet_intent(self, message):
        self.serial_packet.append(self.sync_bytes)
        self.serial_packet.append(self.comm_protocol)
        self.serial_packet.append(self.port)
        self.serial_packet.append(self.payload)

        self.serial_packet = bytearray(self.serial_packet,'utf-8')
        self.ser.open()
        self.ser.write(self.serial_packet)
        self.speak_dialog("send.serial.data")
        self.ser.close()

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
