# SAKSHYA: Deterministic Regulatory Compliance & Fraud Verification Engine

> **AICTE Regulatory Decision-Support System · Dual-Engine Architecture**  
> Eliminating LLM hallucinations in statutory government approvals through formal methods (**Microsoft Z3 SMT Solver**), temporal interval constraint logic (**Allen's Interval Algebra**), and multi-layer document forensics (**OpenCV Error Level Analysis**).

---

## 🏛️ System Overview

Regulatory bodies such as the All India Council for Technical Education (AICTE) process thousands of complex institutional approval applications annually (Approval Process Handbook - APH). Traditional manual scrutiny is prone to oversight, while conventional generative AI/LLM systems hallucinate legal citations and cannot stand up in a court of law.

**Sakshya** solves this through a **Dual-Engine Design**:
1. **Non-Deterministic Layer**: Multimodal OCR, spatial bounding-box extraction, and computer vision forensic models detect pixel alterations, metadata stream tampering, and layout anomalies.
2. **Deterministic Layer**: Formulates statutory clauses into first-order logic and SMT constraints (Z3 Theorem Prover) and temporal DAG constraints to execute zero-hallucination compliance audits and court-admissible discrepancy reports.

```
                  Institution Upload / Portal Intake
                                  │
                                  ▼
                   [ Intake & Storage Pipeline ]
                     (SHA-256 Deduplication, S3/MinIO)
                                  │
                  ┌───────────────┴────────────────┐
                  ▼                                ▼
    [ Document Forensics & Security ]   [ Multimodal OCR & Entity Extractor ]
    • pikepdf Object Stream Anomalies    • Bounding Box Spatial Grounding
    • OpenCV Error Level Analysis (ELA)  • Key-Value Extraction [x1, y1, x2, y2]
    • pyHanko PKCS#7 Digital Signatures  • Faculty, Land, Area, Cadre Normalizer
    • pyzbar Dynamic QR Cross-Check      • pHash Perceptual Deduplication
                  │                                │
                  └───────────────┬────────────────┘
                                  ▼
             [ Cross-Document Regulatory Evidence Graph ]
               (Neo4j / NetworkX DAG: Entities, Timelines, APH Clauses)
                                  │
                  ┌───────────────┴────────────────┐
                  ▼                                ▼
    [ Formal Rule & Logic Engine ]      [ Issuing Authority Verifier ]
    • Z3 SMT Rule Conflict Finder        • DigiLocker NAD Mock/Live
    • Deterministic APH Rule Audit       • Land Records (Bhulekh API)
    • Shortfall & Citation Generator     • MCA21 Society/Trust Verifier
    • Allen's Interval Timeline Engine   • Fallback Manual Review Queue
                  │                                │
                  └───────────────┬────────────────┘
                                  ▼
             [ Explainable Officer Brief & Audit Ledger ]
               • Side-by-Side Original Document Crops vs AICTE Handbook Clauses
               • Cryptographic Audit Trail & Event Sourcing
               • Interactive Officer Dashboard (Next.js 16, React 19, Tailwind CSS)
```

---

## 🔬 The 9 Mandatory Features & How They Work

### 1. Application Management & Document Upload
- **Institution Profiles & Intake Categories**: Supports UG Engineering, PG, Diploma, Extension of Approval (EoA), and new program workflows.
- **Dynamic Checklists**: Category-specific document requirements (Land Deeds, Building Approvals, Fire NOC, Faculty Rosters, Balance Sheets).
- **Missing & Incomplete Document Detection**: Automated gatekeeper preventing submission until mandatory statutory documents are accounted for.

### 2. OCR & Intelligent Data Extraction
- **Spatial Bounding-Box Grounding**: Every extracted figure (land acreage, roll numbers, dates) retains its exact coordinates `[x1, y1, x2, y2, page]` linking back to the source certificate.
- **Automated Document Classification**: Categorizes incoming PDFs into Land Deeds, Building Sanctions, Fire NOCs, Faculty Rosters, and Trust Registrations.
- **Lapsed Validity Detection**: Identifies certificates whose validity expired prior to the portal application submission date.

### 3. Cross-Document & Institutional Record Validation
- **Entity Cross-Checking**: Compares claims across land deeds, architect blueprints, and faculty qualification records.
- **Shortfall Quantification**: Computes mathematical deficits (e.g., land deficit of `0.40 acres`, faculty deficit of `20 teachers`, cadre imbalance).
- **Previous Year Cross-Referencing**: Flags unauthorized changes in approved intake or campus boundary coordinates.

### 4. Document Anomaly & Potential Forgery Detection
- **Metadata Object Stream Forensics**: PyMuPDF parses PDF streams to catch graphic editing software signatures (`Canva`, `Adobe Photoshop`, `Illustrator`) and `ModDate < CreationDate` anomalies.
- **Error Level Analysis (ELA)**: OpenCV pixel-wise variance matrices highlight localized compression anomalies (e.g., splicing `1.75` into `2.10` acres).
- **Deduplication Engine**: Uses SHA-256 for identical byte reuse and 64-bit perceptual `dHash` to catch certificates cloned across institutions.

### 5. Original Issuing-Authority Verification
- **Automated Registry Connectors**: Interfaces with State Land Records (**Bhulekh**), **DigiLocker NAD** (degrees), and **MCA21** (corporate/trust registry).
- **Status Hierarchy**: Classifies queries into `VERIFIED`, `MISMATCH_DETECTED`, `SOURCE_UNAVAILABLE`, and `MANUAL_REVIEW_REQUIRED`.
- **Side-by-Side Diffing**: Highlights discrepancies between institutional application claims and official state database records.

### 6. Regulatory Compliance Engine (Formal SMT Logic)
- **Z3 Rule Conflict Finder**: Formulates rules as mathematical constraints and checks $\exists \vec{x} : (R_A(\vec{x}) \land \neg R_B(\vec{x}))$ to detect circular contradictions without explicit repeals.
- **Counterexample Models**: Extracts values (e.g., $x = 2.0\text{ acres}$) where an institution meets a circular but violates the Handbook, halting automated rejection.
- **Zero Hallucinations**: Generates legally enforceable audit conclusions with exact APH clause citations.

### 7. Infrastructure Compliance Assistance
- **Computer Vision Blueprint Geometry**: OpenCV contour and Hough line transforms verify room counts and enforce the $\ge 66\text{ sqm}$ classroom norm.
- **EXIF Geotag Verification**: Extracts GPS coordinates from campus photographs and computes Haversine distance against the land parcel centroid to detect remote or stock photos.

### 8. Officer Dashboard & Reporting
- **Multi-Page Enterprise Interface**: Dedicated routes for Command Center (`/`), Split-Screen Scrutiny (`/scrutiny/[id]`), Evidence Graph (`/evidence-graph`), Timeline DAG (`/timeline-dag`), Attack Lab (`/attack-lab`), and Rules Matrix (`/rules-matrix`).
- **Court-Admissible PDF Officer Brief**: Server-side ReportLab compiler generates official PDF briefs with digital attestations and deficiency ledgers.

### 9. Human Review, Audit Trail & Security
- **Role-Based Access Control (RBAC)**: Distinct permission tiers for College Nodal Officers, AICTE Scrutiny Officers, and Regional Directors.
- **Statutory Deficiency Notices**: Formal 15-day rectification notices dispatched directly through the platform.
- **Precedence Overrides**: Full audit log tracking officer justifications for circular overrides.
- **Final Human Authority**: Automated engines act as decision-support; legal approvals remain exclusively with authorized officials.

---

## 🛠️ Technology Stack

| Layer | Technology | Function |
|---|---|---|
| **Frontend UI** | Next.js 16 (App Router), React 19, Tailwind CSS 4, Lucide | Responsive, spacious, high-aesthetic dark-mode interface with zero visual clumping. |
| **Backend API** | FastAPI (Python 3.14), Uvicorn | High-performance asynchronous REST API with automatic OpenAPI documentation. |
| **Formal Logic Engine** | Microsoft Z3 Theorem Prover | SMT solver for regulatory constraint validation and circular contradiction detection. |
| **Temporal Logic** | Allen's Interval Algebra | Directed Acyclic Graph (DAG) for chronological impossibility detection. |
| **Document Forensics** | PyMuPDF, OpenCV, PIL, hashlib | Metadata stream analysis, Error Level Analysis (ELA), and perceptual dHash. |
| **Report Generation** | ReportLab | Compiles court-admissible PDF Officer Briefs with embedded citations. |

---

## ⚡ Quick Start & Running Locally

### 1. Prerequisites
- Python 3.11+
- Node.js v18+ & npm

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn api.gateway:app --port 8000 --reload
```
API Documentation will be live at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev -- -p 3000
```
Web Application will be live at: [http://localhost:3000](http://localhost:3000)

### 4. Running Unit Tests
```bash
cd backend
python -m pytest tests/test_engines.py -v
python -m pytest tests/test_api.py -v
```

---

## 🏛️ Project Directory Structure

```
Sakshya/
├── backend/
│   ├── api/
│   │   ├── gateway.py               # Main FastAPI routes, auth, PDF streaming & uploads
│   │   └── sample_data.py           # Benchmark applications (genuine vs tampered)
│   ├── services/
│   │   ├── rule_solver/             # Microsoft Z3 SMT solver & APH rule matrix
│   │   ├── timeline_engine/         # Allen's Interval Algebra DAG engine
│   │   ├── forensics_engine/        # OpenCV ELA, PyMuPDF metadata & dHash deduplication
│   │   ├── extraction_engine/       # Spatial OCR & bounding-box entity extractor
│   │   ├── verification_gateway/    # Bhulekh Land Records & DigiLocker NAD adapters
│   │   ├── infrastructure_cv/       # EXIF GPS verifier & blueprint contour analyzer
│   │   ├── report_generator/        # Court-admissible PDF Officer Brief compiler
│   │   └── audit_trail/             # Event-sourced audit ledger & deficiency notices
│   ├── tests/                       # Automated pytest test suites
│   ├── main.py                      # Backend launcher
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx             # 1. Command Center & National Application Queue
│   │   │   ├── scrutiny/[id]/       # 2. Split-Screen Document Canvas & Bounding Boxes
│   │   │   ├── evidence-graph/      # 3. Interactive Multi-Hop Entity Knowledge Graph
│   │   │   ├── timeline-dag/        # 4. Chronological Impossibility DAG Flowchart
│   │   │   ├── attack-lab/          # 5. Forensic Attack Lab & Adversarial Benchmark
│   │   │   ├── rules-matrix/        # 6. Z3 SMT Rule Conflict Matrix
│   │   │   ├── authority-gateway/   # 7. Issuing Authority Live Sandbox
│   │   │   └── audit-ledger/        # 8. Legal Audit Ledger & Deficiency Notices
│   │   └── components/
│   │       └── SidebarLayout.tsx    # Shared enterprise sidebar layout
│   └── package.json
└── README.md
```

---

## ⚖️ Legal & Government Compliance Disclaimer

Sakshya is built as a **decision-support platform** for government bodies (AICTE, State Technical Boards). Automated verification results, mathematical proofs, and forensic heatmaps are generated to assist regulatory scrutiny committees. Final statutory approval or rejection authority remains exclusively with authorized scrutiny officers pursuant to the AICTE Act.
