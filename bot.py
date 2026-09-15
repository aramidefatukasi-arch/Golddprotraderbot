import os
import re
import telebot
from telebot import types

# Load token from environment variable (Railway will inject this)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

bot = telebot.TeleBot(BOT_TOKEN)

# Define the extraction logic
def extract_bid_details(text):
    # Initialize result dictionary
    details = {
        "Requirements": "Not specified",
        "Submission deadline": "Not specified",
        "Required documents": "Not specified",
        "Eligibility criteria": "Not specified",
        "Evaluation criteria": "Not specified",
        "Budget information": "Not specified",
        "Important clauses": "Not specified"
    }
    
    # Keywords to look for (case-insensitive)
    keywords = {
        "Requirements": r"requirements?|specifications?|scope of work",
        "Submission deadline": r"deadline|submission date|due date|closing date",
        "Required documents": r"required documents?|documents required|mandatory documents",
        "Eligibility criteria": r"eligibility|qualification|who can apply",
        "Evaluation criteria": r"evaluation|assessment|scoring|award criteria",
        "Budget information": r"budget|financial|contract value|funding",
        "Important clauses": r"clauses?|terms and conditions|important terms|contract terms"
    }

    # Split text into lines or sentences for easier parsing
    # This is a simple line-by-line approach. A real parser might use NLP.
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for line in lines:
        for key, pattern in keywords.items():
            # Check if keyword is in the line
            if re.search(pattern, line, re.IGNORECASE):
                # If the line starts with the keyword, take the rest as the value
                if re.match(rf"^{pattern}", line, re.IGNORECASE):
                    # Remove the keyword itself from the value
                    value = re.sub(rf"^{pattern}[\s:]*", "", line, flags=re.IGNORECASE).strip()
                    if value:
                        details[key] = value
                # If the line just contains the keyword, the next line might have the value
                elif re.search(pattern, line, re.IGNORECASE) and len(lines) > 1:
                    idx = lines.index(line)
                    if idx + 1 < len(lines):
                        details[key] = lines[idx + 1]
    
    return details

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 *Welcome to Golddprotrader Bot!*\n\n"
        "I can extract key details from bid/tender documents.\n\n"
        "Simply *paste the text* of a document and I will extract:\n"
        "✅ Requirements\n"
        "✅ Submission deadline\n"
        "✅ Required documents\n"
        "✅ Eligibility criteria\n"
        "✅ Evaluation criteria\n"
        "✅ Budget information\n"
        "✅ Important clauses"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_document_text(message):
    user_text = message.text
    
    # Ignore short messages or commands
    if len(user_text) < 50:
        bot.reply_to(message, "Please send a longer document or text for extraction.")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    
    # Extract details
    extracted = extract_bid_details(user_text)
    
    # Format the response
    response = "📄 *Extraction Results:*\n\n"
    for key, value in extracted.items():
        response += f"*{key}:*\n{value}\n\n"
    
    # Telegram has a 4096 character limit
    if len(response) > 4000:
        response = response[:4000] + "...\n[Truncated]"
        
    bot.reply_to(message, response, parse_mode='Markdown')

if __name__ == '__main__':
    print("Bot is starting...")
    bot.infinity_polling()
