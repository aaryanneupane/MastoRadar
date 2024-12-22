
# MastoRadar - The Decentralized Recommender System for Mastodon

MastoRadar provides a decentralized recommender system for Mastodon, allowing users to explore an additional timeline of toots recommended for themselves based on interractions.

Timelines provided on our MastoRadar instance:
- Home timeline - The same as the native timeline of people and hashtags the user follow
- Explore timeline - The same as the native explore timeline
- MastoRadar timeline - A content-based filtering recommender system fetching recommended toots for the user
- Recommended Ultra - A keyword extraction recommender system fetching recommended toots for the user

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the backend requirements and the package manager [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) to install the frontend requirements.


Frontend:
```bash
cd frontend
npm install
npm run build
```

## Usage

Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate (MAC)
.\venv\Scripts\activate (WIN)
pip install -r requirements.txt
fastapi dev app.py
```

Frontend:
```bash
cd frontend
npm run dev
```

Visit http://localhost:5173/ (or http://127.0.0.1:8000 to test the APIs directly)

## Contributing

Pull requests are welcome.

