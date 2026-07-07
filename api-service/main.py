from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from shared.database import get_db, engine
from shared.models import Base, Site, SiteCheck

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Pydantic schemas
class SiteCreate(BaseModel):
    url: str
    name: str

# Routes
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/sites")
def add_site(site: SiteCreate, db: Session = Depends(get_db)):
    existing = db.query(Site).filter(Site.url == site.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Site already exists")
    new_site = Site(url=site.url, name=site.name)
    db.add(new_site)
    db.commit()
    db.refresh(new_site)
    return new_site

@app.get("/sites")
def get_sites(db: Session = Depends(get_db)):
    return db.query(Site).all()

@app.get("/sites/{site_id}/status")
def get_status(site_id: int, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    checks = db.query(SiteCheck).filter(SiteCheck.site_id == site_id).order_by(SiteCheck.checked_at.desc()).limit(10).all()
    return {"site": site, "recent_checks": checks}