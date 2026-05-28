# ArcheoIndex

ArcheoIndex is a Django-based web application designed to browse, search, and visualize an archaeological keyword thesaurus. The application parses and queries hierarchical thesaurus data represented in SKOS (Simple Knowledge Organization System) format.

---

## Features

- **Thesaurus Browsing**: Interactive tree/hierarchy navigation of Concept Schemes and terms.
- **Dynamic Child Loading**: Asynchronously fetches and displays child concepts (narrower terms) via AJAX.
- **Keyword Search**: Quick search endpoint that matches labels dynamically.
- **Detailed Term Views**: Displays complete information for any given keyword, including descriptions (definitions, alternative/preferred labels) and semantic relationships (broader, narrower, related terms).

---

## Technology Stack

- **Backend**: Python 3, [Django](https://www.djangoproject.com/) 4.2+
- **RDF/SKOS Parsing**: [RDFLib](https://github.com/RDFLib/rdflib) (for loading and querying SKOS Turtle `.ttl` files)
- **Frontend**: Vanilla HTML5, CSS3, and JavaScript (AJAX/Fetch API)
- **Database**: SQLite (built-in Django settings, though primary metadata queries run against the RDF graph)

---

## Directory Structure

```text
ArcheoIndex/
├── ArcheoIndex_thesaurus.ttl   # SKOS thesaurus definition in Turtle format
├── README.md                   # Project documentation
└── archeoindex/                # Django project root
    ├── db.sqlite3              # Local SQLite database
    ├── manage.py               # Django management script
    ├── archeoindex/            # Project configuration
    │   ├── settings.py         # Main Django settings
    │   ├── urls.py             # Root URL routing
    │   ├── wsgi.py / asgi.py   # WSGI/ASGI server configs
    └── keywords/               # Thesaurus search and browsing application
        ├── thesaurus.py        # RDFLib SKOS parser wrapper class
        ├── views.py            # App views and JSON APIs
        ├── urls.py             # Routing for the keywords app
        ├── templates/
        │   └── keywords/
        │       ├── layout.html         # Base template layout
        │       ├── index.html          # Main thesaurus browser page
        │       └── single_keyword.html # Detailed view for individual keywords
        └── static/
            └── keywords/
                ├── styles.css          # Base styles
                ├── header.css          # Navigation and header styles
                ├── landing_body.css    # Landing page layout stylesheet
                ├── single_keyword.css  # Term detail page stylesheet
                └── js/
                    ├── main.js         # Core frontend JS
                    └── landing.js      # Thesaurus tree interaction JS
```

---

## Local Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed. Check your version with:
```bash
python3 --version
```

### 2. Clone and Navigate
Clone the repository and navigate to the project root directory:
```bash
git clone https://github.com/your-username/ArcheoIndex.git
cd ArcheoIndex
```

### 3. Create a Virtual Environment
It is highly recommended to isolate project dependencies using a virtual environment:
```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```
*(On Windows PowerShell, use: `venv\Scripts\Activate.ps1`)*

### 4. Install Dependencies
Install Django and RDFLib using `pip`:
```bash
pip install django rdflib
```

---

## Running the Application

Because the thesaurus parser (`keywords/thesaurus.py`) loads the SKOS RDF data from `ArcheoIndex_thesaurus.ttl` using a relative path from the current working directory, you **must run the server from the root directory**:

```bash
python archeoindex/manage.py runserver
```

Once the server is running, access the web interface in your browser at:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## Key Modules

- **`keywords/thesaurus.py`**: Contains the `Thesaurus` helper class. It initializes an RDFLib Graph, parses `ArcheoIndex_thesaurus.ttl`, and exposes helper methods to query concepts, labels, and relationships.
- **`keywords/views.py`**:
  - `index`: Renders the thesaurus hierarchy landing page.
  - `single_keyword`: Renders details for a specific keyword.
  - `get_children_of`: JSON endpoint returning narrower concepts for a parent term.
  - `getMatchKeywords`: JSON endpoint for keyword search matching.