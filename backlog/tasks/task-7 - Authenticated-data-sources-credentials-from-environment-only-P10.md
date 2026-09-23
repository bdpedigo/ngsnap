---
id: TASK-7
title: 'Authenticated data sources: credentials from environment only (P10)'
status: To Do
assignee: []
created_date: '2026-09-22 19:32'
updated_date: '2026-09-22 21:58'
labels: []
milestone: m-2
dependencies:
  - TASK-3
priority: medium
type: feature
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The datasets the team uses are not all public. Some are behind Google Cloud Storage permissions or CAVE and graphene endpoints that need a token. In the interactive viewer the browser prompts for a login; on a CI runner nobody is there to click. The package must pick up credentials from the environment and hand them to Neuroglancer, and must never write them to disk or embed them in output (P10).

The neuroglancer Python package routes credential requests from the client back to the Python server through `neuroglancer.default_credentials_manager`, with providers for Google, BOSS, and DVID. The task is to inventory which source types the team actually needs, confirm which the existing manager handles, add a token-from-environment path for the rest, and document the required variables. Needs the render backend from task-1 to test end to end.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The data source types the team uses are listed in the README with the environment variable each one needs
- [ ] #2 A state that references a protected source renders successfully in CI when the documented variables are set
- [ ] #3 The same state fails with an error that names the source and the missing credential when the variables are absent
- [ ] #4 No credential value appears in logs, in the output image metadata, or in any file the package writes
- [ ] #5 parse_state resolves auth-backed remote state links (e.g. middleauth+https:// CAVE state-server URLs) by fetching the state JSON with a token from the environment via caveclient, and raises StateInputError naming the source and missing credential when the token is absent
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Scope addition (per user, follow-on to TASK-3): TASK-3 currently rejects auth-backed remote state fragments (middleauth+, gs://) in parse_state with a clear StateInputError and a NOTE pointing here. This task now also owns the parse-layer fetch of the state document itself (not just data-source credentials during render): resolve middleauth+ CAVE state-server links via caveclient using an env token, honoring the same env-only, never-on-disk credential rules (P10). Reuse the same env variables documented for CAVE data sources.
<!-- SECTION:NOTES:END -->
