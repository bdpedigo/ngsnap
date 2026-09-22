---
id: TASK-4
title: >-
  State templating: swap named elements of a Neuroglancer state and return a new
  state (P15)
status: To Do
assignee: []
created_date: '2026-09-22 19:32'
updated_date: '2026-09-22 19:32'
labels: []
milestone: m-1
dependencies:
  - TASK-3
references:
  - design.md
priority: high
type: feature
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Taking a Neuroglancer state and replacing specific elements of it while leaving the rest alone is useful on its own, without any rendering: restyle a link for a paper, force a layout for a talk, turn off axis lines across a batch of links, or swap a data source. Requirement P15 in design.md makes this a public interface. The render path then uses the same interface to apply the house style, so style becomes "a template plus defaults" instead of a separate mechanism.

Two facts shape the design. First, Neuroglancer keeps knobs in two objects: the viewer state (in the link: layout, showAxisLines, background colors, scale, layer visibility) and the client config state (not in the link: showUIControls, showPanelBorders, viewerSize, scaleBarOptions). The template must be able to address both, and the output must keep them separate because only the viewer state can go back into a URL. Second, output must be deterministic and canonical (stable key order, no incidental reordering), because the cache key (P7) hashes it.

The open question in design.md is the template shape: partial dict merged over the input, path-based patches, or named knobs. Decide during the task and record the decision. `neuroglancer.tool.screenshot.apply_state_modifications` is a small existing example of the kind of overrides the template must express.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A public function takes a state (any input accepted by the parsing task) and a template and returns a new state; the input state object is not mutated
- [ ] #2 The template can set, override, and remove top-level and nested viewer-state elements, including per-layer properties addressed by layer name
- [ ] #3 The template can carry client config-state overrides (at minimum UI controls, panel borders, viewer size, scale bar options) and they are returned separately from the viewer state
- [ ] #4 Elements not named by the template are unchanged, verified by a test that diffs input and output
- [ ] #5 Applying the same template to the same state twice yields byte-identical canonical JSON
- [ ] #6 The result can be emitted as a ViewerState, a canonical JSON string, or a Neuroglancer URL
- [ ] #7 The template shape decision is recorded in design.md under Open Questions with the alternatives that were rejected
<!-- AC:END -->
