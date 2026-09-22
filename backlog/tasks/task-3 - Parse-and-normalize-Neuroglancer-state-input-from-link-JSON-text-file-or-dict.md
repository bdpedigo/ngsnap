---
id: TASK-3
title: >-
  Parse and normalize Neuroglancer state input from link, JSON text, file, or
  dict
status: To Do
assignee: []
created_date: '2026-09-22 19:31'
labels: []
milestone: m-1
dependencies: []
priority: high
type: feature
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every entry point in the package (render, cache key, templating, CLI) takes "a Neuroglancer link or JSON state" (P2). Blog authors paste links from several Neuroglancer hosts (neuroglancer-demo.appspot.com, spelunker, institute deployments), and links use Neuroglancer's URL-safe JSON variant with single quotes and underscores. Some links carry a `#!` fragment with inline JSON, others point at a JSON state URL. A single normalization step keeps that mess out of every other module and gives the cache key a canonical input.

The `neuroglancer.url_state` module already parses fragments and round-trips to URLs, so this task is a thin, well-tested layer over it that also handles file paths, raw JSON strings, and Python dicts, and produces one consistent error type for bad input (P8).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A single public function accepts a Neuroglancer URL, a JSON string, a path to a JSON file, a dict, or a neuroglancer ViewerState and returns a ViewerState
- [ ] #2 URLs from at least three different Neuroglancer host prefixes parse to the same state when they carry the same fragment
- [ ] #3 Links whose fragment is a URL to a remote JSON state are either fetched or rejected with a clear error, and the choice is documented
- [ ] #4 Malformed input raises one package-specific exception with a message that names what was wrong
- [ ] #5 A state can be encoded back to a URL with a configurable host prefix, and parse then encode then parse round-trips to an equal state
- [ ] #6 Unit tests cover each input kind and each failure mode without a browser
<!-- AC:END -->
