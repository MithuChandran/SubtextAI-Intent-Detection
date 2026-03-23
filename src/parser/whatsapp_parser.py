import re
import pandas as pd
from datetime import datetime
import emoji

class WhatsAppParser:
    def __init__(self):
        # Android: 12/01/2024, 10:30 - User: Message
        self.android_pattern = re.compile(r'^(\d{2}/\d{2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s(.*?):\s(.*)$')
        
        # iOS: [12/01/2024, 10:30:00] User: Message
        self.ios_pattern = re.compile(r'^\[(\d{2}/\d{2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2})\]\s(.*?):\s(.*)$')

    def extract_emojis(self, text):
        """Extract all emojis from text into a single string"""
        return "".join(c for c in text if emoji.is_emoji(c))

    def parse_file(self, file_path):
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_entry = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try matching Android
            match = self.android_pattern.match(line)
            if match:
                if current_entry:
                    # Extract emojis before saving
                    current_entry['emoji'] = self.extract_emojis(current_entry['message'])
                    data.append(current_entry)
                date, time, sender, message = match.groups()
                current_entry = {
                    'timestamp': f"{date} {time}",
                    'sender': sender,
                    'message': message,
                    'platform': 'android'
                }
                continue

            # Try matching iOS
            match = self.ios_pattern.match(line)
            if match:
                if current_entry:
                    current_entry['emoji'] = self.extract_emojis(current_entry['message'])
                    data.append(current_entry)
                date, time, sender, message = match.groups()
                current_entry = {
                    'timestamp': f"{date} {time}",
                    'sender': sender,
                    'message': message,
                    'platform': 'ios'
                }
                continue

            # Multiline continuation
            if current_entry:
                current_entry['message'] += f"\n{line}"

        if current_entry:
            current_entry['emoji'] = self.extract_emojis(current_entry['message'])
            data.append(current_entry)

        return pd.DataFrame(data)

if __name__ == "__main__":
    # Test execution
    parser = WhatsAppParser()
    test_text = "Hello world! 😊😡"
    print(f"Test Extraction: {parser.extract_emojis(test_text)}")
