# Chick-fil-A Promo Bot

This Python app uses Selenium to track LAFC game results and notifies the user if LAFC wins at home (triggering a Chick-fil-A reward).

## Features
- Web scraping with Selenium
- Email alert system with Gmail
- Smart logic to avoid duplicate notifications
- Kickoff time parsing to delay checks until 3 hours post-game

## Setup

### 1. Install dependencies
```bash
pip install selenium python-dotenv
```
### 2. Create .env file
```
EMAIL_ADDRESS=yourbot@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENT=youremail@example.com
```
### 3. Run the bot
```
python main.py
```
## Upcoming 
- Clippers and Ducks integration
- Discord/text alerts
- Logging and dashboard view
