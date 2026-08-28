import urllib.request
import urllib.parse
import json
import uuid

import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# We will just test the classifier directly from python since we want to know what it outputs
from utils.classifier import classify_document

docs = {
    "brd.txt": "BUSINESS REQUIREMENTS DOCUMENT\nBusiness Objective: Increase revenue.\nStakeholders: CEO, CTO\nBusiness Need: Better performance.\nScope: Global.",
    "srs.txt": "SOFTWARE REQUIREMENTS SPECIFICATION\nFR-001 The system shall run on Linux.\nNFR-001 Performance requirements must be met.\nFunctional requirements included.",
    "frd.txt": "FUNCTIONAL REQUIREMENTS DOCUMENT\nFunctional specification:\nInput: user data\nOutput: report\nSystem function: parse logs\nProcess flow...",
    "user_story.txt": "As a user, I want to login so that I can see my dashboard. Acceptance criteria: Given I am on the login page, When I enter my password, Then I log in.",
    "test_case.txt": "Test Case: Login\nTest ID: TC-001\nTest Scenario: Valid login\nExpected Result: Success\nActual Result: Pass",
    "change_req.txt": "Change Request: CR-042\nRequested Change: Update DB.\nReason for change: Slow.\nChange impact: High.\nPriority: P1.",
    "release_notes.txt": "Release Notes Version 2.0\nBug fixes: #123\nNew features: Search\nEnhancements: Speed\nBreaking changes: None.",
    "meeting_minutes.txt": "Meeting Minutes\nAttendees: Alice, Bob\nAgenda: Planning\nDiscussion: Time limits\nDecisions: Approved\nAction items: Deploy tomorrow.",
    "unknown.txt": "This is just a random text file about how I spent my weekend. It has no software engineering terminology.",
    "ambig_conflict.txt": "Business Objective: Increase sales. System shall authenticate users. Functional requirements and Stakeholders agree.",
    "ambig_generic.txt": "The software is a system that allows users to interact with requirements.",
    "ambig_empty.txt": "   \n\n  "
}

for name, text in docs.items():
    doc_type, conf, sigs = classify_document(text, name)
    print(f"{name}: {doc_type} ({conf}%)")

