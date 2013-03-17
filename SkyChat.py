# -*- coding: utf-8 *-*

"""
Class Name: Client
	This class handles finding, and connecting to,
	all other chat clients on the network.
	
Data:
	__peers 				- Keeps track of all peers currently on the network.
	__myInfo				- The current user's information to be sent to other clients
	__broadcastPort			- Port that all broadcast messages will be sent and received on
	__messagePort			- Port that all connections with other clients will be established on
	__newPeer				- Callback function to be used when a new peer has been found
	
Accessor Functions:
	getPeers				- Returns the list of known peers
	
Functions:
	
	__init__				- Constructor
	
	Input Params:
		contactInfo			- Information about this client's user
		newPeer				- Function to be called when a new peer is found on the network
		
	Output Params: 			- None
	
	Save contactInfo and newPeer
	
	Create a thread to listen for TCP connection requests
	
	Create a thread to listen for UDP broadcasts
	
	Send UDP broadcast to let other clients know about this one.
	
	
	
	
	__connectionListener	- Listens on __messagePort for new connection requests
	
	Input Params:			- None
	Output Params:			- None
	
	Create a TCP socket and bind it to the port number in __messagePort
	
	while true:
		wait for a connection request and accept it
		
		add the new connection to the matching contact in __peers
		
		
	__alertBroadcast		- Sends a UDP message to the given address to let them know about this client
	
	Input Params:
		addr				- Address to send the message to. Default is the special '<broadcast>' address
	Output Params:			- None
	
	Create a new UDP socket
	
	Send contact information for this client on the UDP socket.
	
	
	
	__alertListener			- Listens for UDP notifications of new clients
	
	Input Params:			- None
	Output Params:			- None
	
	Create a UDP socket bound to __broadcastPort
	
	while true:
		listen for data on the port
		
		when data is received parse the contact information from it
		
		if data is not from this client:
			if data is from a new contact:
				add new contact to the __peers list
				send contact information back to the new contact
				call the __newPeer callback function
				
				
				
				
Class Name: Contact
	This class represents a peer client on the network
	
Data:
	__messagePort			- Port that all connections with other clients will be established on
	__connection			- Socket that all communications will be made through
	__thrListen				- Thread that will be used to listen for incoming messages
	__msgCallback			- Callback function that will be used when a new message is received from this contact
	__status				- This contact's current status
	__name					- Display name for this contact
	
Mutator Functions:
	setMessageCallback		- Sets the callback function to be used when a new message is received
	setConnection			- Sets the socket to listen for new connections on and starts a thread to listen to it
	
Accessor Functions:
	getName					- Returns the display name
	getStatus				- Returns this contact's current status
	getData					- Returns an xml representation of this contact
	
Functions:

	__init__				- Constructor
	
	Input Params:
		name				- Display name for this contact
		status				- This contact's current status
		
	Output Params:			- None
	
	Save status and name
	
	
	
	sendMessage				- Sends a message to this client
	
	Input Params:
		message				- The message to be sent
		
	If a connection has not been established:
		create a new connection
		call setConnection with the new connection
		
	send message on TCP connection
	
	
	
	
	__listen				- Listens for new messages on a TCP connection
	
	while true:
		Listen for a message and get it when available
		
		if message is empty:
			close the connection
			return
			
		call messageCallback with the received message
	
"""

__author__ = "Benjamin Force"
__email__ = "benforce@gmail.com"
__version__ = 1.0

import threading
import socket
import xml.etree.ElementTree as etree
from uuid import getnode
import select
import sys


broadcastPort = 8497
messagePort = 42111


class Client:

    __peers = []
    __myInfo = None
    __newPeer = None
    __deletePeer = None
    __online = True

    def __init__(self, contactInfo, newPeer, newConversation, deletePeer):

        self.__myInfo = contactInfo
        self.__newPeer = newPeer
        self.__newConversation = newConversation
        self.__deletePeer = deletePeer

        # Start TCP connection listener thread
        self.__connectionThread = \
        threading.Thread(target=self.__connectionListener)

        self.__connectionThread.start()

        # Start UDP listener thread
        self.__listenThread = threading.Thread(target=self.__alertListener)
        self.__listenThread.start()

        # Send UDP broadcast lettting other clients know that the
        # user has connected
        self.__alertBroadcast()

    def getPeers(self):
        """Gets a list of all connected peers."""
        return self.__peers

    def logout(self):
        """Send an alert to let everyone know that this client is offline."""

        print("Sending logout message.")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

        sock.sendto(self.__logoutCommand(),
        ('<broadcast>', broadcastPort))

        self.__online = False

    def __logoutCommand(self):
        """Returns a string that will be broadcast to let other clients
        know that this user is now offline."""
        return str('<control sender="' +
            str(self.__myInfo.getMAC()) +
            '" command="logout" />').encode()

    def __connectionListener(self):
        """Listens on the protocol port for connection requests."""
        self.__connectionSocket = socket.socket(socket.AF_INET,
        socket.SOCK_STREAM)

        self.__connectionSocket.setsockopt(socket.SOL_SOCKET,
        socket.SO_REUSEADDR, True)

        self.__connectionSocket.bind(('', messagePort))
        self.__connectionSocket.listen(5)

        while self.__online:
            newSock, (addr, port) = self.__connectionSocket.accept()

            print("New connection from", addr)

            # Find the contact that sent the request and give it the
            # connection
            for p in self.__peers:

                if(p.getAddress() == addr):
                    self.__newConversation(p)
                    p.setConnection(newSock)

    def __alertBroadcast(self, addr='<broadcast>'):
        """Send an alert to let everyone know that this client is online."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

        sock.sendto(self.__myInfo.getData(),
        (addr, broadcastPort))

    def __alertListener(self):
        """Listen for UDP broadcasts."""

        # Setup the socket to listen for connections.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock.bind(('', broadcastPort))
        except socket.error:
            print("Only one client per system allowed!")
            sys.exit()

        while self.__online:
            newContact, (addr, port) = sock.recvfrom(1024)

            print("New broadcast received:", newContact.decode())
            if "<Contact" in newContact.decode():
                newContact = ParseContact(newContact)
                newContact.setAddress(addr)

                # Ignore this instance's own broadcast
                if(newContact.getMAC() != self.__myInfo.getMAC()):

                    # Make sure this is a new contact
                    isNewContact = True
                    for p in self.__peers:
                        if(p.getMAC() == newContact.getMAC()):
                            isNewContact = False
                            break

                    if(isNewContact is True):
                        self.__peers.append(newContact)

                        # Send our contact info back
                        self.__alertBroadcast(newContact.getAddress())

                        # Use the callback to handle the new contact
                        self.__newPeer(newContact)

            elif "<control" in newContact.decode():

                index = -1
                root = etree.fromstring(newContact.decode())
                mac = int(root.get("sender"))
                print("Contact logging off:", str(mac))
                for pIndex in range(0, len(self.__peers)):
                    if mac == self.__peers[pIndex].getMAC():
                        print("Found contact")
                        index = pIndex
                        break

                if index == -1:
                    return

                self.__peers.pop(index)
                self.__deletePeer(index)


def ParseContact(data):
    """Parse encoded data into a new instance of the contact class."""
    root = etree.fromstring(data.decode())
    return Contact(name=root.get("Name"), status=root.get("Status"), mac=int(root.get("MAC")))


class Contact:

    __mac = None
    __connection = None
    __thrListen = None
    __msgCallback = None
    __status = "Offline"
    __name = "Unknown"
    __history = []
    __address = None

    def __init__(self, name="Unknown", status="Online", mac=None):

        self.__status = status
        self.__name = name

        if(mac is None):
            self.__mac = getnode()
        else:
            self.__mac = mac

    def getData(self):
        root = etree.Element("Contact", attrib={
            "Name": self.__name,
            "Status": self.__status,
            "MAC": str(self.__mac)})

        return etree.tostring(root)

    def setMessageCallback(self, callback):
        self.__msgCallback = callback

        # send the entire message history
        for msg in self.__history:
            self.__msgCallback(msg)

    def setConnection(self, connection):
        """Set the connection to listen to."""
        print("Setting contact connection.")
        # If a connection is already open, then keep it
        if(self.__connection is not None):
            return

        self.__connection = connection

        self.__thrListen = threading.Thread(target=self.__listen)
        self.__thrListen.start()

    def setAddress(self, value):
        self.__address = value

    def getAddress(self):
        return self.__address

    def getMAC(self):
        return self.__mac

    def getName(self):
        return self.__name

    def sendMessage(self, message):
        # If no connection is availble, open one
        if(self.__connection is None):
            newConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newConnection.connect((self.__address, messagePort))
            self.setConnection(newConnection)

        print("Sending message: ", message)
        self.__connection.send(message.encode())

    def __listen(self):

        while not (self.__connection is None):
            # Wait for data to be available
            try:
                rlist, wlist, elist = select.select(
                    [self.__connection],
                    [],
                    [self.__connection],
                    5)

            except:
                break

            # A message is available
            if(len(rlist) > 0):
                try:
                    buff = self.__connection.recv(1024)

                    if (len(buff.strip()) == 0) or (buff == '<close />'):
                        self.__msgCallback("<close />")
                        break

                    print(self.__name + ": " + buff.decode())
                    self.__history.append(buff.decode())
                    if not (self.__msgCallback is None):
                        self.__msgCallback(self.__history[-1])

                except socket.error as ex:
                    print("An error occured.", ex)
                    break

            if(len(elist) > 0):
                break

        print("clearing socket")
        self.closeConnection()
        self.__connection = None

    def closeConnection(self):
        print("closeConnection")

        if not (self.__connection is None):
            print("closing socket")
            self.__connection.close()

        print("clearing message callback")
        self.__msgCallback = None
