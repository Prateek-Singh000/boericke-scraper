\# Boericke's Materia Medica - Web Scraper



This is a Python-based web scraper built for Jarvis Care. It crawls the Boericke's Homoeopathic Materia Medica (A-Z) and extracts the clinical monographs into a structured JSON dataset.



\## Features

\- \*\*Resumability:\*\* Automatically detects existing `boericke\_remedies.json` and skips previously scraped URLs.

\- \*\*Rate Limiting:\*\* Respects the server by implementing a 0.75-second delay between requests.

\- \*\*Error Handling:\*\* Logs failed URLs to `failed\_urls.txt` and continues without crashing.

\- \*\*Clean Data:\*\* Strips HTML, collapses whitespace, and strictly follows the requested JSON schema.



\## Prerequisites

\- Python 3.9+

\- `requests`

\- `beautifulsoup4`



\## Setup Instructions

1\. Clone this repository to your local machine.

2\. Navigate to the project directory:

&#x20;  `cd boericke-scraper`

3\. Create and activate a virtual environment:

&#x20;  `python -m venv venv`

&#x20;  - Windows: `venv\\Scripts\\activate`

&#x20;  - Mac/Linux: `source venv/bin/activate`

4\. Install the required dependencies:

&#x20;  `pip install -r requirements.txt`



\## How to Run

Execute the main script from your terminal:

`python scraper.py`



The scraper will output progress to the console. Once finished, you will find the complete dataset in `boericke\_remedies.json`. Any URLs that failed to process will be listed in `failed\_urls.txt`.

