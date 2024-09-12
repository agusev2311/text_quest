## README

### Telegram Bot: Text-Based Adventure Quest

This project is a Python-based Telegram bot that runs interactive text-based quests. Players can make decisions by selecting from provided options, which affect the progression of the story. The bot interacts with an external language model to generate dynamic content for each quest.

### Features
- Interactive text quests with multiple choice options.
- Integration with a language model API (YandexGPT-lite) for dynamic quest generation.
- Rate limiting (requests per hour) to prevent abuse.
- Threaded request queue to handle multiple users efficiently.
- SQLite database for logging user interactions.

### Requirements
- Python 3.x
- `requests` library for making API calls.
- `pyTelegramBotAPI` (`telebot`) for Telegram bot interaction.
- `sqlite3` for storing request history.
  
### Installation
1. Clone the repository:
    ```bash
    git clone git@github.com:agusev2311/text_quest.git
    cd text_quest
    ```
   
2. Install required dependencies:
    ```bash
    pip install requests, pyTelegramBotAPI
    ```
    Ensure `telebot` and `requests` are installed.

3. Set up the configuration:
    - Copy `config.example` to `config`:
        ```bash
        cp config.example config
        ```
    - Edit the `config` file and add your keys:
        - `secret_key`: API key for Yandex language model.
        - `ac_id`: Your account ID for the Yandex model.
        - `max_tokens`: Maximum tokens for each API request.
        - `telegram_token`: Your Telegram bot token.
        - `max_requests_per_hour`: Limit for how many requests each user can make per hour.

### Usage
1. Start the bot:
    ```bash
    python main.py
    ```
2. Interact with the bot on Telegram by sending `/start` to initiate the quest. Use `/start_quest <topic>` to begin a specific quest.

3. Players will be presented with multiple choices in the form of buttons. Their choices will affect how the story unfolds.

### Rate Limiting
The bot tracks each user's requests to ensure they do not exceed a defined limit (`max_requests_per_hour`). If the limit is reached, the bot will notify the user and prevent further requests for the hour.

### Request Queue
Requests are processed in a queue to handle multiple users simultaneously. If the bot is busy, new requests are added to the queue, and users are notified of their position.

### Database
User interactions are logged in an SQLite database (`requests.db`) to keep track of messages and responses. This log can help analyze usage patterns and debug issues.

### License
This project is open-source and licensed under the MIT License.

### Support
For issues or questions, contact @agusev2311 on Telegram.
