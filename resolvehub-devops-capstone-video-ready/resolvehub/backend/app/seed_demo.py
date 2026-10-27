"""Insert realistic demo tickets for a presentation. Safe to rerun: seeds only an empty table."""
from .database import SessionLocal
from .models import Ticket

DEMO_TICKETS = [
    {"title": "VPN access fails after password reset", "description": "VPN connection is rejected after the password reset this morning.", "requester": "Olivia Chen", "category": "IT Support", "priority": "Urgent", "status": "Open"},
    {"title": "Request access to analytics workspace", "description": "Need read access to the weekly analytics workspace for the quarterly review.", "requester": "Noah Williams", "category": "Access", "priority": "High", "status": "In Progress"},
    {"title": "Laptop camera not detected", "description": "The camera is missing from the meeting application's device settings.", "requester": "Mia Patel", "category": "Hardware", "priority": "Medium", "status": "Open"},
    {"title": "Update billing contact details", "description": "Billing contact was updated in the customer profile and verified.", "requester": "Ethan Brooks", "category": "Billing", "priority": "Low", "status": "Resolved"},
    {"title": "Email delivery delay for external recipients", "description": "External email delivery is delayed by several minutes and needs investigation.", "requester": "Sofia Garcia", "category": "Email", "priority": "High", "status": "In Progress"},
    {"title": "New employee account setup", "description": "Create access for a new teammate joining the support operations group.", "requester": "Aarav Mehta", "category": "Access", "priority": "Medium", "status": "Open"},
    {"title": "Shared drive permission request", "description": "A team member needs edit access to the shared project folder.", "requester": "Priya Nair", "category": "IT Support", "priority": "Low", "status": "Closed"},
]

def main():
    db = SessionLocal()
    try:
        existing = db.query(Ticket).count()
        if existing:
            print(f"Demo seed skipped: {existing} ticket(s) already exist. No data changed.")
            return
        db.add_all([Ticket(**ticket) for ticket in DEMO_TICKETS])
        db.commit()
        print(f"Inserted {len(DEMO_TICKETS)} demo tickets successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
