import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from datetime import datetime

# --- 1. Mock User Data ---
# In a real app, this would be a secure database.
MOCK_USERS = {
    "user123": {
        "password": "password123",
        "full_name": "Alex Johnson",
        "balance": 150750.50,
        "transactions": [
            ("2025-08-01", "Salary Deposit", 75000.00),
            ("2025-08-01", "Rent Payment", -25000.00),
            ("2025-08-02", "Grocery Store", -4500.75),
            ("2025-08-03", "Online Shopping", -8000.25),
        ]
    }
}

# --- 2. Application Screens ---

class LoginScreen(Screen):
    """Screen for user login."""
    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # App Title
        title = Label(text='Kerala Digital Bank', font_size='32sp', bold=True, color=(0.1, 0.4, 0.7, 1))
        
        # Input fields
        self.username_input = TextInput(hint_text='Username', multiline=False, size_hint_y=None, height=40)
        self.password_input = TextInput(hint_text='Password', password=True, multiline=False, size_hint_y=None, height=40)
        
        # Login Button
        login_button = Button(text='Login', size_hint_y=None, height=50, background_color=(0.1, 0.6, 0.3, 1))
        login_button.bind(on_press=self.login)
        
        # Error message label
        self.error_label = Label(text='', color=(1, 0, 0, 1))
        
        layout.add_widget(title)
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(login_button)
        layout.add_widget(self.error_label)
        
        self.add_widget(layout)

    def login(self, instance):
        """Validates user credentials."""
        username = self.username_input.text
        password = self.password_input.text
        
        if username in MOCK_USERS and MOCK_USERS[username]['password'] == password:
            self.error_label.text = ''
            # Pass user data to the dashboard screen
            self.manager.current = 'dashboard'
            self.manager.get_screen('dashboard').load_user_data(MOCK_USERS[username])
        else:
            self.error_label.text = 'Invalid username or password.'

class DashboardScreen(Screen):
    """Screen for displaying account details after login."""
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        self.user_data = {}
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        self.welcome_label = Label(text='', font_size='24sp', bold=True)
        self.balance_label = Label(text='', font_size='40sp', color=(0.1, 0.6, 0.3, 1))
        
        download_button = Button(text='Download Account Statement', size_hint_y=None, height=50)
        download_button.bind(on_press=self.download_statement)
        
        logout_button = Button(text='Logout', size_hint_y=None, height=50, background_color=(0.8, 0.2, 0.2, 1))
        logout_button.bind(on_press=self.logout)
        
        layout.add_widget(self.welcome_label)
        layout.add_widget(Label(text='Current Balance:', font_size='20sp'))
        layout.add_widget(self.balance_label)
        layout.add_widget(download_button)
        layout.add_widget(logout_button)
        
        self.add_widget(layout)
        
    def load_user_data(self, user_data):
        """Loads and displays the logged-in user's data."""
        self.user_data = user_data
        self.welcome_label.text = f"Welcome, {self.user_data['full_name']}"
        self.balance_label.text = f"₹{self.user_data['balance']:,.2f}"

    def download_statement(self, instance):
        """Generates a text file with transaction history."""
        filename = f"statement_{datetime.now().strftime('%Y%m%d')}.txt"
        
        # Use encoding='utf-8' to support special characters like the Rupee symbol
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("--- Kerala Digital Bank Account Statement ---\n\n")
            f.write(f"Account Holder: {self.user_data['full_name']}\n")
            f.write(f"Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("-" * 40 + "\n")
            f.write(f"{'Date':<12} {'Description':<20} {'Amount (₹)':>15}\n")
            f.write("-" * 40 + "\n")
            for tx in self.user_data['transactions']:
                f.write(f"{tx[0]:<12} {tx[1]:<20} {tx[2]:>15,.2f}\n")
            f.write("-" * 40 + "\n")
            f.write(f"{'Current Balance:':<33} {self.user_data['balance']:>15,.2f}\n")

        # Show a confirmation popup
        popup_layout = BoxLayout(orientation='vertical', padding=10)
        popup_layout.add_widget(Label(text=f"Statement saved as:\n{os.path.abspath(filename)}"))
        close_button = Button(text='Close', size_hint_y=None, height=40)
        popup_layout.add_widget(close_button)
        
        popup = Popup(title='Download Successful', content=popup_layout, size_hint=(0.8, 0.4))
        close_button.bind(on_press=popup.dismiss)
        popup.open()
        
    def logout(self, instance):
        """Logs the user out and returns to the login screen."""
        self.manager.current = 'login'
        self.manager.get_screen('login').username_input.text = ""
        self.manager.get_screen('login').password_input.text = ""


# --- 3. Main App Class ---

class MobileBankingApp(App):
    def build(self):
        """Builds the app with a screen manager."""
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

# --- 4. Run the App ---
if __name__ == '__main__':
    MobileBankingApp().run()