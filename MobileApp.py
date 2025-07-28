import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

kivy.require('2.0.0') # Replace with your Kivy version

class FeedbackAppLayout(BoxLayout):
    """
    Main layout for the feedback application.
    Contains input fields for feedback, email, contact number,
    and a spinner for country calling codes.
    """
    feedback_input = ObjectProperty(None)
    email_input = ObjectProperty(None)
    phone_number_input = ObjectProperty(None)
    country_code_spinner = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical' # Arrange widgets vertically
        self.padding = 30 # Add padding around the layout
        self.spacing = 15 # Add spacing between widgets

        # List of common country calling codes
        self.country_codes = [
            "+1 (USA, Canada)", "+44 (United Kingdom)", "+91 (India)",
            "+49 (Germany)", "+33 (France)", "+81 (Japan)", "+86 (China)",
            "+61 (Australia)", "+55 (Brazil)", "+27 (South Africa)",
            "+34 (Spain)", "+39 (Italy)", "+7 (Russia)", "+52 (Mexico)",
            "+62 (Indonesia)", "+63 (Philippines)", "+65 (Singapore)",
            "+66 (Thailand)", "+82 (South Korea)", "+90 (Turkey)",
            "+971 (UAE)", "+20 (Egypt)", "+234 (Nigeria)", "+254 (Kenya)"
        ]

        # --- Title Label ---
        self.add_widget(Label(text="User Feedback Form", font_size='24sp', size_hint_y=None, height=40))

        # --- Feedback Input ---
        self.add_widget(Label(text="Your Feedback:", size_hint_y=None, height=30))
        self.feedback_input = TextInput(hint_text="Enter your feedback here", multiline=True, size_hint_y=None, height=120)
        self.add_widget(self.feedback_input)

        # --- Email Input ---
        self.add_widget(Label(text="Email ID:", size_hint_y=None, height=30))
        self.email_input = TextInput(hint_text="your.email@example.com", input_type='text', size_hint_y=None, height=40)
        self.add_widget(self.email_input)

        # --- Contact Number Section ---
        contact_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        self.add_widget(Label(text="Contact Number:", size_hint_y=None, height=30))

        # Country Code Dropdown
        self.country_code_spinner = Spinner(
            text="+1 (USA, Canada)", # Default value
            values=self.country_codes,
            size_hint=(0.4, 1) # Take 40% of the horizontal space
        )
        contact_layout.add_widget(self.country_code_spinner)

        # Phone Number Input
        self.phone_number_input = TextInput(
            hint_text="e.g., 1234567890",
            input_type='number', # Restrict input to numbers
            size_hint=(0.6, 1) # Take 60% of the horizontal space
        )
        contact_layout.add_widget(self.phone_number_input)
        self.add_widget(contact_layout)


        # --- Submit Button ---
        submit_button = Button(text="Submit Feedback", size_hint_y=None, height=50)
        submit_button.bind(on_press=self.submit_feedback)
        self.add_widget(submit_button)

    def submit_feedback(self, instance):
        """
        Gathers the input data and displays it in a popup.
        In a real application, this data would be sent to a server or saved locally.
        """
        feedback = self.feedback_input.text
        email = self.email_input.text
        country_code = self.country_code_spinner.text
        phone_number = self.phone_number_input.text

        # Basic validation (can be expanded)
        if not feedback or not email or not phone_number:
            self.show_popup("Error", "Please fill in all fields.")
            return

        if "@" not in email or "." not in email:
            self.show_popup("Error", "Please enter a valid email address.")
            return

        # Prepare the submission message
        message = (
            f"Thank you for your feedback!\n\n"
            f"Feedback: {feedback}\n"
            f"Email: {email}\n"
            f"Contact: {country_code} {phone_number}"
        )

        self.show_popup("Feedback Submitted", message)

        # Clear inputs after submission (optional)
        self.feedback_input.text = ""
        self.email_input.text = ""
        self.phone_number_input.text = ""
        self.country_code_spinner.text = "+1 (USA, Canada)" # Reset to default

    def show_popup(self, title, message):
        """
        Displays a simple popup message to the user.
        """
        popup_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_content.add_widget(Label(text=message, halign='center', valign='middle'))
        close_button = Button(text="Close", size_hint_y=None, height=40)
        popup_content.add_widget(close_button)

        popup = Popup(title=title, content=popup_content, size_hint=(0.9, 0.5))
        close_button.bind(on_press=popup.dismiss)
        popup.open()


class FeedbackApp(App):
    """
    The main Kivy application class.
    Builds and returns the root widget for the app.
    """
    def build(self):
        return FeedbackAppLayout()

if __name__ == '__main__':
    FeedbackApp().run()
