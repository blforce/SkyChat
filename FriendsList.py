

from tkinter import *
from tkinter import ttk
import tkinter.simpledialog as simpledialog
import SkyChat
import ChatWindow


class FriendsList(ttk.Frame):

    __client = None
    __contact = None
    __chatWindows = []
    __newConvQueue = []
    __offlineContactQueue = []

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
        self.initUI()
        self.parent.withdraw()
        userName = simpledialog.askstring("Login", "Username")

        self.parent.update()
        self.parent.deiconify()

        self.__contact = SkyChat.Contact(name=userName)

        self.__checkConversationQueue()

        self.__client = SkyChat.Client(
            self.__contact,
            self.newPeer,
            self.__newConversation,
            self.removePeer)

    def logout(self):
        self.__client.logout()

    def initUI(self):
        """Create the friends list user interface."""

        # Setup the main window
        self.parent.title("SkyChat")
        self.parent.geometry("200x400+100+100")
        self.pack(fill=BOTH, expand=1)

        # Create a scrollbar
        self.scrollFriends = Scrollbar(self, orient=VERTICAL)

        # Create the contact list
        self.lstFriends = Listbox(
            self,
            selectmode=EXTENDED,
            yscrollcommand=self.scrollFriends.set)

        self.lstFriends.pack(side=LEFT, fill=BOTH, expand=1)

        # Open a chat window when the user double-clicks on a list item
        self.lstFriends.bind('<Double-Button-1>', self.__openWindow)

        # Setup the friends list scrollbar
        self.scrollFriends.config(command=self.lstFriends.yview)
        self.scrollFriends.pack(side=RIGHT, fill=Y)

        # Add a menu
        self.createMenu()

    def createMenu(self):
        """Create a basic menu for the friends list window"""
        self.mnuBar = Menu(self.parent)
        self.parent.config(menu=self.mnuBar)

        self.mnuFile = Menu(self.mnuBar)
        self.mnuFile.add_command(label="Exit", command=self.mnuFileExit_Click)
        self.mnuBar.add_cascade(label="File", menu=self.mnuFile)


    def __checkConversationQueue(self):
        """Open a conversation windonw from the main UI thread."""
        if len(self.__newConvQueue) > 0:
            print("Queue item available")
            peer = self.__newConvQueue.pop()
            wndChat = None

            # If a window is already open for this contact, attatch the
            # connection to that window
            for wnd in self.__chatWindows:
                if (wnd.getContact().getMAC() == peer.getMAC()):
                    if wnd.getIsOpen():
                        wndChat = wnd
                        wnd.setContact(peer)
                    else:
                        self.__chatWindows.remove(wnd)
                    break

            # Open a new window if needed
            if wndChat is None:
                wndChat = ChatWindow.ChatWindow(
                    contact=peer,
                    user=self.__contact)

                self.__chatWindows.append(wndChat)

        # Check for new requests every 500 miliseconds
        self.parent.after(500, self.__checkConversationQueue)

    def newPeer(self, peer):
        """Callback function that is used whenever a new peer is discovered
        by the client."""

        print("Found new peer", peer.getName())
        self.lstFriends.insert(0, peer.getName())

    def removePeer(self, index):
        """Removes a peer from the friends list when they log out."""
        print("Removing peer", str(index))
        self.lstFriends.delete(index)

    def __newConversation(self, peer):
        """Queue the creation of a new conversation window."""
        print("New conversation with", peer.getName())
        self.__newConvQueue.append(peer)

    def __openWindow(self, args):
        """Callback function to create a new conversation window."""
        self.__newConversation(
            self.__client.getPeers()[int(self.lstFriends.curselection()[0])])

    def mnuFileExit_Click(self):
        """Let the user exit"""
        self.parent.destroy()



