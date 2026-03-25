# Cascader Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Dash-standard `persistence`, `persisted_props`, and `persistence_type` props to the `Cascader` component, matching the behaviour of `dcc.Dropdown`.

**Architecture:** Dash's renderer handles all persistence logic automatically — reading/writing to localStorage, sessionStorage, or memory — as long as the component declares the three standard props. No changes to fragment logic are needed; only prop declarations in the Dash component wrapper and TypeScript type in the fragment.

**Tech Stack:** TypeScript/React, Dash component conventions, `dash-generate-components`, webpack.

---

### Task 1: Write the failing persistence test

**Files:**
- Modify: `tests/test_cascader.py`

**Context:** Dash's `dash_duo` fixture uses a real Chrome browser via Selenium. Tests call `dash_duo.start_server(app)` to launch the app, then drive interactions. The `_app()` helper wraps layout in `dmc.MantineProvider`. All tests end with `assert dash_duo.get_logs() == []` to catch JS console errors.

The test verifies: select a value → reload the page → value is still selected (trigger shows the label).

- [ ] **Step 1: Write the failing test**

  At the end of `tests/test_cascader.py`, add:

  ```python
  def test_cascader_persistence(dash_duo):
      """Value persists across page reload when persistence=True."""
      app = _app(Cascader(id="c", options=OPTIONS_2LEVEL, persistence=True))
      dash_duo.start_server(app)

      # Open panel and select Japan (Asia > Japan)
      dash_duo.wait_for_element("#c").click()
      dash_duo.wait_for_element(".dash-cascaderr-row").click()  # Asia
      rows = dash_duo.driver.find_elements("css selector", ".dash-cascaderr-column:nth-child(2) .dash-cascaderr-row")
      rows[0].click()  # Japan
      dash_duo.wait_for_text_to_equal("#c .dash-cascaderr-value", "Japan")

      # Reload and check value is restored
      dash_duo.driver.refresh()
      dash_duo.wait_for_element("#c")
      dash_duo.wait_for_text_to_equal("#c .dash-cascaderr-value", "Japan")
      assert dash_duo.get_logs() == []
  ```

- [ ] **Step 2: Run test to verify it fails**

  ```bash
  hatch run test tests/test_cascader.py::test_cascader_persistence -v
  ```

  Expected: FAIL — `TypeError: Cascader() got an unexpected keyword argument 'persistence'` because the prop doesn't exist yet.

- [ ] **Step 3: Commit the failing test**

  ```bash
  git add tests/test_cascader.py
  git commit -m "test: add failing persistence test for Cascader"
  ```

---

### Task 2: Add persistence props to the Dash component wrapper and fragment type

**Files:**
- Modify: `src/ts/components/Cascader.tsx`
- Modify: `src/ts/fragments/Cascader.tsx`

**Context:** `src/ts/components/Cascader.tsx` is the Dash component wrapper — its `propTypes` and `defaultProps` become the Python class and docstrings. `src/ts/fragments/Cascader.tsx` holds the React component; its `CascaderProps` type must include the new props so TypeScript doesn't error, even though the fragment never uses them.

The two-step build is required to avoid Biome reverting source files:
1. `npm run build:js` — webpack bundles TS/CSS into `vizro_dash_components/vizro_dash_components.js`. Biome is NOT involved.
2. `npm run build:backends` — regenerates Python bindings (`Cascader.py` etc.) from the bundle. Biome is NOT involved.

Never run `hatch run generate-components` or `npm run build` — these invoke Biome which auto-formats and reverts manual edits to `.tsx`/`.css` files.

- [ ] **Step 4: Add persistence props to `src/ts/components/Cascader.tsx` propTypes**

  In `Cascader.propTypes`, after the `style` entry, add:

  ```ts
  /**
   * Used to allow user interactions in this component to be persisted when
   * the component — or the page — is refreshed. If `persisted` is truthy and
   * hasn't changed from its previous value, a `value` that the user has
   * changed while using the app will keep that change, as long as the new
   * `value` also matches what was given originally.
   * Used in conjunction with `persistence_type`.
   */
  persistence: PropTypes.oneOfType([
    PropTypes.bool,
    PropTypes.string,
    PropTypes.number,
  ]),
  /**
   * Properties whose user interactions will persist after refreshing the
   * component or the page. Since only `value` is allowed this prop can
   * normally be ignored.
   */
  persisted_props: PropTypes.arrayOf(PropTypes.string),
  /**
   * Where persisted user changes will be stored:
   * - `"local"`: `window.localStorage`
   * - `"session"`: `window.sessionStorage`
   * - `"memory"`: in-memory, cleared on page refresh
   */
  persistence_type: PropTypes.oneOf(["local", "session", "memory"]),
  ```

- [ ] **Step 5: Add persistence defaults to `Cascader.defaultProps`**

  In `Cascader.defaultProps`, add:

  ```ts
  persisted_props: ["value"],
  persistence_type: "local",
  ```

- [ ] **Step 6: Add persistence props to `CascaderProps` type in `src/ts/fragments/Cascader.tsx`**

  In the `CascaderProps` type definition (after `style?`), add:

  ```ts
  persistence?: boolean | string | number;
  persisted_props?: string[];
  persistence_type?: "local" | "session" | "memory";
  ```

- [ ] **Step 7: Run the two-step build**

  From `vizro-dash-components/`:

  ```bash
  npm run build:js
  npm run build:backends
  ```

  Expected: no errors; `vizro_dash_components/vizro_dash_components.js` and `vizro_dash_components/Cascader.py` are updated.

- [ ] **Step 8: Verify Python bindings include the new props**

  ```bash
  grep -A3 "persistence" vizro_dash_components/Cascader.py | head -30
  ```

  Expected: `persistence`, `persisted_props`, and `persistence_type` appear as kwargs and in the docstring.

- [ ] **Step 9: Run the persistence test to verify it now passes**

  ```bash
  hatch run test tests/test_cascader.py::test_cascader_persistence -v
  ```

  Expected: PASS.

- [ ] **Step 10: Run the full test suite to check for regressions**

  ```bash
  hatch run test tests/test_cascader.py -v
  ```

  Expected: all tests PASS.

- [ ] **Step 11: Commit**

  ```bash
  git add src/ts/components/Cascader.tsx src/ts/fragments/Cascader.tsx vizro_dash_components/Cascader.py vizro_dash_components/vizro_dash_components.js vizro_dash_components/proptypes.js
  git commit -m "feat: add persistence props to Cascader component"
  ```
