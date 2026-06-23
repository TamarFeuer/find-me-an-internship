# find-me-an-internship
An AI-powered internship matching agent that fetches job listings from the Adzuna API, scores them against your CV using the Anthropic Claude API, and ranks them by fit. Built with FastAPI backend and a simple frontend for CV upload.

## Tech decisions
- **Frontend: Angular.** Provides a structured, opinionated framework (TypeScript, components, services, `HttpClient`) that fits the "upload CV → view ranked matches" UI well.
