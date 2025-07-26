import datetime
import psycopg2
from datetime import date

# db connection
conn = psycopg2.connect(
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
def show_intro():
    print("\n📋 Hello! Welcome to Stack Trace Job Application Tracker! I hope you will find this tool useful! 🥰")
    print("It's tough out there, but tracking your applications doesn't have to be!")
    print("You can use this tool to track applications, remind you when to follow up, and schedule your interviews!")

def show_main_menu():
    print("\nWhat would you like to do? Enter your choice below:")
    print("\nVIEW: View all applications")
    print("TASKS: View today’s tasks")
    print("ENTER: Track a new job application")
    print("UPDATE: Update an existing application")
    print("TIPS: Some helpful tips to keep in mind as you apply")
    print("BYE: End your session")
    
show_intro()

while True:
    show_main_menu()
    choice = input("\nAction: ").strip().upper()

    # Option 1: View applications
    if choice == "VIEW":
        query = "SELECT * FROM application_tracking"
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        if not rows:
            print("\n😶 No applications found.")
        else:
            print("\n📄 All Applications")
            print("=" * 60)

        for row in rows:
            # Pair column names with values and exclude 'id' and empty/null values
            display_fields = [
                (col, val) for col, val in zip(column_names, row)
                    if col != "id" and val not in (None, '')
            ]

            if display_fields:
                for col, val in display_fields:
                    # Format dates and times
                    if isinstance(val, datetime.date):
                        val = val.strftime("%B %d, %Y")
                    elif isinstance(val, datetime.time):
                        val = val.strftime("%I:%M %p")

                    # Format column name nicely (optional)
                    col_clean = col.replace('_', ' ').title()
                    print(f"{col_clean}: {val}")

                print("-" * 60)

    # option 2: tasks
    elif choice == "TASKS":
        query = """
            SELECT id, job_title, company, next_action,
               check_application_status, next_follow_up_date,
               interview_date, interview_time, second_interview_date, final_interview_date
            FROM application_tracking
            WHERE check_application_status::DATE = %s
            OR next_follow_up_date::DATE = %s
            OR interview_date::DATE = %s
            OR second_interview_date::DATE = %s
            OR final_interview_date::DATE = %s
            ORDER BY job_title;
        """
    cursor.execute(query, (today, today, today, today, today))
    rows = cursor.fetchall()

    if not rows:
        print("\n🎉 No tasks for today!")
    else:
        print(f"\n🗓️ Tasks for {today.strftime('%A, %B %d, %Y')}")
        print("-" * 60)

        for row in rows:
            (app_id, job_title, company, next_action,
             check_date, follow_up_date,
             interview_date, interview_time,
             second_interview_date, final_interview_date) = row

            # Determine task type
            if interview_date == today or second_interview_date == today or final_interview_date == today:
                due_type = "Interview"
            else:
                due_type = "Follow Up"

            # Print task
            print(f"📌 {job_title} @ {company}")
            print(f"   → Task: {next_action.replace('_', ' ').title()}")
            print(f"   → Type: {due_type}")
            if interview_time:
                print(f"   → Interview Time: {interview_time.strftime('%I:%M %p')}")
            print()

            # prompt to complete task
            complete = input("✅ Mark this task as completed? (y/n): ").strip().lower()
            if complete == "y":
                # You can adjust status logic here
                updated_status = input("Enter new application status (or press Enter to skip): ").strip()
                if updated_status:
                    cursor.execute("""
                        UPDATE application_tracking
                        SET application_status = %s
                        WHERE id = %s;
                    """, (updated_status, app_id))
                    conn.commit()
                    print("✅ Status updated!\n")
                else:
                    print("⏭️ Skipped updating status.\n")
            else:
                print("⏭️ Skipped.\n")

        print("-" * 60)

    # option 3: application entry
    elif choice == "ENTER":
        print("\nEnter your new application details:")
        job_title = input("Job title: ").strip()
        company = input("Company: ").strip()
        software = input("How did you apply (LinkedIn, Workday, Greenhouse, company website etc): ").strip()
        notes = input("Any notes about this role? (optional): ").strip()
        print("Optional now, but do your research! 🔎")
        contact_name = input("Contact Name: ").strip()
        contact_details = input("Contact Details: ").strip()

        cursor.execute("""
            INSERT INTO application_tracking (
                job_title, company, application_software, job_notes,
                follow_up_contact_name, follow_up_contact_details
            ) VALUES (%s, %s, %s, %s, %s, %s);
        """, (job_title, company, software or None, notes or None, contact_name or None, contact_details or None))

        conn.commit()
        print("\n✅ Application added! I’ll remind you when you have tasks related to this job. 😊")

    # option 4: update existing
    elif choice == "UPDATE":
        cursor.execute("SELECT id, job_title, company FROM application_tracking ORDER BY id;")
        apps = cursor.fetchall()

        print("\n--- Existing Applications ---")
        for app in apps:
            print(f"{app[0]}: {app[1]} @ {app[2]}")

        app_id = int(input("\nEnter the ID of the application to update: "))
        print("\nWhat do you want to update?")
        print("➡️ Please enter: status, followup, interview, or notes: 👩🏻‍💻")
        field = input("Field to update: ").strip().lower()

        if field == "status":
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
            interview_time = input("Enter interview time (HH:MM, 24h format): ").strip()
            prep_notes = input("Any prep notes? (optional, but recommended): ").strip()
            cursor.execute("""
                UPDATE application_tracking
                SET interview_date = %s,
                    interview_time = %s,
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
        
    elif choice == "TIPS":
        print("Around here we FOLLOW UP! 📩 You are 78% more likely to land an interview if you reach out to a recruiter or hiring manager after you apply.")
        print("TAKE NOTES! ✏️ You should already know why you want to work for the company and about their mission BEFORE speaking with someone from the company.")
        print("Confidence is Key 🔑 You know you deserve this job and focus on YOU, not anyone else!")
        print("Keep applying, keep trying. 💻 It will not be this way forever.")
        

    elif choice == "BYE":
        print("👋 Goodbye! Check back again soon!")
        break

    else:
        print("❌ Invalid selection. 🥲 Please try again from the main menu.")

# cleanup
cursor.close()
conn.close()