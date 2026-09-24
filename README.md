# CompliScan LM 🔍
AI-Powered Statutory Label Compliance Inspection System for Legal Metrology

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6.svg?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tests](https://img.shields.io/badge/Test%20Suite-151%20Passed-success.svg?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

---

## 📌 Project Overview

**CompliScan LM** is an end-to-end compliance inspection web application designed to help legal metrology inspectors and quality assurance teams verify product packaging labels against India's **Legal Metrology (Packaged Commodities) Rules, 2011 (LMPC Rules)**.

Instead of manually reading package labels and verifying each statutory rule, CompliScan LM lets inspectors upload photos of product packages. It uses a combination of OCR (PaddleOCR), AI semantic structuring (Gemini 3.6 Flash), and a deterministic rule engine to automatically extract declarations, highlight missing or invalid declarations, and allow officers to review and export official inspection reports.

> **💡 Design Core: Deterministic Statutory Verification**  
> While AI handles reading and structuring packaging text from raw images, all compliance rules and pass/fail determinations are evaluated by a **100% deterministic code engine** to ensure consistency, accuracy, and full transparency.

---

## 🏛️ Statutory Rules Evaluated

CompliScan LM verifies all 7 mandatory declaration domains under **Rule 6(1)** of the *Legal Metrology (Packaged Commodities) Rules, 2011*:

| # | Statutory Declaration | Legal Citation | Verification Rule |
|---|---|---|---|
| 1 | **Manufacturer / Packer / Importer** | `Rule 6(1)(a)` | Checks presence of registered company name and complete postal address. |
| 2 | **Generic / Common Name** | `Rule 6(1)(b)` | Ensures commodity generic name is declared clearly. |
| 3 | **Net Quantity & Unit** | `Rule 6(1)(c)` | Validates standard units (`g`, `kg`, `ml`, `l`, `m`, `N`, `U`) and non-zero numeric quantity. |
| 4 | **Date of Manufacture / Import** | `Rule 6(1)(d)` | Validates mandatory month (`MM`) and year (`YYYY`) formatting and date plausibility. |
| 5 | **Maximum Retail Price (MRP)** | `Rule 6(1)(e)` | Verifies price structure and mandatory `"inclusive of all taxes"` statement. |
| 6 | **Consumer Care Details** | `Rule 6(1)(f)` | Checks for valid phone/helpline, email, physical address, or designated contact officer. |
| 7 | **Country of Origin** | `Rule 6(1)(da)` | Checked for imported commodities (mandatory under G.S.R. 629(E); exempt for domestic goods). |

---

## 🚀 Main Features

- **📸 Image Quality & Perception Pipeline**:
  - **Quality Gating**: Screens uploaded photos for severe blur, lighting, and resolution issues before processing.
  - **PaddleOCR Engine**: Extracts raw text blocks and bounding polygon coordinates locally using PP-OCRv4.
  - **Gemini 3.6 Flash Structuring**: Maps extracted OCR tokens to standardized legal declaration fields.
  - **Offline Fallback Parser**: Includes a regex heuristic parser that works even when cloud AI services are unavailable.

- **🔍 Interactive Inspector Workspace**:
  - Bounding box visualizer overlaid directly on package image scans.
  - Interactive table showing extracted fields, confidence scores, and raw source text.
  - Ability for inspectors to manual edit or correct extracted values before finalizing.

- **🔄 Multi-Angle Synthesis**:
  - Combines evidence across multiple packaging photos (front, back, side panels) to form a complete package profile.

- **👥 Officer Review & Adjudication**:
  - Two-stage workflow for field inspectors and senior reviewing officers to review, comment, and sign off on inspections.

- **📄 Report Export**:
  - Generates downloadable **PDF & DOCX statutory inspection reports** complete with summary tables, evidence links, and cryptographic SHA-256 checksum seals for tamper verification.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Package Photos] --> B[Quality Screening Gate]
    B -->|Pass| C[PaddleOCR Text Detection]
    B -->|Fail| D[Quality Warning / Resubmit Prompt]
    C --> E{Extraction Engine}
    E -->|Online| F[Gemini 3.6 Flash Structuring]
    E -->|Offline| G[Regex Heuristic Parser]
    F --> H[Multi-Image Evidence Synthesizer]
    G --> H
    H --> I[Rule 6(1) Deterministic Compliance Engine]
    I --> J[Inspector Workspace & Review Panel]
    J --> K[Officer Sign-Off & Case Finalization]
    K --> L[Export PDF / DOCX Inspection Reports]
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **Database**: SQLite / PostgreSQL with SQLAlchemy 2.0 (Asyncio)
- **OCR & Computer Vision**: PaddleOCR (PP-OCRv4 ONNX), OpenCV, Pillow
- **AI Integration**: Google GenAI SDK (`gemini-3.6-flash`)
- **Report Generation**: ReportLab (PDF) & `python-docx` (DOCX)
- **Testing**: Pytest (151 unit & integration tests)

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 5
- **UI & Styling**: Vanilla CSS & Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios

---

## 📦 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+ & npm
- Git

---

### 1. Clone the Repository
```bash
git clone https://github.com/aryaveerz/CompliScan.git
cd CompliScan
```

---

### 2. Backend Setup

1. Create and activate a Python virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install backend dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Configure environment variables in a `.env` file at the root:
   ```env
   DATABASE_URL=sqlite+aiosqlite:///./compliscan.db
   SYNC_DATABASE_URL=sqlite:///./compliscan.db
   SECRET_KEY=dev_secret_key_change_in_production
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. Initialize the database and run the server:
   ```bash
   python -m backend.app.db.init_db
   uvicorn backend.app.main:app --reload --port 8000
   ```
   *API documentation will be available at `http://localhost:8000/docs`.*

---

### 3. Frontend Setup

1. Navigate to the frontend directory and install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *Open `http://localhost:5173` in your browser.*

---

## 🧪 Running Tests

Run the full backend test suite with Pytest:

```bash
python -m pytest backend/tests/ -v
```

All 151 unit and integration tests cover OCR extraction, rule evaluation, multi-evidence synthesis, report generation, and API authorization.

---

## 📂 Project Structure

```
CompliScan/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST API endpoints (auth, inspections, compliance, reports)
│   │   ├── core/            # Config, security, error handlers
│   │   ├── db/              # SQLAlchemy database models & sessions
│   │   ├── schemas/         # Pydantic validation schemas
│   │   └── services/        # OCR, extraction, compliance engine, PDF generator
│   └── tests/               # Pytest test suite (151 tests)
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components & image bounding box viewer
│   │   ├── pages/           # Inspection workspace, dashboard, review queue
│   │   ├── services/        # API client modules
│   │   └── types/           # TypeScript interfaces
├── shared/                  # Common legal rule definitions & enums
└── README.md
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
