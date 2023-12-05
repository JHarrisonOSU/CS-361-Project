import zmq
import cryptocode

"""
Setup the ZMQ socket
"""

context = zmq.Context()  # Create context object to store sockets
socket = context.socket(zmq.REP)  # Create a socket of type REP (Reply)
socket.bind("tcp://*:5555")  # Bind the socket to all interfaces on port '5555'


def encode(str_to_encode, key_str):
    encoded_str = cryptocode.encrypt(str_to_encode, key_str)
    return encoded_str


def decode(str_to_encode, key_str):
    decoded_str = cryptocode.decrypt(str_to_encode, key_str)
    return decoded_str


# Listen for requests
while True:
    # Store incoming message (this also pauses the loop)
    request_tuple = socket.recv_pyobj()
    data_str, key, command = request_tuple  # Unpack the tuple

    # Process the data based on the value of 'command'
    """
    If command is encode:
        Call your encode and send the result string
    
    If command is decode:
        Call your decode and send the resultant string
        
    Else:
        socket.send_string('Error: Invalid command.')       
    """
    if command == "encode":
        print("\nreceived string to encode: ", data_str)
        res_string = encode(data_str, key)
        print("sending encoded string: ", res_string)
        socket.send_string(res_string)
    elif command == "decode":
        print("\nreceived string to decode: ", data_str, "with key", key)
        res_string = decode(data_str, key)
        print("sending decoded string: ", res_string)
        socket.send_string(res_string)
    else:
        socket.send_string("\nError: Invalid command.")

    # Clear all the variables for safety
    request_tuple = None
    data_str = None
    key = None
    command = None
