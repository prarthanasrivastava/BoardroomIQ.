# BoardroomIQ

BoardroomIQ is an autonomous multi-agent business intelligence platform that analyzes uploaded business CSVs, debates evidence, verifies claims, and produces explainable executive recommendations.

## MVP Features

- Upload or use sample datasets for sales, customers, inventory, and marketing.
- Upload one or more CSV/Excel files and let BoardroomIQ decide which agents can run.
- Analyze single business sheets such as customer onboarding, bookings, conversions, and CAC.
- Run specialized Finance, Marketing, Operations, and Risk agents.
- Generate a board meeting timeline from planning to CEO summary.
- Debate and verify agent claims using computed evidence.
- Rank likely causes with confidence scores.
- Forecast near-term revenue and inventory risk with simple trend analytics.

## How To Run The Streamlit MVP

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How To Run The Product UI

Start the FastAPI backend:

```bash
.\.venv\Scripts\python.exe -m uvicorn boardroomiq.api:app --reload --port 8000
```

Start the React frontend in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

On Windows PowerShell, use `npm.cmd` if script execution is blocked:

```powershell
cd frontend
& 'C:\Program Files\nodejs\npm.cmd' install
& 'C:\Program Files\nodejs\npm.cmd' run build
& 'C:\Program Files\nodejs\npm.cmd' run preview -- --port 5173
```

## Expected CSV Inputs

The MVP works best with these columns:

- `sales.csv`: `date`, `product`, `region`, `units_sold`, `revenue`, `cost`
- `customers.csv`: `customer_id`, `region`, `signup_date`, `last_purchase_date`, `repeat_customer`
- `inventory.csv`: `date`, `product`, `stock_level`, `stockout`, `demand`
- `marketing.csv`: `date`, `region`, `campaign`, `spend`, `clicks`, `conversions`

Sample files are included in `data/sample`.

## Flexible Upload Mode

The React + FastAPI version supports:

- `.csv`
- `.xlsx`
- `.xls`
- single-sheet files
- multi-sheet Excel workbooks

BoardroomIQ profiles uploaded columns first. If a user uploads only one onboarding/customer sheet, it can still analyze:

- total booked records
- booked but not converted count
- conversion rate
- status breakdown
- source/channel distribution
- CAC when both spend and conversion columns exist
- timeline dips when a date column exists

Example file: `data/sample/onboarding.csv`.
