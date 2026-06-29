import time
import requests
import schedule
import os
from sqlalchemy.orm import Session
from shared.database import SessionLocal
from shared.models import Site, SiteCheck

NOTIFS_URL = os.getenv("NOTIFS_URL", "http://notifs:8001")

def send_alert(site: Site, reason: str):
    try:
        requests.post(f"{NOTIFS_URL}/alert", json={
            "site_name": site.name,
            "url": site.url,
            "reason": reason
        }, timeout=5)
        print(f"Alert sent for {site.url}")
    except Exception as e:
        print(f"Failed to send alert for {site.url}: {e}")

def ping_site(site: Site, db: Session):
    try:
        response = requests.get(site.url, timeout=10)
        is_up = response.status_code < 500

        check = SiteCheck(
            site_id=site.id,
            is_up=True,
            response_time_ms=int(response.elapsed.total_seconds() * 1000),
            status_code=response.status_code
        )
        if not is_up:
            reason = f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        check = SiteCheck(site_id=site.id, is_up=False, response_time_ms=None, status_code=None)
        reason = "Request timed out"
    except Exception as e:
        check = SiteCheck(site_id=site.id, is_up=False, response_time_ms=None, status_code=None)
        reason = str(e)
    db.add(check)
    db.commit()
    print(f"Checked {site.url} — up: {check.is_up}, {check.response_time_ms}ms")

    if not check.is_up and reason:
        send_alert(site, reason)

def run_checks():
    db = SessionLocal()
    try:
        sites = db.query(Site).filter(Site.is_active == True).all()
        for site in sites:
            ping_site(site, db)
    finally:
        db.close()

schedule.every(5).minutes.do(run_checks)

print("Worker started, running checks every 5 minutes...")
run_checks()  # run once immediately on startup

while True:
    schedule.run_pending()
    time.sleep(1)