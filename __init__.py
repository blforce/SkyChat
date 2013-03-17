from tkinter import *
import sys
from FriendsList import *

# Create the root window
root = Tk()
fList = FriendsList(root)


def onClose():
    """Callback function used to logout the client whenever the main
    window is closed."""

    print("logging out")
    fList.logout()

    print("destroying window")
    root.destroy()

    print("exiting")
    sys.exit()

root.protocol("WM_DELETE_WINDOW", onClose)
root.mainloop()
