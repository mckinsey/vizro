# Plan: `show_in_url="global"` (global URL support) — how to (re-)enable it

> **Status:** intentionally **NOT** implemented on `feat/syncing_controls_mpa`.
> This branch delivers *cross-page control syncing over the internal `dcc.Store`* only.
> Global URL support was prototyped in the stash that seeded this branch and then
> deliberately removed. This document captures the design so it can be resurrected later.
>
> Related: issue [#2054](https://github.com/McK-Internal/vizro-internal/issues/2054)
> ("Work out how to handle cross-page actions") and PR
> [#1723](https://github.com/mckinsey/vizro/pull/1723) (same-page control syncing).

## 1. What "global URL" means

`show_in_url` currently has two meanings:

| value   | behaviour |
|---------|-----------|
| `False` | control value never appears in the URL query string |
| `True`  | control value appears in the URL **only while you are on that control's own page** |

Global URL support adds a third meaning:

| value      | behaviour |
|------------|-----------|
| `"global"` | control value appears in the URL query string on **every** page, not just its own |

The point: a `"global"` control acts like a dashboard-wide, bookmarkable/shareable
parameter. Because its value already lives in `vizro_controls_store` (which persists
across in-app navigation), the clientside sync callback can keep writing it into the
URL on whatever page you are currently viewing. Navigation links are **not** rewritten;
the query string is reconciled by the sync callback after the page changes.

This is a layer *on top of* the cross-page store syncing delivered in this branch. The
store already carries every control's `currentValue` between pages; global URL support
only adds "…and also mirror these particular controls into the URL everywhere".

## 2. Building blocks already present on this branch (reused as-is)

These were kept because cross-page store syncing needs them anyway — global support
does not have to reintroduce them:

- **`vizro_controls_store`** (`_dashboard.py`) already stores per control:
  `currentValue`, `originalValue`, `pageId`, `selectorId`, and `showInURL`
  (`storage_type="session"`). The `showInURL` key is exactly the metadata the
  clientside needs to decide URL behaviour, so it is *already there* — for global
  support it would simply start carrying the string `"global"` as well as booleans.
- **`set_control`** (`actions/_set_control.py`) already writes a cross-page target's
  new value into the store (`_controls_store[control]["currentValue"] = value` +
  `set_props("vizro_controls_store", ...)`). Global support reuses this untouched.
- **The per-page sync callback** (`_page.py` → `page.js:sync_url_query_params_and_controls`)
  already runs for **all** controls on the page, restores `currentValue` on page open,
  keeps `currentValue` fresh on control change, and encodes same-page `show_in_url=True`
  controls into the URL.

## 3. What global support adds (the parts removed from the stash)

### 3.1 API / type change

- `Filter.show_in_url` and `Parameter.show_in_url`: widen `bool` → `bool | Literal["global"]`
  (in the stash this was the looser `bool | str`; prefer a `Literal` so validation is tight).
  Files: `src/vizro/models/_controls/filter.py`, `src/vizro/models/_controls/parameter.py`.
- Update the field docstrings to document the three states.
- `warn_missing_id_for_url_control` (`_controls_utils.py`) already fires for any truthy
  `show_in_url`; `"global"` is truthy so the "set a fixed id" warning keeps working.

### 3.2 Clientside: encode global controls on every page

In `page.js:sync_url_query_params_and_controls`, **after** encoding the current page's
`show_in_url === true` controls into `urlParams`, add a second pass that encodes every
control whose `showInURL === "global"` — pulled from the **store** (across all pages),
not just from the current page's `controlMap`. Stash reference (removed):

```js
// Encode "global" show_in_url controls from other pages into URL parameters.
const globalControlMap = new Map(
  Object.entries(vizroControlsStore)
    .filter(([id, control]) => control["showInURL"] === "global")
    .map(([id, control]) => [id, control["currentValue"]]),
);
for (const [id, value] of encodeUrlParams(globalControlMap, Array.from(globalControlMap.keys()))) {
  urlParams.set(id, value);
}
```

### 3.3 Clientside: decode URL for controls on *other* pages on page open

On page open, decode URL params for **all** control ids in the store (not only current-page
ids) and write them into `store.currentValue`, so a `"global"` value arriving via the URL
(fresh load / shared link) is restored into the store and survives onward navigation.
Current-page controls additionally get applied to their selectors; off-page controls only
update the store. Stash reference (removed / trimmed back to current-page-only on this branch):

```js
const allControlIds = Object.keys(vizroControlsStore);
const decodedParamMap = decodeUrlParams(urlParams, allControlIds);
decodedParamMap.forEach((value, id) => {
  if (controlMap.has(id)) {            // control is on the current page → also set its selector
    const index = controlIds.indexOf(id);
    controlMap.set(id, value);
    outputSelectorValues[index] = value;
  }
  vizroControlsStore[id]["currentValue"] = value;   // always refresh the store
});
```

> On this branch the decode was deliberately narrowed to `controlIds` (current page only),
> because without global support there is no reason to hydrate off-page controls from the URL.

### 3.4 Re-trigger the sync callback when the store changes

For a global control living on page B that is synced from page A, changing it on page A
must update page A's URL immediately. That requires the sync callback to re-run when the
store changes (not only when a local selector changes). In the stash this was done by:

- `_page.py`: adding `Input("vizro_controls_store", "data")` to the sync `clientside_callback`
  (this branch uses `State`, not `Input`, precisely to avoid this re-trigger).
- `page.js`: branching on `dash_clientside.callback_context.triggered_id`:
  - selector changed → update that control's `currentValue`, `set_props` the store;
  - `"vizro_controls_store"` changed → skip the store write, just fall through to re-encode
    the URL (this is how the other-page global value reaches the current URL);
  - always return `no_update` for the OPL trigger when not a page-open.

> ⚠️ Switching the store from `State` back to `Input` is the single most disruptive part of
> re-enabling global support: it makes the sync callback fire on every cross-page
> `set_control`. Re-check that this does not double-run OPL or fight the guard callback.

## 4. Known problems observed in the stash prototype (fix before shipping)

Carried over verbatim from the prototype author's notes (`scratch_dev/app.py` TODOs) and
worth solving as part of any global implementation:

1. **Reset controls does not update the URL for a global control on another page.**
   Resetting only fires OPL + the sync callback for the *current* page; the global control
   sitting on another page never gets its `set_control` path, so the URL keeps the stale
   value. Needs an explicit "reset also rewrites global params" step, or a fully clientside
   reset that touches the store.
2. **URL "blinks" twice** when syncing a global control: once when the source control's own
   value changes (URL encode), then again when the store change re-triggers the callback.
   Proposed fix in the notes: *solve syncing controls fully clientside* so there is a single
   URL write.
3. **Unknown URL query params.** Decide how to treat params that do not map to any control.
   Proposal from the notes: on first load, treat all unknown params as `"global"` and keep
   them. Handle carefully — this interacts with bookmarking and with non-Vizro params.
4. **"Reset global controls"** — product decision on whether reset clears global controls
   dashboard-wide or only on the current page.

## 5. Suggested implementation order (future)

1. Widen the `show_in_url` type + docs (§3.1).
2. Add the global encode pass in `page.js` (§3.2) — verify a global control appears in the
   URL on a page it does not live on.
3. Add the cross-page URL decode on open (§3.3) — verify a shared link restores a global
   control before navigating.
4. Switch the store to an `Input` and add the `triggered_id` branch (§3.4) — verify
   source-page URL updates when a global control on another page is synced.
5. Work through the four known problems in §4, starting with reset (§4.1) and the double
   blink (§4.2).
6. Add tests + a `scratch_dev` demo page with a `show_in_url="global"` control.

## 6. Where the removed code lived (for `git`-archaeology)

Everything described above existed in the stash applied at the start of this branch
(`stash@{0}: WIP on feat/syncing_controls_mpa`) and in the prototype commits it built on.
The concrete removed hunks were in:

- `src/vizro/models/_controls/filter.py`, `.../parameter.py` — `show_in_url: bool | str`.
- `src/vizro/models/_dashboard.py` — `showInURL` value could be `"global"`.
- `src/vizro/models/_page.py` — `Input("vizro_controls_store", "data")` on the sync callback.
- `src/vizro/static/js/models/page.js` — the global encode block, the all-pages URL decode,
  and the `triggered_id === "vizro_controls_store"` branch.
- `examples/scratch_dev/app.py` — a `show_in_url="global"` demo control.
