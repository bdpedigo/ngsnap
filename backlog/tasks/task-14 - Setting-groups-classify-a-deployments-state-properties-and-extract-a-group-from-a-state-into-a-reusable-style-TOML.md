---
id: TASK-14
title: >-
  Setting groups: classify a deployment's state properties and extract a group
  from a state into a reusable style TOML
status: To Do
assignee: []
created_date: '2026-09-22 23:39'
labels: []
dependencies:
  - TASK-5
references:
  - design.md
priority: medium
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Authors want to reuse the "look" of a curated Neuroglancer link across many new links without hand-copying settings. Today a Style (TASK-5) is authored by hand in TOML, and there is no shared vocabulary for which state properties are cosmetic/presentation vs data-source vs view/location-camera for the deployments the team uses. Because of that there is also no way to lift, say, all the cosmetic settings out of an existing good-looking state and save them for later application. This task introduces named setting groups for the current NGL deployment and an extract operation that pulls a chosen group out of a given state and writes it as a Style TOML that Style.from_file can load and apply through the existing templating path. It builds on the same parse (TASK-3) and template/Style (TASK-4, TASK-5) machinery rather than inventing a second mechanism; the extracted TOML is just a Style authored automatically from a source state instead of by hand.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A documented, deployment-scoped classification maps Neuroglancer state properties into named groups covering at least cosmetic/presentation, data source, and view/location-camera
- [ ] #2 Given a state (link, JSON, file, or dict) and a group name, the package returns the subset of that state that belongs to that group
- [ ] #3 The extracted subset can be written to a Style TOML (template/config sections) that `Style.from_file` loads and applies via the existing templating interface, no new merge mechanism
- [ ] #4 A cosmetic extraction excludes non-cosmetic properties such as data sources/layer sources and camera/position
- [ ] #5 Round trip is idempotent: applying the extracted TOML to the source state reproduces the extracted group of properties
- [ ] #6 Properties that are not classified into any group are handled in a documented, predictable way (dropped or flagged, not silently mixed in)
- [ ] #7 Tests cover extracting the cosmetic group from a representative multi-layer state and the extract-then-apply round trip
<!-- AC:END -->
