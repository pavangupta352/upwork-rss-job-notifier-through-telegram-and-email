import feedparser
import smtplib
from email.mime.text import MIMEText
import time
import os
from telegram import Bot


# Upwork RSS Feed URL
rss_url = 'your rss url'

# Email Details
sender_email = "mailersystem1234@gmail.com"
sender_password = "wojotzfhjveplbce"
receiver_email = "pavan.gupta.352@gmail.com"

# File to store seen job postings
seen_posts_file = 'seen_posts.txt'


def send_email(subject, body):
    """Sends an email with the given subject and body."""
    msg = MIMEText(body, 'html')  #
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()


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
    """Formats job details for the email body."""
    description = post.description.replace(
        '<br />', '\n')  # Replace HTML line breaks with new lines
    email_body = f"""
    <strong>Title:</strong> {post.title}<br>
    <strong>Link:</strong> <a href="{post.link}">{post.link}</a><br>
    <strong>Description:</strong><br>
    <p>{description}</p>
    """
    return email_body


def check_new_posts(url, seen_posts):
    """Checks for new job postings in the RSS feed."""
    feed = feedparser.parse(url)
    for post in feed.entries:
        if post.id not in seen_posts:
            seen_posts.add(post.id)
            write_seen_post(post.id)
            email_body = format_job_details(post)
            send_email(f"New Job Posting: {post.title}", email_body)


while True:
    seen_posts = read_seen_posts()
    check_new_posts(rss_url, seen_posts)
    time.sleep(60)  # Wait for 1 minute before checking again
