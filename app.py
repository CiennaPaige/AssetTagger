#importing libraries 
import os #to run commands on operating system 
from tkinter import * #imports all modules from Tkinter library 
import tkinter as tk #GUI (graphical user interface) library 
from tkinter import ttk #imports tkinter style module
import requests #library to run API requests

#importing API keys from afile 
from afile import uvalue, pvalue



#TODO: switch to actual ServiceNow call
# Sets the request parameters (URL)
url = 'https://YOURSERVICENOWACCOUNT.service-now.com' #origional URL removed for security 

# pulls username and password from afile
user = uvalue
pwd = pvalue 

# Sets proper headers
headers = {"Content-Type":"application/json","Accept":"application/json"}

#sets title font
LFONT = ("Veranda", 20)

class MainFrame(tk.Tk):
    """main frame object holding all of the different pages and 
    controller of pages : setting up the ID and functions"""

    def __init__(self, *args, **kwargs):
        """function to initalize class object"""
        tk.Tk.__init__(self, *args, **kwargs)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        #initializing an empty array
        self.frames = {}

        #iterating through a tuple of different pages. If a new page is added, make sure to add it to the tuple here.
        for F in (DataPage, SuccessPage, FailPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            
            self.frames[page_name] = frame
        
            frame.grid(row=0, column=0, sticky=
            'nsew')

        self.show_frame("DataPage") #DataPage will be the first page my application shows
        
    def show_frame(self, page_name):
        """function to show pages"""
        
        frame = self.frames[page_name]
        frame.tkraise()


class LoginPage(tk.Frame):
    """setting up page to login. Not currently being used but can be added later for user authentication"""

    def __init__(self, parent, controller):
        """initalizing class object"""
        tk.Frame.__init__(self, parent)
        frame = tk.Frame(self)
        self.controller = controller

        #creates username label and entry
        uname = StringVar()
        uname_label = Label(self, text='Username', font=('bold', 14), padx=60, pady=30)
        uname_label.grid(row=1, column=0) #grid determines placement of items within page
        uname_entry= Entry(self, textvariable=uname)
        uname_entry.grid(row=1, column=2) 

        #creates password label and entry; password is hidden with '*' characters
        p_word = StringVar()
        pword_label = Label(self, text='Password', font=('bold', 14), pady=40)
        pword_label.grid(row=2, column=0)
        pword_entry= Entry(self, show= '*', textvariable=p_word)
        pword_entry.grid(row=2, column=2)

        #creates button to login 
        login_btn = Button(self, text="Login", width=12, bg='#4a7abc', 
        command= lambda: self.login(controller, uname.get(), p_word.get()))
        login_btn.grid(row=3, column= 1)
    

    def login(self, controller, uname, p_word):
    #function to validate login info

        login_label = Label (self, text="Logging you in...")
        login_label.grid(row= 4, column = 1)
        uname = uname.casefold() #username case does not matter
        
        #try allows computer to attempt to login, but if an error occurs, it does the except function 
        try: 

            if uname == "dummyusername" and p_word == "dummypassword": #hardcoded username and password. will likely be updated if authentication feature implemented 

                controller.show_frame("DataPage")
                app.geometry('500x350')
            
            else: 
                app.geometry('600x350')
                wrong_label = Label (self, text="Username or Password is invalid")
                wrong_label.grid(row= 4, column = 1)
                
        
        except: 
            controller.show_frame("FailPage")


class DataPage(tk.Frame):
    """setting up page to enter asset tag"""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        #using OS library to retrieve serial number
        output = os.popen('cmd /c "wmic bios get serialnumber| find /v "SerialNumber""').read()

        num = output.strip('\n') #allows num to only contain the serial number and no spaces

        #displays serial number on page
        serial_label = Label(self, text='SerialNumber', font=('bold', 14), 
        padx=50, pady=30)
        serial_label.grid(row=0, column=0)
        serial_num = Label(self, text=num, font=('bold', 14))
        serial_num.grid(row=0, column=2)

        #displays entry for asset tag
        asset_tag = StringVar()
        asset_label = Label(self, text='Asset Tag', font=('bold', 14), pady=40)
        asset_label.grid(row=2, column=0)
        asset_entry= Entry(self, textvariable=asset_tag)
        asset_entry.grid(row=2, column=2)

        #creates button to submit asset tag to ServiceNow
        submit_btn = Button(self, text="send", width=12, bg='#4a7abc', 
        command= lambda: self.send_tag(controller, num, asset_tag.get()))
        submit_btn.grid(row=3, column= 1)
    

    def send_tag(self, controller, num, asset_tag):
        """function that sends asset tag, serial number, vendor, and model to Service Now.
        May be modified later to pull more info from device and push it to ServiceNow"""

        sending_label = Label (self, text="sending data to ServiceNow...(do not close)")
        sending_label.grid(row= 4, column = 1)
        
        try: 

            #retrieving computer model 
            omodel = os.popen('cmd /c "wmic csproduct get name| find /v "Name""').read()

            #retrieving computer manufacturer 
            oman = os.popen('cmd /c "wmic csproduct get vendor| find /v "Vendor""').read()

            man = oman.strip('\n')
            model = omodel.strip('\n')

            #organizes data to be sent to ServiceNow. This is what would be motified if we wanted to send more data to ServiceNow.
            data= {"asset_tag": asset_tag, "serial_number": num, "u_axonius_model": model, "manufacturer": man} 

            response = requests.post(url, auth=(user, pwd), headers=headers, json=data)

            # Prints success code of code is 201
            # might need to modify to allow for code 200 too, though this hasn't been an issue thus far
            if response.status_code != 201: 
                print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
                exit()

            # Decodes the JSON response into a dictionary and allows us to print the data. This gives us confirmation as to what was sent to ServiceNow
            data = response.json()
            print(data)

            controller.show_frame("SuccessPage")
        
        except: 
            # only shows fail page if sending data was unsuccessful
            controller.show_frame("FailPage")


class SuccessPage(tk.Frame):
    """class to notify user if asset tag was sent to ServiceNow Successfully"""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        success_label = ttk.Label(self, text="Success! \n", font = LFONT)
        success_label.pack()  

        close_label = ttk.Label(self, text="You may close the app \n", font = LFONT)
        
        close_label.pack() #positions label in center of screen 

class FailPage(tk.Frame):
    def __init__(self, parent, controller):
        """class to notify user if asset tag could not be sent to ServiceNow"""

        tk.Frame.__init__(self, parent)

        self.controller = controller

        fail_label = ttk.Label(self, text="Something went wrong \n", font = LFONT)
        fail_label.pack()  


        close_label = ttk.Label(self, text="Restart the app \n", font = LFONT)
        close_label.pack() 


#creates window object 
app = MainFrame()

#entitles popup "Asset Tagger"
app.title('Asset Tagger')

#sets up app icon
icon = PhotoImage(file='barcode.png')
app.iconphoto(True, icon)

#manages the initial size of the window. Change this to resize window.
app.geometry('500x350')

app.mainloop() #starts program
