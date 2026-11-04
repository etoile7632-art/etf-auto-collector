# ETF PCF Collector — initial scaffold (not production ready)

This repository contains a **safe starting framework**, not a functioning six-fund live scraper. Source URLs, field mappings and as-of dates must be verified from each manager's actual published data before use. An empty source list yields `PENDING`, **never** a fabricated zero-change result.

## Setup
1. Create a GitHub repository and upload the contents, including `.github/workflows/collect.yml`.
2. In Actions, run `ETF PCF collector` manually to verify the workflow. Initial output will be 0/6 verified by design.
3. Verify each fund's official ISIN/ticker and approved PCF source. Configure a source with `url`, `format` (`csv` or `json`), `mapping` (`ticker`, `name`, `weight` field names), and an **explicit source-derived** `asof` date. Never hardcode today's date as the holdings date. Production adapters should extract date from the official response.
4. Confirm data rights, source access, exchange trading calendar, source date and per-fund data integrity before enabling publication.
5. Connect the verified JSON to the existing website only after its deployment API and JSON schema have been validated.

## Security and limitations
- Public repository snapshots are public. Do not include credentials, private information or copyrighted datasets without permission.
- GitHub Actions cron uses UTC and may run late or be skipped. The workflow targets 08:15 KST Monday–Friday; it is not a guaranteed SLA.
- GitHub Actions and storage have usage limits. Free usage depends on repository visibility and GitHub plan.
- This project does not yet implement scraping of JavaScript sites, date extraction, comparison logic, holiday checks, site publishing, or the existing master JSON schema.
- Missing data must remain `PENDING` and must not be interpreted as unchanged holdings.
