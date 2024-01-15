import kivy
import simplepyble
import time
import random
kivy.require('2.2.1') # replace with your current kivy version !
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.config import Config  
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
Window.size = (478, 887)
from datetime import timedelta
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

adapters = 1
adapter = 1
peripherals = 1
peripheral = 1
services = 1
service_uuid = 1
characteristic_uuid = 1
characteristic_uuid_timer = 1
characteristic_uuid_status = 1
displayTime = ""
firstpass = True
popupGO = 1
popupMULTI = 1

player_counter = 1
max_players_per_column = 15
name_container = None
groupname_list = []
group_players_list = []
groupContainer = None
group_index = None
connected = False
turn_index = 0
target_identifier = None
local_timer_list = []

globalTheme = [
    [48/255, 214/255, 230/255, 1],  # Background color
    [136/255, 252/255, 252/255, 1], # Button color
    [0, 0, 0, 1],   # Text color
    [1, 1, 1, 1],   # Text highlight color
    [1, 0, 0, 1]    # Debug color
]

class MainScreen(Screen):
    global globalTheme
    theme = globalTheme
    pass

class PopupScreen(Screen):
    def __init__(self, **kwargs):
        super(PopupScreen, self).__init__(**kwargs)
        self.countdown_label = Label(text="GO", font_size=200)
        self.add_widget(self.countdown_label)

class SinglePlayerScreen(Screen):
    global globalTheme
    theme = globalTheme
    is_size_selected_value = False
    invalid_characters = ['.', '$', '#', '[', ']', '/',";",':',",","?","-",")","(","%","@"]

    def on_pre_enter(self):
        self.ids.size_33cl.active=True

    def on_checkbox_active(self, checkbox, value):
        self.is_size_selected_value = value

    def Validate_Username(self,value):
        username_input = value
        entered_username = username_input.text

        if any(char in entered_username for char in self.invalid_characters):
            username_input.text = ""
            self.show_invalid_username_popup()
            return False
        elif len(entered_username) > 15:
            print("Username cannot be longer than 12 characters")
            username_input.text = ""
            self.show_invalid_username_popup()
            return False
        else:
            print(f"Entered valid username: {entered_username}")
            App.get_running_app().start_timer(self, True)
            return True

    def validate_and_show_popup(self):
        username_input = self.ids.singlePlayerTextInput
        if self.is_size_selected_value and self.Validate_Username(username_input) and username_input.text:
            self.show_popup()
        elif not self.is_size_selected_value:
            self.show_invalid_username_popup()

    def show_popup(self):
        global popupGO
        content = PopupScreen()
        popupGO = Popup(content=content, title="", size_hint=(None, None), size=(400, 400))
        popupGO.open()
    
    def show_invalid_username_popup(self):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text="Invalid username or size not selected!\nPlease enter a valid username and select a size."))

        invalid_username_popup = Popup(content=content, title="", size_hint=(None, None), size=(600, 200))
        invalid_username_popup.open()


class MultiPlayerScreen(Screen):
    global globalTheme
    theme = globalTheme

    def on_pre_enter(self):
        global turn_index
        turn_index = 0
        self.ids.size_33cl.active=True

    def __init__(self, **kwargs):
        super(MultiPlayerScreen, self).__init__(**kwargs)
        self.timer_ids = {}

    def update_group_labels(self, target_identifier, display_time, player_index, buildPass):
        global local_timer_list

        self.ids.multiplayerTitle.text = target_identifier
        
        multiplayerContainer = self.ids.multiplayerContainer

        player_index = 0
        if multiplayerContainer is not None:
            multiplayerContainer.clear_widgets()
            for player_name in groups.get(f"{target_identifier}"):
                player_label = Label(text=f"{player_name}", font_size=40,color=self.highlightText(player_index))
                
                multiplayerContainer.add_widget(player_label)

                if len(local_timer_list) < len(groups.get(f"{target_identifier}")):
                    local_timer_list.append("00:00:00")
                
                self.ids.timer.text = display_time
                local_timer_list[turn_index] = display_time
                
                timer_label = Label(text=f"{local_timer_list[player_index]}", font_size=40,color=self.highlightText(player_index))
                multiplayerContainer.add_widget(timer_label)

                timer_label_id = f"timer{player_index}"
                timer_label.id = timer_label_id
                self.timer_ids[player_index] = timer_label_id
                player_index +=1
        

            print(f"local timer list: {local_timer_list}")
            print(f"current time to print: {display_time}")

    def highlightText(self, player_index):
        if turn_index == player_index:
            return self.theme[3]
        else:
            return self.theme[2]

    def stop_timer(self):
        Clock.unschedule(self.update_timeMp)

    def update_timeMp(self, dt):
        global group_players_list
        global turn_index

        contents = peripheral.read(service_uuid, characteristic_uuid_timer)
        while contents == b'gameStart':
            print("geen data")
            contents = peripheral.read(service_uuid, characteristic_uuid_timer)
            time.sleep(0.1)
        decode_contents = contents.decode('utf-8')
        status = decode_contents.split(';')
        popupMULTI.dismiss()

        contents_str = status[0]
        contents1 = contents_str[-3:].zfill(2)        
        contents2 = contents_str[-5:-3].zfill(2)        
        contents3 = contents_str[-7:-5].zfill(2)        
        display_time = f"{contents3}:{contents2}:{contents1}"        
        print(display_time)
        
        if status[-1] == 'stop timer':
            self.stop_timer()
            print("timer stopped")
            self.update_group_labels(target_identifier, display_time, turn_index, False)
            player_name = groups.get(target_identifier, [])[turn_index]
            App.get_running_app().readyDataForFireBase(self, contents_str, player_name, "MultiPlayer")
            turn_index +=1
            return
        print(f"Contents: {contents}")

        
        player_index = turn_index % len(groups.get(f"{target_identifier}"))
        timer_label_id = self.timer_ids[player_index]

        # Check if the label ID exists before updating
        if timer_label_id in self.ids:
            self.ids[timer_label_id].text = display_time

        if turn_index == len(groups.get(f"{target_identifier}")):
            turn_index = 0

        self.update_group_labels(target_identifier, display_time, turn_index, False)

class ScoreboardScreen(Screen):
    global globalTheme
    theme = globalTheme

    #The scoreboard doesn't automatically refresh
    
    
    def on_pre_enter(self):
        self.ids.defaultCheckbox.active=True

    def checkbox_click(self, instance, value, sizeBottle):
            if value == True:
                self.ids.scoreContainer.clear_widgets()
                self.ids.scoreContainer.add_widget(Label(text=f"Rank :",color=self.theme[2]))
                self.ids.scoreContainer.add_widget(Label(text=f"Name :",color=self.theme[2]))
                self.ids.scoreContainer.add_widget(Label(text=f"Time :",color=self.theme[2]))
 
                player = ''
                ref = db.reference(f'{sizeBottle}cl')
                sorted_data = ref.order_by_child('score').get()
                amountOfPlayers = 0
                for player, values in sorted_data.items():
                    score = str(values['score'])
                    contents1 = score[-3:].zfill(2)
                    contents2 = score[-5:-3].zfill(2)
                    contents3 = score[-7:-5].zfill(2)
                    score = f"{contents3}:{contents2}:{contents1}"
                    size = f'{sizeBottle}cl'
                    player = f'{player}'
                    separator = ';'
                    player = player.split(separator, 1)[0]
                    amountOfPlayers = amountOfPlayers + 1
                    self.ids.scoreContainer.add_widget(Label(text=f"{amountOfPlayers}",color=self.theme[2]))
                    self.ids.scoreContainer.add_widget(Label(text=f"{player}",color=self.theme[2]))
                    self.ids.scoreContainer.add_widget(Label(text=f"{score}",color=self.theme[2]))
                    if amountOfPlayers >= 100:
                        break

class SettingsScreen(Screen):
    global globalTheme
    theme = globalTheme


    regularTheme = [
    [48/255, 214/255, 230/255, 1],  # Background color
    [136/255, 252/255, 252/255, 1],  # Button color
    [0, 0, 0, 1]  # Text color
    ]
    darkTheme = [
    [0/255, 0/255, 0/255, 1],  # Background color
    [100/255, 100/255, 100/255, 1],  # Button color
    [1, 1, 1, 1]  # Text color
    ]

    def on_pre_enter(self):
        self.ids.defaultThemeCheckbox.active=True

    def checkbox_click(self, instance, value, selectedTheme):
            global globalTheme
            if value == True:
                if selectedTheme == "Regular":
                    globalTheme = self.regularTheme
                if selectedTheme == "Dark":
                    globalTheme = self.darkTheme
            Builder.unload_file('filename.kv')
            Builder.load_file('HMIApp2.kv')

class GroupScreen(Screen):
    global globalTheme
    theme = globalTheme
    def __init__(self, **kwargs):
        super(GroupScreen, self).__init__(**kwargs)

    def update_group_buttons(self):
        global groupContainer
        groupContainer = self.ids.groupContainer


        # Check if groupContainer exists before clearing it
        if groupContainer is not None:
            groupContainer.clear_widgets()
        
        
        ref = db.reference(f'groups')
        global groups
        groups = ref.get()
        print(groups)
        print(f"Length of database groups = {len(groups)}")


        for group_name in groups:
            group_button = Button(text=group_name, size_hint=(.60, .05), font_size=40, on_press=self.on_group_button_press,color=self.theme[2],background_color= (self.theme[1]),background_normal= '')
            groupContainer.add_widget(group_button)
            

    def on_pre_enter(self):
        self.update_group_buttons()

    def on_group_button_press(self, instance):
        # Handle the button press, you can define the behavior you want here
        global group_index
        global target_identifier
        global local_timer_list
        global turn_index
        turn_index = 0
        local_timer_list = []
        target_identifier = instance.text
        print(f"Button {instance.text} pressed")
        screen_manager = self.manager  # Access the ScreenManager
        self.manager.get_screen("MultiPlayer").update_group_labels(target_identifier, "00:00:00", 0, True)
        if 'MultiPlayer' in screen_manager.screen_names:
            screen_manager.current = 'MultiPlayer'

class MakeGroupScreen(Screen):
    global globalTheme
    theme = globalTheme
    invalid_characters = ['.', '$', '#', '[', ']', '/', ";", ':', ",", "?", "-", ")", "(", "%", "@"]
    def __init__(self, **kwargs):
        super(MakeGroupScreen, self).__init__(**kwargs)
        self.player_names = []  # List to store player names
        self.player_timer = []
        self.player_count = 1 
        
    def Validate_Username2(self, value):
        username_input = value
        entered_username = username_input.text

        if any(char in entered_username for char in self.invalid_characters):
            username_input.text = ""
            self.show_invalid_username_popup()
            return False
        elif len(entered_username) > 15:
            print("Username cannot be longer than 15 characters")
            username_input.text = ""
            self.show_invalid_username_popup()
            return False
        else:
            print(f"Entered valid username: {entered_username}")
            return True

    def validate_and_show_popup2(self):
     username_input = self.ids.username_input 
     if self.Validate_Username2(username_input) and username_input.text:
        self.show_popup()
     else:
        self.show_invalid_username_popup()

    def show_invalid_username_popup(self):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text="Invalid username or size not selected!\nPlease enter a valid username and select a size."))

        invalid_username_popup = Popup(content=content, title="", size_hint=(None, None), size=(600, 200))
        invalid_username_popup.open()

    def add_player(self, player_name):
        global player_counter
        global name_container

        if not self.Validate_Username2(self.ids.username_input):
            return

        # Create the GridLayout if it doesn't exist
        if name_container is None:
            name_container = self.ids.nameContainer

        # Create a new Label for the player
        player_label = Label(text=f"{player_counter}: {player_name}", font_size=40, color=self.theme[2])

        # Add the Label to the GridLayout
        name_container.add_widget(player_label)

        self.player_names.append(player_name)
        self.player_timer.append("00:00:00")

        # Increment the player counter
        player_counter += 1

        # Check if the maximum number of players per column is reached
        if player_counter % (max_players_per_column + 1) == 0:
            # If reached, create a new column
            name_container.cols += 1
        # Clear the TextInput after adding the player
        self.ids.username_input.text = ""

    def sendGroupDataToFirebase(self, instance, groupname):
        playerNames = self.player_names.copy()
        ref = db.reference(f'groups')
        ref.child(f'{groupname}').set(playerNames)
    
    def add_group(self, groupname):

        self.ids.nameContainer.clear_widgets()
        global player_counter
        player_counter = 1
        self.ids.nameContainer.cols = 1

        self.sendGroupDataToFirebase(self, groupname)
        

        self.manager.get_screen("GroupScreen").update_group_buttons()
class ScreenManager(ScreenManager):
    pass

kv = Builder.load_file('HMIApp2.kv')

class MyPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(136/255, 252/255, 252/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class DakansnellerApp(App):
    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        return kv

    def on_request_close(self, *args):
        print("Kivy app closed by user input")
        self.disconnect()

    # Fetch the service account key JSON file contents
    cred = credentials.Certificate('biersnorkel-895a0-firebase-adminsdk-fuktx-f8f7290d19.json')
    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
    'databaseURL': "https://biersnorkel-895a0-default-rtdb.europe-west1.firebasedatabase.app/"
    })
    
    def sendDataToFirebase(self, userName, size, timeAsInt):
        ref = db.reference(f'{size}cl')
        data = {'score': timeAsInt}
        ref.child(f'{userName};{random.randint(1, 100000)}').set(data)

    def readyDataForFireBase(self, instance, rawDataFromESP_str, userName, currentScreen):
        timeAsInt = int(rawDataFromESP_str)

        checkboxes = [
            self.root.get_screen(f"{currentScreen}").ids.size_25cl,
            self.root.get_screen(f"{currentScreen}").ids.size_33cl,
            self.root.get_screen(f"{currentScreen}").ids.size_50cl,
            self.root.get_screen(f"{currentScreen}").ids.size_100cl
        ]

        selected_size = None
        for checkbox in checkboxes:
            if checkbox.active:
                selected_size = checkbox.text
                break

        self.sendDataToFirebase(userName, selected_size, timeAsInt)

    def popup_to_connect(self, button_text):
        if connected == False:
            label = Label(text='No device connected', font_size=25)
            def connectToESP(instance):
                self.connectESP(instance)
            def update_label_text(instance):
                label.text = 'Connecting...'
                Clock.schedule_once(connectToESP, 0.1)
            popup_content = BoxLayout(orientation='vertical')
            button = Button(text='CONNECT TO DEVICE', on_press=update_label_text,)
            popup_content.add_widget(label)
            popup_content.add_widget(button)



            # button.bind(on_press=update_label_text)

            popup = Popup(title='', content=popup_content, size_hint=(None, None), size=(400, 400))
            # popup.bind(on_dismiss=self.on_popup_dismiss)
            popup.open()

    def start_timer(self, x, single):
        # Access the timer label by its id and update its text property 
        enableTimer = "gameStart"
        peripheral.write_request(service_uuid, characteristic_uuid_timer, str.encode(enableTimer))
        if single == True:
            Clock.schedule_interval(self.update_time, 0.05)
        if single == False:
            global popupMULTI
            content = PopupScreen()
            popupMULTI = Popup(content=content, title="", size_hint=(None, None), size=(400, 400))
            popupMULTI.open()
            Clock.schedule_interval(self.root.get_screen('MultiPlayer').update_timeMp, 0.05)
        # Write the content to the characteristic

    def stop_timer(self):         # Cancel the scheduled updates when the timer stops        
        Clock.unschedule(self.update_time)

    def update_time(self, dt):         # This function will be called every 0.05 seconds
        contents = peripheral.read(service_uuid, characteristic_uuid_timer)
        while contents == b'gameStart':
            print("geen data")
            contents = peripheral.read(service_uuid, characteristic_uuid_timer)
            time.sleep(0.1)
        decode_contents = contents.decode('utf-8')
        status = decode_contents.split(';')
        popupGO.dismiss()

        contents_str = status[0]
        contents1 = contents_str[-3:].zfill(2)
        contents2 = contents_str[-5:-3].zfill(2)
        contents3 = contents_str[-7:-5].zfill(2)
        display_time = f"{contents3}:{contents2}:{contents1}"
        print(display_time)

        if status[-1] == 'stop timer':
            self.stop_timer()
            print("timer stopped")
            self.root.get_screen("SinglePlayer").ids.timer.text = display_time
            userName = self.root.get_screen("SinglePlayer").ids.singlePlayerTextInput.text
            self.readyDataForFireBase(self, contents_str, userName, "SinglePlayer")
            return
        print(f"Contents: {contents}")
        self.root.get_screen("SinglePlayer").ids.timer.text = display_time

    def disconnect(self):
        global service_uuid
        global characteristic_uuid_timer
        global peripheral
        global connected
        global firstpass
        print("BLE disconnected by user request")
        message = "DISCONNECT"
        peripheral.write_request(service_uuid, characteristic_uuid_timer, str.encode(message))
        connected = False
        firstpass = True


    def connectESP(self, instance):
        global firstpass
        if firstpass:
            firstpass = False
            global service_uuid
            global characteristic_uuid_timer
            global characteristic_uuid_status
            global characteristic_uuid
            global adapters
            global adapter
            global peripherals
            global peripheral
            global services
            global connected
            adapters = simplepyble.Adapter.get_adapters()

            if len(adapters) == 0:
                print("No adapters found")

            # Query the user to pick an adapter
            adapter_list = []
            for i, adapter in enumerate(adapters):
                print(f"{i}: {adapter.identifier()} [{adapter.address()}]")

            adapter = adapters[0]


            adapter.set_callback_on_scan_start(lambda: print("Scan started."))
            adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))
            adapter.set_callback_on_scan_found(lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]"))

            # Scan for 5 seconds
            adapter.scan_for(5000)
            peripherals = adapter.scan_get_results()

            target_identifier = 'ESP32 Sensor'
            esp_index = next((i for i, p in enumerate(peripherals) if target_identifier in p.identifier()), None)

            # Query the user to pick a peripheral
            print("Please select a peripheral:")
            for i, peripheral in enumerate(peripherals):
                print(f"{i}: {peripheral.identifier()} [{peripheral.address()}]")

            if esp_index is not None:
                print(f"Index of ESP32 Sensor: {esp_index}")
            else:
                print("ESP32 Sensor not found in the list.")
                print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")

            peripheral = peripherals[esp_index]
            print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")

            peripheral.connect()
            services = peripheral.services()
            service_characteristic_pair = []
            for service in services:
                for characteristic in service.characteristics():
                    service_characteristic_pair.append((service.uuid(), characteristic.uuid()))

            service_uuid, characteristic_uuid_timer = service_characteristic_pair[4]
            print("Connected")
            connected = True

if __name__ == '__main__':
    DakansnellerApp().run()


        
