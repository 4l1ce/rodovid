# Privacy Policy — rodovid-agent

Last updated: 2026-11-12

rodovid-agent is a Claude plugin made of skills, agents and local Python
scripts. It has no server, no telemetry and no account of its own. The
publisher receives no data from the plugin or its users.

## What the plugin reads

- Names, dates, places and family relationships of people recorded in
  archival sources (metric books, confession registers, revision lists,
  censuses). These are overwhelmingly people who died long ago.
- Files the user gives it: transcribed xlsx indexes, scans, earlier case
  notes.
- For archive-request drafts only: the user's own name and contact details,
  as the user provides them.

Living people are not researched, and are not added to shared family trees.

## Where data is stored

Only in files on the user's own machine or in the user's project: xlsx
indexes and the evidence ledger, markdown case notes, and request drafts.
The user can delete these files at any time. The plugin keeps no other
copy.

## External services

The plugin works through the user's own browser (Claude in Chrome or
Claude's built-in browser), using the sites' normal pages:

| Service | What is sent | When |
|---|---|---|
| FamilySearch (familysearch.org) | Search terms (names, places, years); page views of catalog items and images | Searching records and reading scans |
| FamilySearch Family Tree | People, relationships and source citations | Only after the user explicitly approves each change |
| Archive websites (the oblast state archive for the place, e.g. ДАЧО, ДАКО; ЦДІАК, ЦДІАЛ), Wikisource, Wikimedia Commons | Search terms and page views | Building the source inventory |

Each service handles this data under its own privacy policy. The plugin
never reads cookies or session tokens, never calls a site's internal APIs
and never enters passwords. Archive requests are drafted only; the user
sends them.

Conversations with Claude are handled by Anthropic under Anthropic's
privacy policy, not by this plugin.

## Contact

Questions about this policy: open an issue at
https://github.com/4l1ce/rodovid/issues
