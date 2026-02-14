#!/usr/bin/env python3
"""Send newsletter via Gmail SMTP."""

import argparse
import json
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

CONFIG_PATH = Path.home() / ".ai-digest-config.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(f"Error: Config not found at {CONFIG_PATH}", file=sys.stderr)
        print('Create it with: {"gmail_address": "...", "gmail_app_password": "..."}', file=sys.stderr)
        sys.exit(1)
    return json.loads(CONFIG_PATH.read_text())


def send_newsletter(to_email: str, subject: str, markdown_path: str):
    config = load_config()
    gmail_addr = config["gmail_address"]
    gmail_pass = config["gmail_app_password"]

    with open(markdown_path) as f:
        content = f.read()

    msg = MIMEMultipart("alternative")
    msg["From"] = gmail_addr
    msg["To"] = to_email
    msg["Subject"] = subject

    # Plain text version
    msg.attach(MIMEText(content, "plain", "utf-8"))

    # Simple HTML conversion (headings, bold, links, bullets)
    html = markdown_to_html(content)
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_addr, gmail_pass)
        server.sendmail(gmail_addr, to_email, msg.as_string())

    print(f"Newsletter sent to {to_email}")


def markdown_to_html(md: str) -> str:
    """Minimal markdown to HTML conversion."""
    lines = md.split("\n")
    html_lines = ['<div style="font-family: -apple-system, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px;">']

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("### "):
            html_lines.append(f'<h3 style="color: #333;">{stripped[4:]}</h3>')
        elif stripped.startswith("## "):
            html_lines.append(f'<h2 style="color: #222; border-bottom: 1px solid #eee; padding-bottom: 8px;">{stripped[3:]}</h2>')
        elif stripped.startswith("# "):
            html_lines.append(f'<h1 style="color: #111;">{stripped[2:]}</h1>')
        elif stripped == "---":
            html_lines.append('<hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;">')
        elif stripped.startswith("- "):
            text = process_inline(stripped[2:])
            html_lines.append(f'<li style="margin: 4px 0;">{text}</li>')
        elif stripped:
            text = process_inline(stripped)
            html_lines.append(f'<p style="color: #444; line-height: 1.6;">{text}</p>')

    html_lines.append("</div>")
    return "\n".join(html_lines)


def process_inline(text: str) -> str:
    """Handle **bold**, [text](url) links."""
    import re
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Links
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2" style="color: #0066cc;">\1</a>', text)
    return text


def main():
    parser = argparse.ArgumentParser(description="Send newsletter via email")
    parser.add_argument("--to", required=True, help="Recipient email")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--file", required=True, help="Path to markdown newsletter")
    args = parser.parse_args()

    send_newsletter(args.to, args.subject, args.file)


if __name__ == "__main__":
    main()
