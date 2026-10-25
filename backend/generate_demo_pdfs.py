import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import os

os.makedirs(r"c:\Users\bhave\Sakshya\demo_test_documents", exist_ok=True)

# 1. Generate Tampered Deed with Canva metadata
buffer1 = io.BytesIO()
c1 = canvas.Canvas(buffer1, pagesize=letter)
c1.setFont("Helvetica-Bold", 16)
c1.drawString(72, 720, "GOVERNMENT OF MAHARASHTRA - REVENUE DEPARTMENT")
c1.setFont("Helvetica", 12)
c1.drawString(72, 690, "REGISTERED SALE DEED & TITLE CONVEYANCE")
c1.line(72, 680, 540, 680)

c1.setFont("Helvetica", 10)
c1.drawString(72, 640, "Institution: National Knowledge Institute of Technology")
c1.drawString(72, 620, "Survey / Khasra Identifier: Survey No. 991/B, Sector 4")
c1.setFont("Helvetica-Bold", 11)
c1.drawString(72, 590, "Schedule A - Land Holding: 2.10 Acres (Digitally Altered from 1.75 Acres)")
c1.setFont("Helvetica", 10)
c1.drawString(72, 560, "Execution Date: 10th August 2019")
c1.drawString(72, 540, "Sub-Registrar Registration Seal: CERTIFIED / SEAL-PUNE-0912")
c1.save()

# Inject Canva metadata via PyMuPDF
doc1 = fitz.open(stream=buffer1.getvalue(), filetype="pdf")
doc1.set_metadata({
    "creator": "Canva PDF Generator v2.4.1",
    "producer": "Canva Graphics Engine (Pro Subscription)",
    "title": "Land Deed Alteration Template",
    "author": "Graphic Designer"
})
doc1.save(r"c:\Users\bhave\Sakshya\demo_test_documents\1_Tampered_Land_Deed_Canva.pdf")
doc1.close()

# 2. Generate Expired Fire NOC
buffer2 = io.BytesIO()
c2 = canvas.Canvas(buffer2, pagesize=letter)
c2.setFont("Helvetica-Bold", 16)
c2.drawString(72, 720, "DIRECTORATE OF FIRE & EMERGENCY SERVICES")
c2.setFont("Helvetica", 12)
c2.drawString(72, 690, "STATUTORY FIRE SAFETY NO OBJECTION CERTIFICATE")
c2.line(72, 680, 540, 680)

c2.setFont("Helvetica", 10)
c2.drawString(72, 640, "Issued To: National Knowledge Institute Campus Building A & B")
c2.drawString(72, 620, "Inspection Reference: DFES/INSP/2021/8892")
c2.setFont("Helvetica-Bold", 11)
c2.drawString(72, 590, "Validity Period: Valid Up To 09-01-2023 (EXPIRED)")
c2.setFont("Helvetica", 10)
c2.drawString(72, 560, "Condition: Annual fire evacuation drills and hydrant pressure tests required.")
c2.save()

doc2 = fitz.open(stream=buffer2.getvalue(), filetype="pdf")
doc2.set_metadata({
    "creator": "Fire Department IT Portal",
    "producer": "Government Printing Bureau",
    "title": "Fire NOC 2021"
})
doc2.save(r"c:\Users\bhave\Sakshya\demo_test_documents\2_Expired_Fire_Safety_NOC.pdf")
doc2.close()

# 3. Generate Genuine Clean Land Deed
buffer3 = io.BytesIO()
c3 = canvas.Canvas(buffer3, pagesize=letter)
c3.setFont("Helvetica-Bold", 16)
c3.drawString(72, 720, "STATE REVENUE DEPARTMENT - LAND RECORDS OFFICE")
c3.setFont("Helvetica", 12)
c3.drawString(72, 690, "CERTIFIED TITLE DEED & PROPERTY CARD")
c3.line(72, 680, 540, 680)

c3.setFont("Helvetica", 10)
c3.drawString(72, 640, "Registered Title Holder: Savitribai Phule Institute of Technology")
c3.drawString(72, 620, "Survey Identifier: Khasra No. 402/1, Pune Urban District")
c3.setFont("Helvetica-Bold", 11)
c3.drawString(72, 590, "Total Registered Area: 2.85 Acres (Clear Title, Non-Agricultural)")
c3.setFont("Helvetica", 10)
c3.drawString(72, 560, "Registration Date: 15-02-2019")
c3.drawString(72, 540, "Digital Attestation: DIGILOCKER-VERIFIED-HASH-402")
c3.save()

doc3 = fitz.open(stream=buffer3.getvalue(), filetype="pdf")
doc3.set_metadata({
    "creator": "State Land Portal CAD Scanner",
    "producer": "Bhulekh Digital Document Engine v4",
    "title": "Certified Land Record Khasra 402/1"
})
doc3.save(r"c:\Users\bhave\Sakshya\demo_test_documents\3_Genuine_Government_Deed.pdf")
doc3.close()

print("Demo test documents successfully generated in demo_test_documents/")
