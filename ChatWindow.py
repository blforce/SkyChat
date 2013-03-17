
"""
Class Name: ChatWindow
	This class allows the user to interact with another client
	on the network.

Mutator Functions:
	setContact		- Sets the contact this window communicates with.
Accessor Functions:
	getContact 		- Gets the contact this window communicates with.
	getIsOpen		- Gets a boolean value indicating if this window is still open.
Functions:
	sendMessage		- Sends the user's message and resets the entry field.
	Input Params	- None
	Output Params	- None
	
	send message to other client
	add message to history view
	clear message entry field
	
	messageCallback	- Receives a message from the remote client.
	Input Params
		message		- The received message
	Output Params	- None
	
	If this message is to close the conversation
		add this event to the history view
	else
		add user message to history view
	
"""

from tkinter import *
from SkyChat import *


class ChatWindow(Toplevel):

	__contact = None
    __newContact = None
    __isOpen = True

    def __init__(self, contact, user):
        Toplevel.__init__(self)

        self.user = user

        self.initUI()

        self.protocol("WM_DELETE_WINDOW", self.__onClose)

        self.setContact(contact)
        self.__setContact()

    def getContact(self):
        return self.__contact

    def setContact(self, contact):
        self.__newContact = contact


    def __setContact(self):

        if not (self.__newContact is None):
            self.__contact = self.__newContact
            self.__newContact = None

            self.title("SkyChat - " + self.__contact.getName())
            self.txtChatHistory.delete("1.0", END)

            self.__contact.setMessageCallback(self.messageCallback)

        self.after(1000, self.__setContact)



    def initUI(self):
        self.title("SkyChat")
        self.geometry("400x400+100+100")

        # Setup grid options
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        # Add a scrollbar for the history view
        self.scrollChatHistory = Scrollbar(self, orient=VERTICAL)
        self.scrollChatHistory.grid(column=2, row=0, sticky=(N, S))


        # Create the history view
        self.txtChatHistory = Text(self, yscrollcommand=self.scrollChatHistory.set)
        self.txtChatHistory.grid(
            column=0,
            row=0,
            columnspan=2,
            sticky=(N, E, S, W))

        self.scrollChatHistory.config(command=self.txtChatHistory.yview)

        # Create the new message entry field
        self.txtMessage = Entry(self)
        self.txtMessage.grid(column=0, row=1, sticky=(W, E))
		
		# Send a message when the user presses Return
        self.txtMessage.bind('<Return>', self.__txtMessage_OnReturn)

        # Create the send message button
        self.btnSend = Button(self, text="Send", command=self.sendMessage)
        self.btnSend.grid(column=1, row=1, columnspan=2, sticky=(N, S))

        # Create the status bar
        self.lblStatus = Label(self, text="Ready.", bd=1, relief=SUNKEN, anchor=W)
        self.lblStatus.grid(column=0, row=2, sticky=(E, W), columnspan=3)

        self.createMenu()

        # Set the focus to the message entry field
        self.txtMessage.focus_set()

        self.__createFormatTags()


    def __createFormatTags(self):
		"""Create format tags for the conversation history."""
		
        self.txtChatHistory.tag_config("sender", font=('calibri', 11, 'bold'))
        self.txtChatHistory.tag_config("message_body", font=('calibri', 11), wrap=WORD)

    def __txtMessage_OnReturn(self, args):
        self.sendMessage()

    def __onClose(self):
        """When the window is closing, let the other client know."""
		
        self.__isOpen = False
        self.__contact.closeConnection()
        self.destroy()

    def getIsOpen(self):
        return self.__isOpen

    def sendMessage(self):
		"""Send a message to the other client."""
		
        msg = self.txtMessage.get()
        self.txtMessage.delete(0, END)
        self.__contact.sendMessage(msg)
		
		"""Add the sent message to the conversation history"""
        self.txtChatHistory.insert(
            END,
            self.user.getName() + ":  ",
            "sender")
        self.txtChatHistory.insert(
            END,
            msg + "\n",
            "message_body")

    def messageCallback(self, message):
		"""Handles messages received from the other client"""
        if message == '<close />':
            self.txtChatHistory.insert(
                END,
                self.__contact.getName() + " has left the chat.\n")
        else:
            self.txtChatHistory.insert(
                END,
                self.__contact.getName() + ":  ",
                "sender")
            self.txtChatHistory.insert(
                END,
                message + "\n",
                "message_body")

    def createMenu(self):
        self.mnuBar = Menu(self)
        self.config(menu=self.mnuBar)

        self.mnuFile = Menu(self.mnuBar)
        self.mnuFile.add_command(label="Exit", command=self.mnuFileExit_Click)
        self.mnuBar.add_cascade(label="File", menu=self.mnuFile)

    def mnuFileExit_Click(self):
        self.destroy()

