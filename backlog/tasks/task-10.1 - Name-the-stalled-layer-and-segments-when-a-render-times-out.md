---
id: TASK-10.1
title: Name the stalled layer and segments when a render times out
status: To Do
assignee: []
created_date: '2026-09-24 23:53'
labels: []
dependencies: []
references:
  - >-
    https://github.com/google/neuroglancer/blob/master/python/neuroglancer/tool/screenshot.py
parent_task_id: TASK-10
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A figure in the nftn PNN post hung for 600s with no clue why. Bisecting its 17 selected segments showed one (864691136453720831 in gs://iarpa_microns/minnie/minnie65/seg_m1300) that times out even when rendered alone; its mesh appears to be missing from the source, so Neuroglancer never reports the view as loaded. The only evidence was a generic RenderTimeoutError, and finding the cause took manual bisecting. As a stopgap the timeout message now tells authors that missing selected objects can cause timeouts. Neuroglancer tracks chunk load statistics during a screenshot, so a timeout could report what is still loading on any data source, instead of checking mesh sources per format before rendering (which remains a possible later guard).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A render that times out raises RenderTimeoutError whose message names each layer that had not finished loading
- [ ] #2 When a segmentation layer is stuck on meshes, the message says so and lists the selected segment IDs whose meshes never loaded, where Neuroglancer exposes that
- [ ] #3 Renders that finish are unaffected: no extra output at the default log level and no measurable slowdown
- [ ] #4 A browser test reproduces the timeout with a selected segment whose mesh is absent and asserts on the reported layer and segment
<!-- AC:END -->
