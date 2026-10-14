# Ride Hailing Backend

A modular FastAPI monolith for a ride-hailing domain using in-memory repositories.

## Features

- User registration and profile management
- Driver registration, location updates, and availability tracking
- Driver matching using geospatial proximity and fallback rules
- Configurable marginal tier pricing and minimum fare enforcement
- Coupon creation, deletion, validation, and discount application at booking
- Ride lifecycle: creation, assignment, cancellation, and completion
- User and driver ride histories
- Request IDs and structured JSON request/error logs

## Assumptions

- Distance is straight-line Haversine distance between pickup and destination.
- Tiers are marginal: each rate applies only to the distance within its tier.
- Sedan rates follow the assignment: ₹10/km for the first 2 km, ₹8/km for km 3–5, then ₹5/km.
- The assignment does not specify Hatchback rates. This implementation assumes ₹8/km, ₹6/km, and ₹4/km for the same respective tiers.
- The minimum fare is applied before coupon discounting.
- Coupons are percentage discounts, validated and applied when a ride is booked.
- If a requested Hatchback is unavailable, a Sedan may be assigned; the fare remains based on the requested Hatchback class.
- The default matching radius is 5 km. Matching is nearest eligible driver, with exact vehicle matches preferred and Sedan fallback for Hatchback requests.
- Ride cancellation is included as an extra; there is currently no cancellation fee.
- Data is in-memory and resets when the process restarts. The matching lock protects only threads in one process, not multiple workers.

Pricing thresholds, rates, minimum fare, and search radius are centralized in `app/core/config.py`; the pricing calculator accepts a settings object so schedules can be changed or extended without changing its tier calculation.

## Key design decisions and trade-offs

- **Layered design:** FastAPI routers handle HTTP validation and response mapping; services own business rules; repository interfaces isolate storage; domain models represent users, drivers, rides, and coupons. This keeps booking and pricing logic testable without making the API layer responsible for business decisions.
- **Driver matching:** choose the nearest available driver within the configured radius, preferring an exact vehicle match; if a Hatchback was requested and none is available, a Sedan is the free fallback. A process-local lock protects in-memory driver claims between threads, but does not coordinate multiple worker processes.
- **Storage:** in-memory repositories avoid database setup and suit the assignment's short time limit, but data is lost on restart and is not shared across processes.
- **Pricing:** use a configurable marginal-tier calculator and a separately applied coupon discount. Haversine distance is a practical approximation for this exercise, not a road-route distance.

## What I would improve with more time

I would replace in-memory storage with a database, use transactional/atomic driver claims that work across processes, move settings to environment-backed configuration, and add authentication and authorization. I would expand API tests around validation failures and concurrent booking. I would consider surge pricing and cancellation fees only after confirming their policies; neither is part of the current behavior.

## AI collaboration

AI was used to scaffold and iterate on service, API, and test code. Prompts included “go by service by service,” “why we have hardcoded values in the code,” and “complete the rest of the code.” I reviewed the generated implementation against the assignment requirements and tested the behavior.

I rewrote inline pricing assumptions into named configuration instead of leaving them as scattered constants. I also corrected the initial upgrade fare calculation: charging the Sedan rate when assigning a Sedan to a Hatchback request would violate the “free upgrade” requirement, so the fare now remains based on the requested Hatchback class. Regression tests verify this behavior. I did not accept generated code without reviewing and testing it against the requirements.

**Code ownership check before submission:** The developer should review every file, be able to explain each implementation choice, and rewrite or remove anything they cannot explain. AI-generated output is a draft, not a substitute for understanding or verification.

**Commit history:** The implementation is organized in focused feature commits for review. These commits group the completed work and do not reconstruct its original development timeline.

## Run locally

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn pydantic pytest httpx
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest -q
```

## API overview

All application endpoints use the `/api/v1` prefix.

- `POST /api/v1/users`
- `POST /api/v1/drivers`
- `PATCH /api/v1/drivers/{driver_id}/location`
- `POST /api/v1/rides`
- `GET /api/v1/rides/{ride_id}`
- `GET /api/v1/rides/users/{rider_id}`
- `GET /api/v1/rides/drivers/{driver_id}`
- `PATCH /api/v1/rides/{ride_id}/complete`
- `PATCH /api/v1/rides/{ride_id}/cancel`
- `POST /api/v1/coupons`
- `GET /api/v1/coupons`
- `GET /api/v1/coupons/{code}`
- `DELETE /api/v1/coupons/{code}`
