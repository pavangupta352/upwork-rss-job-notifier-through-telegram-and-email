from telegram.error import TelegramError, NetworkError
import html
import re
import feedparser
import asyncio
from telegram import Bot
import feedparser
import smtplib
from email.mime.text import MIMEText
import time
import os

# Upwork RSS Feed URL
rss_url = 'your rss url'

# Telegram Bot Configuration
bot_token = 'your_bot_token'
chat_id = 'your_chat_id'
bot = Bot(token=bot_token)

# File to store seen job postings
seen_posts_file = 'seen_posts.txt'


async def send_telegram_message(text):
    max_length = 4096
    max_retries = 3  # Max number of retries for sending messages

    for start in range(0, len(text), max_length):
        end = start + max_length
        chunk = text[start:end]

        for attempt in range(max_retries):
            try:
                await bot.send_message(chat_id=chat_id, text=chunk)
                break  # Message sent successfully, break the retry loop
            except (TelegramError, NetworkError) as e:
                if attempt < max_retries - 1:
                    # Wait for 5 seconds before retrying
                    await asyncio.sleep(5)
                else:
                    print(
                        f"Failed to send message after {max_retries} attempts. Error: {e}")


def read_seen_posts():
    """Reads the IDs of seen posts from a file."""
    if not os.path.exists(seen_posts_file):
        return set()
    with open(seen_posts_file, 'r') as file:
        return set(file.read().splitlines())


def write_seen_post(post_id):
    """Writes a new seen post ID to the file."""
    with open(seen_posts_file, 'a') as file:
        file.write(post_id + '\n')


def format_job_details(post):
    """Formats job details for the Telegram message."""
    # Unescape HTML entities
    unescaped_description = html.unescape(post.description)

    # Remove HTML tags
    clean_description = re.sub(r'<[^>]+>', '', unescaped_description)

    return f"New Job Posting: {post.title}\nLink: {post.link}\nDescription:\n{clean_description}"


async def check_new_posts(url, seen_posts):
    """Checks for new job postings in the RSS feed."""
    feed = feedparser.parse(url)
    for post in feed.entries:
        if post.id not in seen_posts:
            seen_posts.add(post.id)
            write_seen_post(post.id)
            message_body = format_job_details(post)
            await send_telegram_message(message_body)


async def main():
    """Main function to run the check repeatedly."""
    while True:
        seen_posts = read_seen_posts()
        await check_new_posts(rss_url, seen_posts)
        await asyncio.sleep(60)  # Wait for 1 minute before checking again

if __name__ == "__main__":
    asyncio.run(main())
