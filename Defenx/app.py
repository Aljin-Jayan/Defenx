from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, Field, EmailStr
from typing import List, Optional, Dict, Any, Union
import os
import hashlib
import difflib
import logging
import requests
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
import secrets
import string
from bs4 import BeautifulSoup
import uvicorn
import asyncio

# Import components from your existing code files
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import difflib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision import models

app = FastAPI(
    title="Website Defacement Detector API",
    description="API for detecting unauthorized changes to websites",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for storing data
BASE_DIR = Path("defacement_detector_data")
SNAPSHOTS_DIR = BASE_DIR / "snapshots"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
LOGS_DIR = BASE_DIR / "logs"

for directory in [BASE_DIR, SNAPSHOTS_DIR, SCREENSHOTS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "defacement_detector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("defacement_detector")

# Email configuration from newfile.py
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.yandex.ru")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "Defenx.secure@yandex.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "13525wdbsgreae")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "sample@gmail.com")

# Global storage for website snapshots (in-memory for simplicity)
html_snapshots = {}
screenshot_pairs = {}
monitored_sites = {}

# Pydantic models
class URLRequest(BaseModel):
    url: str
    check_frequency: Optional[int] = 3600  # Default check frequency in seconds
    similarity_threshold: Optional[float] = 0.95  # Default similarity threshold
    notify_email: Optional[str] = None  # Optional email to send notifications
    take_screenshots: Optional[bool] = True  # Whether to take and compare screenshots

class MonitoringStatus(BaseModel):
    url: str
    status: str
    last_checked: Optional[str] = None
    html_hash: Optional[str] = None
    last_screenshot: Optional[str] = None
    monitoring_since: str

class DefacementAlert(BaseModel):
    url: str
    timestamp: str
    reason: str
    similarity: Optional[float] = None
    visual_similarity: Optional[float] = None
    changes: List[str]

class SnapAnalyser:
    """Port of your snap.py file"""
    def __init__(self):
        pass

    def load_file_content(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()

    def compare_snapshots(self, original_snapshot, current_snapshot):
        diff = difflib.unified_diff(original_snapshot, current_snapshot, lineterm='')
        changes = list(diff)
        return changes

# Core functions for website content analysis

def get_html_content(url: str) -> str:
    """Fetch website content"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        raise HTTPException(status_code=404, detail=f"Error fetching URL: {str(e)}")

def hash_html(html_content: str) -> str:
    """Calculate hash of HTML content"""
    return hashlib.sha256(html_content.encode('utf-8')).hexdigest()

def send_email_notification(url: str, reason: str, detailed_changes: List[str]) -> bool:
    """Send email notification for defacement"""
    try:
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = f"⚠️ ALERT: Website Defacement Detected on {url}"
        
        # Email body
        body = f"""
        Website Defacement Alert
        
        URL: {url}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Reason: {reason}

        "Dear User,\n\n"

         We have detected a defacement on your website, indicating possible unauthorized access or malicious activity. 
         Immediate action is required to prevent further security risks.\n\n
         What Happened?\n
         Our automated monitoring system at DefenX identified suspicious changes to your website’s content.
         This could be due to:\n
         ✅ Unauthorized access to your website files.\n
         ✅ Malicious scripts injected into your web pages.\n
         ✅ Changes to homepage content, displaying unwanted messages or images.\n\n
         Initial Precautions to Take Immediately:\n
         🔹 Take your website offline temporarily to prevent further damage.\n
         🔹 Reset all administrator passwords, including database and hosting credentials.\n
         🔹 Scan your website files for malware using an updated antivirus tool.\n
         🔹 Restore a recent backup if available, but ensure the backup is clean.\n
         🔹 Check user access logs for any unauthorized login attempts.\n\n
        
        Sample of Changes:
        {"".join(detailed_changes[:20])}
        
         Next Steps with DefenX:\n
            Our security team is actively investigating the incident. We will provide you with a detailed security report and recommendations
            to enhance your website’s protection.\n\n
            If you need immediate assistance, please contact our support team at support@defenx.com or call [your helpline number].\n\n
            Your website’s security is our priority. We strongly advise implementing web application firewalls (WAF), 
            regular backups, and security patches to prevent future attacks.\n\n
            Best regards,\n\n
            DefenX Security Team\n
            📧 support@defenx.com\n

            
        This is an automated alert from the Website Defacement Detection System.
        """
        
        msg.attach(MIMEText(body, "plain"))
        
        # Send email
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email notification sent for {url}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending email notification: {e}")
        return False

async def capture_screenshot(url: str) -> str:
    """Capture website screenshot using Selenium"""
    try:
        # Create a safe filename from URL
        filename = url.replace('://', '_').replace('/', '_').replace(':', '_')
        screenshot_path = str(SCREENSHOTS_DIR / f"{filename}_{int(time.time())}.png")
        
        # Set up Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1366, 768)  # Consistent size
        
        # Navigate and screenshot
        driver.get(url)
        # Wait for page to load
        await asyncio.sleep(5)
        
        driver.save_screenshot(screenshot_path)
        driver.quit()
        
        logger.info(f"Screenshot saved to {screenshot_path}")
        return screenshot_path
    
    except Exception as e:
        logger.error(f"Error capturing screenshot for {url}: {e}")
        return None

def compare_images(image1_path: str, image2_path: str) -> tuple:
    """Compare two images using a neural network for feature extraction"""
    try:
        # Load ResNet-50 model
        resnet50 = models.resnet50(pretrained=True)
        resnet50.eval()
        
        # Transform image for the model
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            transforms.Resize((224, 224)),
        ])

        # Load images
        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)

        # Apply transformation
        image1_tensor = transform(image1).unsqueeze(0)
        image2_tensor = transform(image2).unsqueeze(0)

        # Get feature vectors from ResNet-50
        with torch.no_grad():
            features1 = resnet50(image1_tensor)
            features2 = resnet50(image2_tensor)
        
        # Calculate cosine similarity
        similarity = torch.nn.functional.cosine_similarity(features1, features2).item()
        
        defacement_detected = similarity < 0.9  # Threshold for significant change
        
        return defacement_detected, similarity
    
    except Exception as e:
        logger.error(f"Error comparing images: {e}")
        return False, 0.0

def analyze_html_changes(old_content: str, new_content: str, similarity_threshold: float = 0.95) -> tuple:
    """Analyze changes between old and new HTML content"""
    # Calculate content similarity
    similarity = difflib.SequenceMatcher(None, old_content, new_content).ratio()
    
    # Check for suspicious keywords
    suspicious_keywords = [
        "hacked", "pwned", "owned", "defaced", "security breach",
        "hacker", "cyber caliphate", "anonymous", "hack3d"
    ]
    
    soup = BeautifulSoup(new_content, "html.parser")
    text_content = soup.get_text().lower()
    found_keywords = [kw for kw in suspicious_keywords if kw in text_content]
    
    # Compare HTML structure
    old_soup = BeautifulSoup(old_content, "html.parser")
    old_tags = [tag.name for tag in old_soup.find_all()]
    new_tags = [tag.name for tag in soup.find_all()]
    structure_similarity = difflib.SequenceMatcher(None, old_tags, new_tags).ratio()
    
    # Get specific changes
    diff = list(difflib.unified_diff(
        old_content.splitlines(keepends=True), 
        new_content.splitlines(keepends=True), 
        n=3
    ))
    
    # Decision logic
    defacement_detected = False
    reasons = []
    
    if similarity < similarity_threshold:
        defacement_detected = True
        reasons.append(f"Content similarity below threshold: {similarity:.2f} < {similarity_threshold}")
    
    if found_keywords:
        defacement_detected = True
        reasons.append(f"Suspicious keywords found: {', '.join(found_keywords)}")
    
    if structure_similarity < 0.8:
        defacement_detected = True
        reasons.append(f"Significant HTML structure changes detected: {structure_similarity:.2f}")
    
    return defacement_detected, "\n".join(reasons) if reasons else "No issues detected", similarity, diff

async def check_website(url: str, similarity_threshold: float = 0.95, take_screenshots: bool = True) -> Dict:
    """Check a website for defacement"""
    result = {
        "url": url,
        "checked_at": datetime.now().isoformat(),
        "defacement_detected": False,
        "reason": None,
        "content_similarity": None,
        "visual_similarity": None,
        "changes": None
    }
    
    # Get current HTML content
    try:
        current_html = get_html_content(url)
        current_hash = hash_html(current_html)
    except Exception as e:
        logger.error(f"Error fetching HTML for {url}: {e}")
        result["reason"] = f"Error fetching content: {str(e)}"
        return result
    
    # Check if we have a previous snapshot
    if url in html_snapshots:
        previous_hash = html_snapshots[url]["hash"]
        previous_html = html_snapshots[url]["content"]
        
        # If hash matches, no changes detected
        if current_hash == previous_hash:
            result["reason"] = "No changes detected"
            html_snapshots[url]["last_checked"] = datetime.now().isoformat()
            return result
        
        # Analyze HTML changes
        defacement_detected, reason, similarity, changes = analyze_html_changes(
            previous_html, current_html, similarity_threshold
        )
        
        result["defacement_detected"] = defacement_detected
        result["reason"] = reason
        result["content_similarity"] = similarity
        result["changes"] = changes[:50] if changes else []  # Limit to 50 changes
        
        # Update HTML snapshot
        html_snapshots[url] = {
            "content": current_html,
            "hash": current_hash,
            "last_checked": datetime.now().isoformat()
        }
        
        # Check screenshot comparison if enabled
        if take_screenshots:
            current_screenshot = await capture_screenshot(url)
            
            if current_screenshot and url in screenshot_pairs and screenshot_pairs[url]:
                previous_screenshot = screenshot_pairs[url]
                
                # Compare screenshots
                visual_defacement, visual_similarity = compare_images(
                    previous_screenshot, current_screenshot
                )
                
                result["visual_similarity"] = visual_similarity
                
                # If visual defacement detected but not HTML defacement
                if visual_defacement and not defacement_detected:
                    result["defacement_detected"] = True
                    result["reason"] += "\nVisual defacement detected in screenshot comparison"
            
            # Update screenshot reference
            screenshot_pairs[url] = current_screenshot
    else:
        # First time check - initialize monitoring
        html_snapshots[url] = {
            "content": current_html,
            "hash": current_hash,
            "last_checked": datetime.now().isoformat()
        }
        
        if take_screenshots:
            screenshot_pairs[url] = await capture_screenshot(url)
        
        result["reason"] = "Monitoring initialized"
    
    # Update monitoring status
    monitored_sites[url] = {
        "status": "defaced" if result["defacement_detected"] else "ok",
        "last_checked": datetime.now().isoformat(),
        "monitoring_since": monitored_sites.get(url, {}).get("monitoring_since", datetime.now().isoformat())
    }
    
    return result

# API endpoints

@app.get("/")
async def root():
    return {"message": "Website Defacement Detector API is running"}

@app.post("/monitor", status_code=status.HTTP_200_OK)
async def initialize_monitoring(request: URLRequest, background_tasks: BackgroundTasks):
    """Start monitoring a website for defacement"""
    url = request.url
    
    # Initialize monitoring in background
    background_tasks.add_task(
        check_website, 
        url=url,
        similarity_threshold=request.similarity_threshold,
        take_screenshots=request.take_screenshots
    )
    
    # Store site configuration
    monitored_sites[url] = {
        "status": "initializing",
        "check_frequency": request.check_frequency,
        "similarity_threshold": request.similarity_threshold,
        "notify_email": request.notify_email,
        "take_screenshots": request.take_screenshots,
        "monitoring_since": datetime.now().isoformat(),
        "last_checked": None
    }
    
    return {
        "message": f"Monitoring initialized for URL: {url}",
        "check_frequency": request.check_frequency,
        "similarity_threshold": request.similarity_threshold
    }

@app.post("/check")
async def check_for_defacement(request: URLRequest, background_tasks: BackgroundTasks):
    """Check a website for defacement immediately"""
    url = request.url
    
    # Check if URL is being monitored
    if url not in monitored_sites:
        return await initialize_monitoring(request, background_tasks)
    
    # Perform check
    result = await check_website(
        url=url,
        similarity_threshold=monitored_sites[url].get("similarity_threshold", 0.95),
        take_screenshots=monitored_sites[url].get("take_screenshots", True)
    )
    
    # If defacement detected, send notification
    if result["defacement_detected"]:
        notify_email = monitored_sites[url].get("notify_email") or RECIPIENT_EMAIL
        
        if notify_email:
            background_tasks.add_task(
                send_email_notification,
                url=url,
                reason=result["reason"],
                detailed_changes=result["changes"]
            )
    
    return {
        "url": url,
        "defacement_detected": result["defacement_detected"],
        "reason": result["reason"],
        "checked_at": result["checked_at"],
        "content_similarity": result["content_similarity"],
        "visual_similarity": result["visual_similarity"]
    }

@app.get("/status")
async def get_monitoring_status(url: Optional[str] = None):
    """Get monitoring status for all or a specific website"""
    if url:
        if url in monitored_sites:
            status_data = monitored_sites[url]
            html_data = html_snapshots.get(url, {})
            
            return {
                "url": url,
                "status": status_data.get("status", "unknown"),
                "last_checked": status_data.get("last_checked"),
                "html_hash": html_data.get("hash"),
                "monitoring_since": status_data.get("monitoring_since"),
                "check_frequency": status_data.get("check_frequency"),
                "screenshot_available": url in screenshot_pairs and screenshot_pairs[url] is not None
            }
        else:
            raise HTTPException(status_code=404, detail=f"URL '{url}' is not being monitored")
    
    # Return status for all monitored sites
    result = []
    for site_url, status_data in monitored_sites.items():
        html_data = html_snapshots.get(site_url, {})
        
        result.append({
            "url": site_url,
            "status": status_data.get("status", "unknown"),
            "last_checked": status_data.get("last_checked"),
            "html_hash": html_data.get("hash"),
            "monitoring_since": status_data.get("monitoring_since"),
            "check_frequency": status_data.get("check_frequency")
        })
    
    return result

@app.delete("/stop")
async def stop_monitoring(request: URLRequest):
    """Stop monitoring a website"""
    url = request.url
    
    if url not in monitored_sites:
        raise HTTPException(status_code=404, detail=f"URL '{url}' is not being monitored")
    
    # Remove from monitoring
    monitored_sites.pop(url, None)
    html_snapshots.pop(url, None)
    screenshot_pairs.pop(url, None)
    
    return {"message": f"Stopped monitoring URL: {url}"}

@app.post("/compare_snapshots")
async def compare_html_snapshots(request: URLRequest):
    """Compare current HTML with baseline for a monitored website"""
    url = request.url
    
    if url not in html_snapshots:
        raise HTTPException(status_code=404, detail=f"URL '{url}' is not being monitored or has no baseline")
    
    # Get current HTML
    current_html = get_html_content(url)
    baseline_html = html_snapshots[url]["content"]
    
    # Compare
    defacement_detected, reason, similarity, changes = analyze_html_changes(
        baseline_html, current_html, 
        monitored_sites[url].get("similarity_threshold", 0.95)
    )
    
    return {
        "url": url,
        "defacement_detected": defacement_detected,
        "reason": reason,
        "content_similarity": similarity,
        "changes": changes[:50] if changes else []  # Limit to 50 changes
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "time": datetime.now().isoformat(),
        "monitored_sites_count": len(monitored_sites),
        "version": "1.0.0"
    }

# Standalone server function
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)