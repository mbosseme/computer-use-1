# Graph Search Diagnostics

Generated: 2026-03-05T14:16:56.474795+00:00

## Mailbox History Access
- Pages fetched: 24
- Messages fetched: 6000
- Newest message: 2026-03-05T14:13:42+00:00
- Oldest message in sample window: 2025-12-12T16:23:31+00:00

## Long-History Probe
- Pages fetched: 108
- Messages fetched: 26815
- Oldest message reached: 2022-02-15T21:25:48+00:00

## Older Date Slice Retrieval
- Filter: receivedDateTime < 2024-01-01T00:00:00Z
- Count: 26
- Sample: Weekly 1:1 - Audrey, Weekly 1:1 - Audrey, Weekly 1:1 - Audrey, Weekly 1:1 - Audrey, Weekly 1:1 - Audrey

## AQS Search ($search on messages)
- Query: `"Clarivate"` | folder=None | count=60 | unique_ids=60
  - Sample: Quick heads‑up on market intelligence coverage, Re: Reaching Out to Carrie, RE: Reaching Out to Carrie
- Query: `"forvis"` | folder=None | count=25 | unique_ids=25
  - Sample: Re: ABI Platform - Experimentation Artifact Request, RE: ABI Platform - Experimentation Artifact Request, RE: Premier R&D Tax Credit – FY2025 Project Qualification & Documentation Request
- Query: `"Revenue AI Agent"` | folder=None | count=60 | unique_ids=60
  - Sample: End User Digest: 13 New Messages , Re: McKinsey Product Codes, RE: McKinsey Product Codes
- Query: `subject:"Revenue AI Agent"` | folder=None | count=0 | unique_ids=0
  - Error: Graph GET me/messages failed: 400 {"error":{"code":"BadRequest","message":"Syntax error: character ':' is not valid at position 7 in 'subject:\"Revenue AI Agent\"'.","innerError":{"date":"2026-03-05T14:15:41","request-id":"7fae739c-c1d0-4ae7-8dcb-8466cc014ef1","client-request-id":"7fae739c-c1d0-4ae7-8dcb-8466cc014ef1"}}}
  - Sample: 
- Query: `"Copilot"` | folder=Inbox | count=60 | unique_ids=60
  - Sample: Re: GitHub Copilot Workshop #1, Re: GitHub Copilot Workshop #1, Re: GitHub Copilot Workshop #1
- Query: `"Copilot"` | folder=SentItems | count=60 | unique_ids=60
  - Sample: Re: GitHub Copilot Workshop #1, Re: GitHub Copilot Workshop #1, Re: GitHub Copilot Workshop #1

## Graph Search API (/search/query) — Messages
- Query: `Clarivate` | count=25
  - Sample: Quick heads‑up on market intelligence coverage, Re: Reaching Out to Carrie, RE: Reaching Out to Carrie
- Query: `Revenue AI Agent` | count=25
  - Sample: End User Digest: 13 New Messages , Re: McKinsey Product Codes, RE: McKinsey Product Codes
- Query: `Forvis IRS` | count=5
  - Sample: Re: ABI Platform - Experimentation Artifact Request, RE: ABI Platform - Experimentation Artifact Request, Re: ABI Platform - Experimentation Artifact Request

## Graph Search API (/search/query) — Events
- Query: `Clarivate` | count=18
  - Sample: Re: Clarivate: Enterprise Bundle: Guidance & Review (Final Pass), Premier x Clarivate Discussion , Clarivate Negotiation
- Query: `Copilot` | count=24
  - Sample: Copilot Studio Lite & SharePoint Agents, Microsoft Copilot : Introduction to First Party Agents, Copilot Chat Training #3
- Query: `Forvis` | count=0
  - Sample: 

## Meeting Invite Bodies Access
- Error: Graph GET me/messages failed: 400 {"error":{"code":"RequestBroker--ParseUri","message":"Could not find a property named 'messageClass' on type 'Microsoft.OutlookServices.Message'.","innerError":{"date":"2026-03-05T14:15:53","request-id":"29e86a27-97c8-4ea2-b6ae-0550697cae6a","client-request-id":"29e86a27-97c8-4ea2-b6ae-0550697cae6a"}}}

## Calendar Event Body Preview Access
- Events fetched: 100
- Events with bodyPreview: 87
- Sample: 'Growth' Project: Analysis Primers Workshop (Rx + Clinical), 'Growth' Project: Analysis Primers Workshop (Non-Clinical + Food), *PLACEHOLD* 'Growth' Project: Analysis Primers Workshop (Final Group), Project Catalyst - Team Status Update (Bi-Weekly), Watch Kids

## Local Keyword Scan (Index-Independent)
- Pages scanned: 108
- Messages scanned: 26815
- Query terms: `revenue ai agent` | matches=2
  - Sample: Re: Revenue AI Agent - Demo , RE: Revenue AI Agent - Demo 
- Query terms: `forvis` | matches=5
  - Sample: RE: ABI Platform - Experimentation Artifact Request, RE: ABI Platform - Experimentation Artifact Request, FW: ABI Platform - Experimentation Artifact Request
- Query terms: `irs audit` | matches=0
  - Sample: 
- Query terms: `clarivate` | matches=5
  - Sample: , Re: Clarivate: what they likely do today with Premier MI purchasing + item master feeds (and why it matters for Mar 31 cutover), Re: Clarivate: what they likely do today with Premier MI purchasing + item master feeds (and why it matters for Mar 31 cutover)
- Query terms: `copilot workshop` | matches=5
  - Sample: Re: GitHub Copilot Workshop #1, Re: GitHub Copilot Workshop #1, Re: GitHub Copilot Workshop #1
