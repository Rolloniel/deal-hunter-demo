# Upwork Job Post: AI Conversational Deal & Travel Monitoring Agent (LLM + Web Monitoring + Alerts)

**Title:** Build an AI Conversational Agent That Recommends & Tracks Products, Flights, and Deals (Modern AI Stack)

## Overview

I'm building a modern AI-powered conversational agent (app and/or browser extension + backend) that allows users to chat naturally with the app to:

- Discover and get recommendations for products, flights, and destinations
- Tell the agent what they want to track (e.g., "Let me know when this TV drops below $900" or "Track flights to Tokyo in March")
- Have the agent monitor the web daily (or via APIs where appropriate)
- Get notified automatically when:
  - A product goes on sale
  - A flight price drops or hits a historical low
  - A deal meets user-defined conditions

The long-term vision is an AI personal deal-hunting agent, but this project is for a **production-quality V1** with a scalable architecture.

---

## Core V1 Features

### 1. Conversational AI Interface (LLM)
- Chat-based UI (web/mobile/extension)
- Users can:
  - Ask for product recommendations ("Best 65-inch OLED TV under $2k")
  - Ask for travel ideas ("Best destinations in Europe in April")
  - Ask for flight suggestions ("Cheapest way to fly to Paris from NYC")
- LLM translates chat intent into structured tracking tasks

### 2. AI Recommendations Engine
Use LLM + structured data to:
- Recommend products (based on budget, brand, category)
- Recommend destinations (seasonality, cost, popularity)
- Recommend flight options (best dates, routes, ranges)
- Explain recommendations clearly (why this option)

### 3. Intelligent Tracking & Monitoring Agent
After recommendations or direct user commands, the agent:
- Creates tracking rules automatically
- Monitors:
  - Product prices (via web pages and/or retailer APIs)
  - Flight prices (via flight data APIs or compliant sources)
- Runs daily scans (V1)

### 4. Price Drop & "Best Time to Buy" Detection
- Store price history
- Detect:
  - Absolute price drops
  - % threshold drops
  - "Lowest seen price" signals
- LLM-generated explanations: "This is the lowest price in the last 60 days."

### 5. Notifications & Alerts
Notify users via:
- Push notifications (preferred)
- Email (backup)

Alert includes:
- What changed
- Old vs new price
- Direct link to buy/book

### 6. User Dashboard
View:
- Active tracked items (products, flights, destinations)
- Current price and history
- Alert conditions
- Manage tracking rules created via chat

---

## Architecture & Tech Expectations (Latest Tech)

I want a modern, scalable AI-agent-style architecture, not a monolithic scraper.

### Backend
- Python (FastAPI) or Node.js (NestJS)
- Event-driven / async architecture
- Clear separation between:
  - Conversation layer
  - Recommendation layer
  - Monitoring/agent execution layer

### AI / LLM
- OpenAI / Anthropic / similar via API
- Agent-style flow:
  - Intent extraction
  - Tool calling (search, scrape, API query)
  - Memory/state per user
  - Prompt + schema-driven outputs (JSON)

### Data
- PostgreSQL (primary)
- Redis (queues, caching, rate limits)
- Time-series friendly schema for price history

### Jobs & Monitoring
- Queue-based schedulers (BullMQ, Celery, Cloud Tasks)
- Retry logic, failure handling, logging
- Observability (basic metrics + alerts)

### Web Monitoring
Combination of:
- Retailer APIs where available
- Headless browsers (Playwright/Puppeteer)
- Third-party scraping APIs (preferred for reliability)
- Anti-bot-aware and compliant approach

### Flights & Travel
- Use real flight data APIs (Amadeus, Skyscanner, Duffel, etc.)
- Avoid unreliable scraping for flights unless explicitly discussed

### Frontend
- Web app (Next.js / React)
- Optional:
  - Mobile app (React Native / Flutter)
  - Browser extension (Chrome MV3)
- Clean conversational UI + dashboard

### Cloud & DevOps
- AWS / GCP preferred
- Containerized (Docker)
- CI/CD
- Secrets management

---

## Deliverables

- Fully working V1 deployed to staging
- Conversational UI + tracking system
- Backend APIs + agent services
- Database schema + migrations
- Price history & alert logic
- Documentation:
  - Architecture overview
  - How to add new "tracker types"
  - How to deploy & scale

---

## What I Expect in Your Proposal

Please include:
- Relevant projects (AI agents, chat apps, scrapers, travel apps, monitoring systems)
- How you would design the conversation → intent → tracking → monitoring loop
- Your approach to:
  - Product matching accuracy
  - Flight price data reliability
- Recommended scraping/API providers and why
- Cost considerations (LLM usage, scraping, APIs)
- A milestone-based delivery plan

---

## Example Milestones

1. System architecture + conversation flow design
2. LLM chat interface + intent extraction
3. Product recommendation + tracking engine
4. Flight API integration + price monitoring
5. Notification system
6. Dashboard, testing, deployment

---

## Required Skills

### Must Have
- Production experience with LLM APIs
- Async backend systems (FastAPI/NestJS)
- Web scraping or data monitoring systems
- Queue-based background jobs
- API integrations (travel, pricing, notifications)

### Strongly Preferred
- AI agent frameworks (LangGraph, CrewAI, custom tool-based agents)
- Travel/flight pricing systems
- Browser extension or mobile app experience
- Affiliate/deep-link monetization experience
