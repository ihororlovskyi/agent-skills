---
name: echarts
description: Use when building, styling, debugging, or optimizing Apache ECharts visualizations in vanilla JavaScript, React, or Vue applications, including chart setup, lifecycle management, responsive resizing, theming, large datasets, streaming updates, and server-side rendering.
metadata:
  author: Ihor Orlovskyi
  version: "1.0.0"
license: MIT
compatibility: Requires a JavaScript package manager; `echarts` must be installed in the target project (framework wrappers are optional).
---

# ECharts

Use this skill to build or fix Apache ECharts charts without turning the task into an option-reference lookup. Match the project's existing setup first; only introduce wrappers or new dependencies when the project has none.

## Decision Tree

```
User task -> Does the project already use ECharts?
    - Yes -> Find existing chart components/helpers, reuse their init, theme,
             and resize patterns. Match import style (full vs echarts/core).
    - No -> Pick integration by framework:
        - React -> echarts-for-react wrapper, or a small hook around
                   init/dispose if the project avoids extra deps
        - Vue 3 -> vue-echarts wrapper, or composable around init/dispose
        - Vanilla / other -> echarts.init on a sized container

Next -> Bundle size a concern (app ships to users)?
    - Yes -> Import from 'echarts/core' and register only the used charts,
             components, and renderer (tree-shaking)
    - No / internal tool / prototype -> import * as echarts from 'echarts'

Then -> Build the smallest working option, render it, then layer on
        interactivity (tooltip, dataZoom, toolbox) and theming.
```

## Core Workflow

1. Inspect first: find existing ECharts usage, themes, and shared option helpers before writing a new chart.
2. Size the container: the container element must have non-zero width and height **before** `echarts.init` runs; a chart in a display:none or unmounted tab renders blank.
3. Own the lifecycle: one `init` per container, `resize()` on container size change, `dispose()` on unmount. Wrappers handle this; hand-rolled code must.
4. Update via `setOption`: default merge mode for incremental updates (streaming, new data); `notMerge: true` when the chart type or structure changes.
5. Verify visually: render the chart and check axes, labels, and tooltip against real data before polishing.

## Setup

```bash
npm install echarts                      # core library (always)
npm install echarts-for-react            # React wrapper (optional)
npm install vue-echarts                  # Vue 3 wrapper (optional)
```

Tree-shakeable imports for production bundles:

```ts
import * as echarts from 'echarts/core';
import { LineChart, BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, DataZoomComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([LineChart, BarChart, GridComponent, TooltipComponent, DataZoomComponent, CanvasRenderer]);
```

A missing registration fails at runtime with a console error naming the missing chart/component — register it, do not switch to full import to silence the error.

## Lifecycle Rules

- **Vanilla**: keep the chart instance; call `chart.resize()` from a `ResizeObserver` on the container; call `chart.dispose()` before removing the container.
- **React (echarts-for-react)**: pass `option` as a prop; use `notMerge` prop when replacing structure; get the instance via `ref.getEchartsInstance()` only for imperative needs (streaming `setOption`, `dispatchAction`).
- **React (hand-rolled hook)**: `init` in an effect, `dispose` in its cleanup; keep `option` updates in a separate effect so the chart is not re-created on every render.
- **Vue (vue-echarts)**: use `:option` binding with `autoresize`; access the instance via template ref for `dispatchAction`.
- Never call `echarts.init` twice on the same DOM node; reuse the instance or dispose first (`echarts.getInstanceByDom` to check).

## Data and Options

- Prefer the `dataset` component (`source` + `encode`) when multiple series or charts share one table of data; use per-series `data` for simple single-series charts.
- Time series: use `xAxis: { type: 'time' }` with `[timestamp, value]` pairs instead of pre-formatting date strings into a category axis.
- Large categorical axes: set `axisLabel.interval`/`rotate` deliberately instead of accepting overlap.
- Tooltips: `trigger: 'axis'` for line/bar time series, `trigger: 'item'` for pie/scatter/map.
- Use `valueFormatter` or `tooltip.formatter` for units; keep number formatting in one shared helper when the dashboard has many charts.

## Performance

- Canvas (default renderer) is fine up to ~100K points; use SVG renderer only for small charts needing crisp export or DOM-level styling.
- For large line/scatter series: enable `large: true` and `sampling: 'lttb'` on the series; turn off `animation` for initial render of big datasets.
- Millions of points: use `echarts-gl` (WebGL) — a separate dependency; add it only when actually needed.
- Streaming: call `setOption({ series: [{ data }] })` on the existing instance (merge mode); do not re-init or pass `notMerge` per tick.
- Many charts on one page: share a single `ResizeObserver`/resize handler and use `echarts.connect` for linked tooltips/dataZoom instead of duplicating handlers.

## Theming

- Register a theme once (`echarts.registerTheme('name', themeObject)`) and pass the name to every `init`; do not copy color arrays into each chart's option.
- Dark mode: prefer `init(el, null, ...)` plus a registered dark theme, or `darkMode: true` in the option; re-init (dispose + init) when switching themes — themes are fixed at init time.
- Keep chart-independent styling (font family, palette) in the theme; keep data-dependent styling (visualMap ranges, markLines) in the option.

## SSR and Export

- Server-side rendering (reports, emails, OG images): `echarts.init(null, null, { renderer: 'svg', ssr: true, width, height })` then `renderToSVGString()` — Node only, no DOM needed.
- Client image export: enable `toolbox.feature.saveAsImage`, or call `chart.getDataURL({ pixelRatio: 2 })` programmatically.

## Common Failure Modes

- **Blank chart, no error**: container had zero size at init (hidden tab, flex parent without height, init before mount). Fix sizing/timing, then call `resize()`.
- **Chart does not update**: a new option object with merge mode silently keeps stale series/axes — use `notMerge: true` when removing series or changing chart type.
- **"Component xxx not exists" / missing chart**: tree-shaken build without the registration; add it to `echarts.use([...])`.
- **Memory growth in SPA**: instances not disposed on route change; verify `dispose()` runs in unmount cleanup.
- **Chart wrong size after sidebar/panel toggle**: window `resize` event never fired; observe the container (ResizeObserver / `autoresize`), not the window.
- **Tooltip clipped**: set `tooltip.confine: true` or `appendToBody`-style `tooltip.appendTo` when the chart sits in an overflow-hidden container.
- **Sluggish with big data**: animation on + no sampling; set `animation: false`, `sampling: 'lttb'`, `large: true` before reaching for WebGL.

## Reference Examples

- `examples/vanilla_line.html` - Vanilla JS time-series line chart with resize handling
- `examples/react_chart.tsx` - React component with tree-shaken imports and echarts-for-react
- `examples/vue_chart.vue` - Vue 3 component using vue-echarts with autoresize
