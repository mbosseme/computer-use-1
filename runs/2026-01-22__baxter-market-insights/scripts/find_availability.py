from datetime import datetime, timedelta, date
import json
from pathlib import Path
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig

# Timezone handling might be tricky without pytz, but let's try basic arithmetic or use the timezone info from Graph.
# Ideally we just look at the raw times returned which are usually in the requested timezone or UTC.
# Graph `getSchedule` takes `startDateTime` and `endDateTime` with timezones.

def get_availability(client, user_email):
    now = datetime.now()
    # Next 7 days
    start_date = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1) # Start next hour
    end_date = start_date + timedelta(days=7)
    
    # Format for Graph
    # We will ask for the user's timezone from the mailbox settings if possible, or just default to Eastern if configured
    # actually load_graph_env loads PLANNER_TIMEZONE
    
    # We need a proper datetime string.
    # We'll use naive isoformat assuming local system time logic or UTC if simpler.
    # Let's try to query mailboxSettings first to get user's timezone.
    # If 403 (requires MailboxSettings.Read), we fallback to config/env.
    
    # tz_resp = client.get("me/mailboxSettings/timeZone")
    # user_tz = tz_resp.get("value", "Eastern Standard Time") 
    
    user_tz = "Eastern Standard Time" # Default fallback
    print(f"User Timezone: {user_tz}")

    # Start/End in the user's timezone (approximation without heavy tz calc lib, just passing strings)
    start_str = start_date.strftime("%Y-%m-%dT%H:00:00")
    end_str = end_date.strftime("%Y-%m-%dT%H:00:00")
    
    payload = {
        "schedules": [user_email],
        "startTime": {
            "dateTime": start_str,
            "timeZone": user_tz
        },
        "endTime": {
            "dateTime": end_str,
            "timeZone": user_tz
        },
        "availabilityViewInterval": 30 # 30 min slots
    }
    
    resp = client.post("me/calendar/getSchedule", json=payload)
    
    # The response is a collection of ScheduleInformation
    # value: [ { scheduleId: ..., availabilityView: "0022..." } ]
    
    import math
    
    suggestions = []
    
    if "value" in resp:
        shed_info = resp["value"][0]
        avail_view = shed_info.get("availabilityView", "")
        
        # '0' = Free
        # '2' = Busy
        # Each char is 30 mins starting from start_str
        
        # We want to find slots in business hours (9am - 5pm)
        # We need to map the index back to the hour of day.
        
        current_dt = start_date
        
        # We need to correctly increment current_dt match the slots.
        # Since we passed naive string and tz, Graph calculates relative to that.
        # We can just iterate the slots.
        
        daily_slots = {} # Key: Date, Value: List of times
        
        for i, status in enumerate(avail_view):
            slot_time = start_date + timedelta(minutes=i*30)
            
            # Check business hours (9 to 17)
            # Also check if it's a weekday (0=Mon, 6=Sun)
            if 9 <= slot_time.hour < 17 and status == '0' and slot_time.weekday() < 5:
                # Check if next slot is also free (for a 1 hour block or at least 45 mins safe)
                if i+1 < len(avail_view) and avail_view[i+1] == '0':
                    day_key = slot_time.strftime("%A, %b %d")
                    time_str = slot_time.strftime("%I:%M %p")
                    
                    if day_key not in daily_slots:
                        daily_slots[day_key] = []
                    
                    # Avoid adding every single 30 min slot, maybe just distinct blocks
                    # Simple heuristic: if we didn't just add the previous slot
                    if not daily_slots[day_key] or (slot_time - datetime.strptime(f"{day_key} {daily_slots[day_key][-1]}", "%A, %b %d %I:%M %p")).seconds > 1800:
                         daily_slots[day_key].append(time_str)
            
    return daily_slots

def main():
    repo_root = Path.cwd()
    env = load_graph_env(repo_root)
    auth = GraphAuthenticator(repo_root=repo_root, env=env)
    
    config = GraphClientConfig(
        base_url=env.base_url,
        scopes=env.scopes,
        planner_timezone=env.planner_timezone
    )
    client = GraphAPIClient(authenticator=auth, config=config)
    
    # Get me
    me = client.get("me")
    my_email = me.get("mail") or me.get("userPrincipalName")
    print(f"My Email: {my_email}")
    
    slots = get_availability(client, my_email)
    
    print("\n--- Available Slots (Next 7 Days, 9am-5pm) ---")
    count = 0
    for day, times in slots.items():
        if count >= 3: break # Just top 3 days
        print(f"{day}: {', '.join(times[:3])}") # Just top 3 times per day
        count += 1

if __name__ == "__main__":
    main()
