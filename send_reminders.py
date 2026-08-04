import os
from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client
import resend

# 1. Load credentials from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not RESEND_API_KEY:
    print("❌ Missing environment credentials. Exiting script.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
resend.api_key = RESEND_API_KEY

# 2. Get current time & date specifically in Perth, WA (AWST = UTC+8)
perth_tz = ZoneInfo("Australia/Perth")
now_perth = datetime.now(perth_tz)

current_hour_str = now_perth.strftime("%H:00")
today_str = now_perth.strftime("%Y-%m-%d")

print(f"⏰ Running reminder check for Perth Time: {current_hour_str}, Date: {today_str}")

# 3. Query user_settings for users who want emails at THIS Perth hour
try:
    res_settings = supabase.table("user_settings") \
        .select("*") \
        .eq("email_reminders", True) \
        .eq("reminder_time", current_hour_str) \
        .execute()
    
    users_due = res_settings.data if res_settings.data else []
    print(f"👥 Found {len(users_due)} user(s) scheduled for {current_hour_str} AWST.")

    for setting in users_due:
        email = setting["user_name"]
        
        # 4. Check if the user has ALREADY logged a session today (Perth date)
        res_logs = supabase.table("daily_logs") \
            .select("id") \
            .eq("user_name", email) \
            .eq("log_date", today_str) \
            .execute()
        
        has_logged_today = len(res_logs.data) > 0 if res_logs.data else False
        
        if not has_logged_today:
            print(f"📧 User {email} has NOT logged today ({today_str}). Sending reminder...")
            
            # 5. Dispatch the email via Resend
            params = {
                "from": "Quran Tracker <onboarding@resend.dev>",
                "to": [email],
                "subject": "📖 Protect your streak! Log today's revision",
                "html": f"""
                <div style="font-family: sans-serif; background-color: #022c22; color: #ffffff; padding: 30px; border-radius: 12px; max-width: 500px; margin: auto;">
                    <h2 style="color: #d4af37; margin-top: 0;">Assalamu Alaikum! 🌙</h2>
                    <p style="font-size: 16px; line-height: 1.5; color: #e5e7eb;">
                        Consistency is the secret to retaining the Quran. You haven't logged your revision session yet today!
                    </p>
                    <p style="font-size: 15px; color: #d1d5db;">
                        Take just 10–15 minutes now to protect your memorization and keep your streak strong.
                    </p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://your-streamlit-app-url.streamlit.app" 
                           style="background-color: #d4af37; color: #022c22; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; display: inline-block;">
                           📖 Open Quran Tracker
                        </a>
                    </div>
                    <p style="font-size: 12px; color: #9ca3af; text-align: center; margin-bottom: 0;">
                        You received this because you enabled daily reminders in your Quran Tracker settings.
                    </p>
                </div>
                """
            }
            resend.Emails.send(params)
            print(f"✅ Email successfully dispatched to {email}")
        else:
            print(f"🎉 User {email} already logged today. Skipping email.")

except Exception as e:
    print(f"❌ Error during reminder check: {e}")