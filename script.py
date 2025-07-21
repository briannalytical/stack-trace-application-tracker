import psycopg2
from datetime import date

# db connection
conn = psycopg2.connect (
    dbname="postgres",
    user="postgres",
    password="your_password_here",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# fetch today's date
today = date.today()

# menu
print("\n📋 Hello! How can I help you?")
print("1. View today’s tasks")
print("2. Track a new job application")
print("3. Update an existing application")

choice = input("Enter 1, 2, or 3: ").strip()

# option 1: tasks
if choice == "1":
    query = """
        SELECT id, job_title, company, next_action, check_application_status, next_follow_up_date
        FROM application_tracking
        WHERE check_application_status::DATE = %s
            OR next_follow_up_date::DATE = %s
        ORDER BY job_title;
    """
    cursor.execute(query, (today, today))
    rows = cursor.fetchall()

    if not rows:
        print("\n🎉 No tasks for today!")
    else:
        print(f"\n🗓️ Tasks for {today.strftime('%A, %B %d, %Y')}")
        print("-" * 50)
        for row in rows:
            app_id, job_title, company, next_action, check_date, follow_up_date = row
            due_type = "Check status" if check_date == today else "Follow up"
            print(f"📌 {job_title} @ {company}")
            print(f"   → Task: {next_action.replace('_', ' ').title()}")
            print(f"   → Type: {due_type}")
            print()

# option 2: application entry
elif choice == "2":
    print("\nEnter your new application details:")
    job_title = input("Job title: ").strip()
    company = input("Company: ").strip()
    software = input("How did you apply for this application: (LinkedIn, Greenhouse, company website, etc): ").strip()
    notes = input("Any notes about this particular role? (optional): ").strip()
    print("Optional now, but do your research! 🔎 Who is the contact or recruiter you'll need to follow up with? If you don't know now, you can add it later.")
    contact_name = input("Contact Name: ").strip()
    contact_details = input("Contact Details: ").strip()

    cursor.execute("""
        INSERT INTO application_tracking (job_title, company, application_software, job_notes)
        VALUES (%s, %s, %s, %s);
    """, (job_title, company, software or None, notes or None))

    conn.commit()
    print("✅ Application added! I'll remind you when you have tasks related to this job in the future! 🎉 Around here we FOLLOW UP with applications. 😊")

# option 3: update existing 
elif choice == "3":
    cursor.execute("SELECT id, job_title, company FROM application_tracking ORDER BY id;")
    apps = cursor.fetchall()

    print("\n--- Existing Applications ---")
    for app in apps:
        print(f"{app[0]}: {app[1]} @ {app[2]}")

    app_id = int(input("\nEnter the ID of the application you want to update: "))
    print("\nWhat do you need to update?")
    print("➡️ please enter status, followup, interview, or notes")
    field = input("Field to update: ").strip().lower()

    if field == "status":
        print("\nAvailable status values:")
        new_status = input("New application status: ").strip()
        cursor.execute("""
            UPDATE application_tracking
            SET application_status = %s
            WHERE id = %s;
        """, (new_status, app_id))

    elif field == "followup":
        contact_name = input("Contact name: ").strip()
        contact_details = input("Contact email/phone: ").strip()
        cursor.execute("""
            UPDATE application_tracking
            SET follow_up_contact_name = %s,
                follow_up_contact_details = %s
            WHERE id = %s;
        """, (contact_name, contact_details, app_id))

    elif field == "interview":
        interview_date = input("Enter interview date (YYYY-MM-DD): ").strip()
        interview_name = input("Interviewer name: ").strip()
        prep_notes = input("Any prep notes? (optional): ").strip()

        cursor.execute("""
            UPDATE application_tracking
            SET interview_date = %s,
                interviewer_name = %s,
                interview_prep_notes = %s
            WHERE id = %s;
        """, (interview_date, interview_name, prep_notes or None, app_id))

    elif field == "notes":
        new_notes = input("Enter your updated job notes: ").strip()
        cursor.execute("""
            UPDATE application_tracking
            SET job_notes = %s
            WHERE id = %s;
        """, (new_notes, app_id))

    conn.commit()
    print("✅ Application updated.")

else:
    print("❌ Invalid selection 🥲 Please start again.")

# ---------- CLEANUP ----------
cursor.close()
conn.close()