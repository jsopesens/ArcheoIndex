# ArcheoIndex

This software is a Django-based web application designed to browse, search, and visualize an archaeological keyword thesaurus: **ArcheoIndex**. The application parses and queries hierarchical thesaurus data represented in SKOS (Simple Knowledge Organization System) format.

---

## Features

- **Thesaurus Browsing**: Interactive tree/hierarchy navigation of Concept Schemes and terms.
- **Dynamic Child Loading**: Asynchronously fetches and displays child concepts (narrower terms) via AJAX.
- **Keyword Search**: Quick search endpoint that matches labels dynamically.
- **Detailed Term Views**: Displays complete information for any given keyword, including descriptions (definitions, alternative/preferred labels) and semantic relationships (broader, narrower, related terms).

---

## Technology Stack

- **Backend**: Python 3, [Django](https://www.djangoproject.com/) 4.2+
- **RDF/SKOS SSoT**: [RDFLib](https://github.com/RDFLib/rdflib) (for loading and querying SKOS Turtle `.ttl` files)
- **Frontend**: Vanilla HTML5, CSS3, and JavaScript (AJAX/Fetch API)

---

## Directory Structure

```text
ArcheoIndex/
├── ArcheoIndex_thesaurus.ttl   # SKOS thesaurus definition in Turtle format
├── thesaurus_test.ttl          # SKOS thesaurus with predictible content to unit testing
├── README.md                   # Project documentation
├── requirements.txt            # Libraries required to execute the software
├── .env.example                # Example of enviromental configuration
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

# Activate the virtual environment:
#   on Linux
source venv/bin/activate
#   on Windows
source venv\Scripts\Activate.ps1

```

### 4. Install Dependencies
Install Django and RDFLib using `pip`:
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy the example configuration file and adjust the values if necessary:

```bash
cp .env.example .env
```

### 6. Deploy on production
Collect static files (production):

```bash
py manage.py collectstatic
```

---

## Running the Application

The default configuration loads `ArcheoIndex_thesaurus.ttl` through `THESAURUS_PATH` in `archeoindex/settings.py`:

```bash
cd archeoindex
py manage.py runserver
```

Once the server is running, access the web interface in your browser at:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## Tests

The test suite uses a small, self-contained SKOS fixture instead of the production thesaurus:

- `thesaurus_test.ttl` contains the test concepts (currently 19), with the base URI `http://test_thesaurus.org#`.
- `archeoindex/settings_test.py` inherits the normal Django settings and replaces `THESAURUS_PATH` and `THESAURUS_URI` with `TEST_THESAURUS_PATH` and `TEST_THESAURUS_URI`.
- `keywords/tests.py` contains unit tests for `Concept` and the RDF graph access helpers.

Run the suite from the Django project directory:

```bash
cd archeoindex
py manage.py test --settings=archeoindex.settings_test
```

When adding tests, use concept identifiers that exist in `thesaurus_test.ttl`.

---

## Key Modules

- **`keywords/thesaurus.py`**: Contains the `Thesaurus` helper class. It initializes an RDFLib Graph, parses `ArcheoIndex_thesaurus.ttl`, and exposes helper methods to query concepts, labels, and relationships.
- **`keywords/views.py`**:
  - `index`: Renders the thesaurus hierarchy landing page.
  - `single_keyword`: Renders details for a specific keyword.
  - `get_children_of`: JSON endpoint returning narrower concepts for a parent term.
  - `get_match_keywords`: JSON endpoint for keyword search matching.


## Expected Naming Conventions in thesaurus file
The ttl file (or any other format for the controlled vocabulary) have to include some controlled vocabulary as:
 - skos:Concept
 - skos:notation
 - skos:definition
 - skos:prefLabel
 - skos:inScheme
 - skos:broader
 - skos:narrower

Even the software is prepared to interact with this syntaxis, it is possible to adapt **`Concept.py`** to interact with other syntax presented in [skos documentation](https://www.w3.org/2009/08/skos-reference/skos.html).

## Automated Contributions Policy (No Bots Allowed)

To maintain project quality and prevent automated noise, **this repository strictly prohibits any issues, discussions, or pull requests generated or submitted automatically by bots, AI agents, or automated scripts**.

* **No Automated PRs:** Do not use automated tools to mass-submit dependency updates, typo fixes, or code formatting without prior human review and manual submission.
* **No AI-Generated Issues:** Issues must be written and thoroughly verified by a human. Purely automated or AI-scraped bug reports will be closed immediately.
* **Consequences:** Any automated interaction that violates these rules will be closed, flagged as spam, and the executing account/IP may be blocked from this organization.
