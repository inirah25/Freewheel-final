import os
import pandas as pd
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import time
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from django.conf import settings
import django 
 
load_dotenv()
 
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
MANAGER_EMAIL = os.getenv("MANAGER_EMAIL")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")  # Adjust this to your project name
 
EXCEL_PATH = os.path.join(settings.MEDIA_ROOT, 'Submitted_Shift_End.xlsx')
IST = pytz.timezone('Asia/Kolkata')
 
SHIFT_END_TIMES = {
    "S1": "15:54",
    "G":  "12:19",
    "S2": "14:47",
    "S3": "23:54",
    "S4": "01:04",
    "S6": "07:00"
}
 
scheduler_started = False  # Flag to prevent multiple scheduler startups
 
def send_html_email(subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = MANAGER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()

    try:
        import socket
        addr_info = socket.getaddrinfo("smtp.gmail.com", 587, socket.AF_INET)
        ip_address = addr_info[0][4][0]

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print("Email sent successfully via IPv4")
    except Exception as e:
        print(f"Error sending email: {e}")


 
def process_shift(shift_code):
 
    try:
 
        df = pd.read_excel(EXCEL_PATH)
 
        if df.empty:
 
            print(f"[{shift_code}] Excel is empty. Skipping.")
 
            return
 
        df.columns = [col.strip() for col in df.columns]
 
        # Find the 'Ticket Status' column
 
        status_col = None
 
        for col in df.columns:
 
            if "ticket" in col.lower() and "status" in col.lower():
 
                status_col = col
 
                break
 
        if not status_col:
 
            print(f"[{shift_code}] No 'Ticket Status' column found.")
 
            return
 
        # Count ticket statuses
 
        status_counts = df[status_col].astype(str).str.strip().str.lower().value_counts()
 
        open_count = status_counts.get('open', 0)
 
        pending_count = status_counts.get('pending', 0)
 
        solved_count = status_counts.get('solved', 0) + status_counts.get('sloved', 0)
 
        hold_count = status_counts.get('hold', 0)
 
        total = open_count + pending_count + solved_count + hold_count
 
        # Create Ticket Summary Table (HTML)
 
        ticket_summary_html = f"""
<h3>Ticket Summary</h3>
<table style="border-collapse: collapse; width: 60%; font-family: Arial, sans-serif;">
<thead>
<tr style="background-color: #f2f2f2; color: #333;">
<th style="border: 1px solid #ddd; padding: 8px;">Status</th>
<th style="border: 1px solid #ddd; padding: 8px;">Open</th>
<th style="border: 1px solid #ddd; padding: 8px;">Pending</th>
<th style="border: 1px solid #ddd; padding: 8px;">Solved</th>
<th style="border: 1px solid #ddd; padding: 8px;">Hold</th>
<th style="border: 1px solid #ddd; padding: 8px;">Total Tickets</th>
</tr>
</thead>
<tbody>
<tr style="background-color: #ffffff; color: #000;">
<td style="border: 1px solid #ddd; padding: 8px;">Ticket Count</td>
<td style="border: 1px solid #ddd; padding: 8px;">{open_count}</td>
<td style="border: 1px solid #ddd; padding: 8px;">{pending_count}</td>
<td style="border: 1px solid #ddd; padding: 8px;">{solved_count}</td>
<td style="border: 1px solid #ddd; padding: 8px;">{hold_count}</td>
<td style="border: 1px solid #ddd; padding: 8px;">{total}</td>
</tr>
</tbody>
</table>
 
        """
 
        # Style the full Excel data as an HTML table
 
        styled_df_html = df.to_html(index=False, border=0, classes="data-table")
 
        styled_df_html = styled_df_html.replace(
 
            "<table border=\"0\" class=\"data-table\">",
 
            "<table style=\"border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;\">"
 
        ).replace(
 
            "<th>", "<th style='border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;'>"
 
        ).replace(
 
            "<td>", "<td style='border: 1px solid #ddd; padding: 8px;'>"
 
        )
 
        full_table_html = f"""
<h3>Shift Report - Full Details</h3>
 
        {styled_df_html}
 
        """
 
        today_str = datetime.now(IST).strftime('%d-%m-%Y')
 
        subject = f"Shift {shift_code} Report - {today_str}"
 
        body = (
 
            f"<p>Please find below the full report for shift <strong>{shift_code}</strong>.</p>"
 
            f"{ticket_summary_html}<br><br>{full_table_html}"
 
        )
 
        send_html_email(subject, body)
 
        print(f"[{shift_code}] Email sent with full Excel content in body.")
 
        # Clear Excel
 
        df.iloc[0:0].to_excel(EXCEL_PATH, index=False)
 
        print(f"[{shift_code}] Excel cleared.")
 
    except Exception as e:
 
        print(f"Error in processing shift {shift_code}: {e}")
 
 
def schedule_jobs():
    scheduler = BackgroundScheduler(timezone=IST)
 
    for shift_code, time_str in SHIFT_END_TIMES.items():
        hour, minute = map(int, time_str.split(":"))
 
        scheduler.add_job(
            process_shift,
            'cron',
            hour=hour,
            minute=minute,
            args=[shift_code],
            id=f"{shift_code}_job"
        )
 
    scheduler.start()
    print("Scheduler started.")
 
def start_scheduler_once():
    global scheduler_started
    if not scheduler_started:
        schedule_jobs()
        scheduler_started = True