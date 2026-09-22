import {
  CaretDownIcon,
  Cross1Icon,
  MagnifyingGlassIcon,
} from "@radix-ui/react-icons";
import * as Popover from "@radix-ui/react-popover";
import React, {
  type MouseEvent,
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { createPortal } from "react-dom";
import "../css/dropdown-chrome.css";
import "../css/cascader.css";
import { ChevronRightIcon } from "./CascaderIcons";
import {
  buildColumns,
  buildLeafToPath,
  type CascaderOption,
  type CascaderOptionsRaw,
  type CascaderPath,
  type CascaderScalar,
  collectAllLeaves,
  collectLeaves,
  findDuplicateLeafValues,
  fromWire,
  normalizeOptions,
  parentCheckState,
  searchOptions,
  serializePath,
  toWire,
} from "./cascaderUtils";

/** A single root-to-leaf selection: the sequence of node `value`s (see cascaderUtils). */
type Path = CascaderPath;

/**
 * The wire `value`: a list of paths / single path (`full_path=true`), or a list of leaf
 * scalars / single leaf scalar (`full_path=false`), or null. Normalized internally via `fromWire`.
 */
type CascaderValue = Path | Path[] | CascaderScalar | CascaderScalar[] | null;

// Stable identity so path mode's `leafToPath` memo dep doesn't churn; path mode never reads it.
const EMPTY_LEAF_TO_PATH: Map<string, CascaderPath> = new Map();

export type CascaderLabels = {
  select_all?: string;
  deselect_all?: string;
  selected_count?: string;
  search?: string;
  clear_search?: string;
  clear_selection?: string;
  no_options_found?: string;
};

const defaultLabels: CascaderLabels = {
  select_all: "Select All",
  deselect_all: "Deselect All",
  selected_count: "{num_selected} selected",
  search: "Search",
  clear_search: "Clear search",
  clear_selection: "Clear selection",
  no_options_found: "No options found",
};

export type CascaderProps = {
  id?: string;
  setProps?: (props: Record<string, unknown>) => void;
  options: CascaderOptionsRaw;
  value?: CascaderValue;
  full_path?: boolean;
  multi?: boolean;
  searchable?: boolean;
  clearable?: boolean;
  placeholder?: string;
  disabled?: boolean;
  maxHeight?: number;
  className?: string;
  style?: React.CSSProperties;
  optionHeight?: "auto" | number;
  debounce?: boolean;
  closeOnSelect?: boolean;
  labels?: CascaderLabels;
  search_value?: string;
  persistence?: boolean | string | number;
  persisted_props?: string[];
  persistence_type?: "local" | "session" | "memory";
};

const CascaderFragment = ({
  id,
  setProps,
  options: optionsRaw,
  value,
  full_path = false,
  multi = false,
  searchable = true,
  clearable = true,
  placeholder,
  disabled = false,
  maxHeight = 200,
  className,
  style,
  optionHeight = "auto",
  debounce = false,
  closeOnSelect,
  labels: labelsProp,
  search_value,
}: CascaderProps) => {
  const shouldCloseOnSelect = closeOnSelect ?? !multi;
  const dashApi = (
    window as unknown as {
      dash_component_api?: {
        useDashContext?: () => { useLoading?: () => boolean };
      };
    }
  ).dash_component_api;
  const ctx = dashApi?.useDashContext?.();
  const loading = ctx?.useLoading?.();
  const labels = useMemo(
    () => ({ ...defaultLabels, ...labelsProp }),
    [labelsProp],
  );
  const options = useMemo(() => normalizeOptions(optionsRaw), [optionsRaw]);

  // Leaf → path lookup for the leaf-mode (full_path=false) wire boundary. Path mode never reads it,
  // so skip building the per-leaf Map there. (The tree is still walked in path mode for
  // `allLeafPathsSet` and `pool`; this only avoids the extra Map allocation.)
  const leafToPath = useMemo(
    () => (full_path ? EMPTY_LEAF_TO_PATH : buildLeafToPath(options)),
    [options, full_path],
  );

  // Leaf mode requires unique leaf values (a leaf is the wire identity). Duplicates make the
  // leaf→path resolution ambiguous, so warn loudly (last-wins) rather than crash. Path mode is fine.
  useEffect(() => {
    if (full_path) return;
    const duplicates = findDuplicateLeafValues(options);
    if (duplicates.length > 0) {
      console.error(
        `vdc.Cascader: leaf mode (full_path=false) requires unique leaf values, but found ` +
          `duplicates: ${duplicates.map(String).join(", ")}. Selections may be ambiguous; ` +
          `set full_path=true to address leaves by their full path.`,
      );
    }
  }, [options, full_path]);

  const [isOpen, setIsOpen] = useState(false);
  const [activePath, setActivePath] = useState<number[]>([]);
  // Bumped whenever a pending arrow-key focus target is queued, so the effect
  // that applies it re-runs even when the target branch was already expanded
  // (e.g. reopening onto a preselected path) and `columns` doesn't change.
  const [focusTick, setFocusTick] = useState(0);
  const [localValue, setLocalValue] = useState(value);

  const searchValue = search_value ?? "";
  const setSearchValue = useCallback(
    (v: string) => setProps?.({ search_value: v || undefined }),
    [setProps],
  );

  const localValueRef = useRef(localValue);
  const valueRef = useRef(value);
  localValueRef.current = localValue;
  valueRef.current = value;

  const pendingSearchRef = useRef("");

  const [portalContainer, setPortalContainer] = useState<HTMLDivElement | null>(
    null,
  );
  const cascaderContentRef = useRef<HTMLDivElement>(
    document.createElement("div"),
  );
  const searchRef = useRef<HTMLInputElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const triggerKeyDownActiveRef = useRef(false);
  const pendingFocusRef = useRef<{ colIdx: number; rowIndex?: number } | null>(
    null,
  );

  const reactId = useId();
  const accessibleId = id ?? reactId.replace(/:/g, "");

  useEffect(() => {
    if (JSON.stringify(value) !== JSON.stringify(localValueRef.current)) {
      setLocalValue(value);
    }
  }, [value]);

  const prevOptionsRef = useRef(options);
  useEffect(() => {
    if (prevOptionsRef.current !== options) {
      prevOptionsRef.current = options;
      setActivePath([]);
    }
  }, [options]);

  const allLeafPathsSet = useMemo(
    () => new Set(collectAllLeaves(options).map((leaf) => leaf.key)),
    [options],
  );
  const prevAllLeafPathsRef = useRef(allLeafPathsSet);
  useEffect(() => {
    // On an options change, drop any selection that no longer terminates on a current leaf.
    // Normalize the wire value to internal paths (mode-aware), prune, then re-encode to the wire.
    if (
      prevAllLeafPathsRef.current === allLeafPathsSet ||
      searchValue ||
      value === null ||
      value === undefined
    ) {
      prevAllLeafPathsRef.current = allLeafPathsSet;
      return;
    }
    prevAllLeafPathsRef.current = allLeafPathsSet;
    if (multi && !Array.isArray(value)) {
      // A non-array value is invalid in multi mode; reset to an empty selection.
      setProps?.({ value: [] });
      return;
    }
    const paths = fromWire(value, leafToPath, multi, full_path);
    const cleaned = paths.filter((p) => allLeafPathsSet.has(serializePath(p)));
    if (multi) {
      const cleanedWire = toWire(cleaned, multi, full_path);
      // fromWire drops unresolved leaves in leaf mode, so compare the re-encoded wire to the input.
      if (JSON.stringify(cleanedWire) !== JSON.stringify(value)) {
        setProps?.({ value: cleanedWire });
      }
    } else if (cleaned.length === 0) {
      setProps?.({ value: null });
    }
  }, [
    allLeafPathsSet,
    value,
    multi,
    searchValue,
    setProps,
    leafToPath,
    full_path,
  ]);

  const finalizeClose = useCallback(() => {
    pendingSearchRef.current = "";
    const updates: Record<string, unknown> = {};
    if (search_value) {
      updates.search_value = undefined;
    }
    if (debounce && localValueRef.current !== valueRef.current) {
      updates.value = localValueRef.current;
    }
    if (Object.keys(updates).length > 0) {
      setProps?.(updates);
    }
    setIsOpen(false);
    // Radix restores focus to whatever was focused when the panel opened (the
    // trigger), but guarantee it explicitly rather than depending on that timing.
    requestAnimationFrame(() => triggerRef.current?.focus());
  }, [debounce, search_value, setProps]);

  const handleOpenChange = useCallback(
    (open: boolean) => {
      if (open) {
        setIsOpen(true);
      } else {
        finalizeClose();
      }
    },
    [finalizeClose],
  );

  useEffect(() => {
    if (!isOpen) return;
    requestAnimationFrame(() => {
      if (searchable) {
        searchRef.current?.focus();
      } else {
        // No search input to receive focus, so focus the panel itself. It is not in the panel's
        // focusable list, so `handlePanelKeyDown` treats it as index -1 and ArrowDown moves to the
        // first option (rather than the keystroke being lost on the still-focused trigger).
        cascaderContentRef.current?.focus();
      }
    });
  }, [isOpen, searchable]);

  // OUTPUT seam: `next` is always the selection in internal path form; `toWire` encodes it to the
  // active wire shape (leaf scalars when full_path=false, paths when true) before emitting.
  const emitValue = useCallback(
    (next: Path[]) => {
      const wire = toWire(next, multi, full_path) as typeof value;
      if (debounce) {
        setLocalValue(wire);
      } else {
        setLocalValue(wire);
        setProps?.({ value: wire });
      }
    },
    [debounce, setProps, multi, full_path],
  );

  // INPUT seam: normalize the wire `localValue` into internal path form (mode-aware).
  const selectedPaths: Path[] = useMemo(
    () => fromWire(localValue, leafToPath, multi, full_path),
    [localValue, leafToPath, multi, full_path],
  );

  const selectedKeys = useMemo(
    () => selectedPaths.map(serializePath),
    [selectedPaths],
  );

  const selectedSet = useMemo(
    () => new Set<string>(selectedKeys),
    [selectedKeys],
  );

  const columns = useMemo(
    () => buildColumns(options, activePath),
    [options, activePath],
  );

  // Each column beyond the first is rendered as a pop-out (see renderColumns) portaled outside
  // `.dash-cascader-content` — its `overflow: hidden` (needed so column 0's own list scrolls without
  // a second scrollbar) would otherwise clip a same-level sibling that tried to escape it, and CSS
  // doesn't allow "clipped on one axis, visible on the other" on a single element (a mixed
  // overflow-x/overflow-y forces the visible axis to become `auto`, silently turning the panel into
  // a real horizontal scroller that then jumps to follow focus). Portaling sidesteps that entirely.
  //
  // Flyouts use `position: fixed`, so each one's `top`/`left` (flyoutRects[colIdx]) is computed in
  // viewport coordinates directly from the active row that opened it and the right edge of the
  // column before it — no relative/percentage math, no coordinate-space conversion.
  const columnRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [flyoutRects, setFlyoutRects] = useState<
    { top: number; left: number }[]
  >([]);

  const recomputeFlyoutRects = useCallback(() => {
    const rects: { top: number; left: number }[] = [];
    const col0Rect = columnRefs.current[0]?.getBoundingClientRect();
    if (!col0Rect) {
      setFlyoutRects(rects);
      return;
    }
    for (let colIdx = 1; colIdx < columns.length; colIdx++) {
      const prevColumnEl = columnRefs.current[colIdx - 1];
      const rowEl = prevColumnEl?.querySelector<HTMLElement>(
        `[data-row-index="${activePath[colIdx - 1]}"]`,
      );
      if (!prevColumnEl || !rowEl) continue;
      // `left` is derived purely from column 0's rect (always correctly positioned — it's in normal
      // flow) rather than the previous flyout's own rect, since when several levels mount in the same
      // update (e.g. search navigating straight into a branch 2+ levels deep) the previous flyout may
      // still be rendering at this render's not-yet-corrected fallback position.
      // `top` has the same problem for column >= 2: anchor to the already-computed correct top of
      // colIdx - 1 (available from this same pass, processed in order) plus the row's offset *within*
      // its column — that offset is correct regardless of the column's own absolute position, since
      // both the row and its column share whatever position error the column currently has.
      const rowRect = rowEl.getBoundingClientRect();
      const top =
        colIdx === 1
          ? rowRect.top
          : rects[colIdx - 1].top +
            (rowRect.top - prevColumnEl.getBoundingClientRect().top);
      rects[colIdx] = {
        top,
        left: col0Rect.right + (colIdx - 1) * col0Rect.width,
      };
    }
    setFlyoutRects(rects);
  }, [columns, activePath]);

  useLayoutEffect(() => {
    recomputeFlyoutRects();
  }, [recomputeFlyoutRects]);

  // Scrolling any column in the chain shifts every flyout anchored below it; re-measure on scroll so
  // a pop-out doesn't visually detach from the row that opened it.
  useEffect(() => {
    const columnEls = columnRefs.current;
    for (const el of columnEls) {
      el?.addEventListener("scroll", recomputeFlyoutRects, { passive: true });
    }
    return () => {
      for (const el of columnEls) {
        el?.removeEventListener("scroll", recomputeFlyoutRects);
      }
    };
  }, [recomputeFlyoutRects]);

  // biome-ignore lint/correctness/useExhaustiveDependencies: re-run on focusTick (bumped whenever a pending focus target is queued), not just when columns changes
  useEffect(() => {
    const pending = pendingFocusRef.current;
    if (!pending) return;
    pendingFocusRef.current = null;
    // Columns beyond the first are portaled outside cascaderContentRef's DOM subtree (see
    // recomputeFlyoutRects), so look them up via columnRefs (populated for every column,
    // portaled or not) rather than querying the content node's real DOM descendants.
    const columnEl = columnRefs.current[pending.colIdx];
    if (!columnEl) return;
    // In single-select mode the row itself is focusable (.dash-cascader-kbd-row);
    // in multi-select mode only its checkbox is, so fall back to that.
    const rowEl =
      pending.rowIndex !== undefined
        ? columnEl.querySelector<HTMLElement>(
            `[data-row-index="${pending.rowIndex}"]`,
          )
        : null;
    const searchScope = rowEl ?? columnEl;
    const target = searchScope.matches(".dash-cascader-kbd-row")
      ? searchScope
      : searchScope.querySelector<HTMLElement>(
          ".dash-cascader-kbd-row, input[type='checkbox']:not([disabled])",
        );
    if (target) {
      target.focus();
      target.scrollIntoView({ behavior: "auto", block: "nearest" });
    }
  }, [focusTick]);

  const searchResults = useMemo(() => {
    if (!searchValue) return [];
    return searchOptions(options, searchValue);
  }, [options, searchValue]);

  const findLabel = useCallback(
    (path: Path): string => {
      // Walk the tree by path and return the terminal node's label.
      const fallback = String(path[path.length - 1] ?? "");
      let level = options;
      let node: CascaderOption | undefined;
      for (const seg of path) {
        node = level.find((o) => o.value === seg);
        if (!node) return fallback;
        level = node.children ?? [];
      }
      return node?.label ?? fallback;
    },
    [options],
  );

  const clearSelection = useCallback(() => {
    // Empty selection; toWire encodes it as [] (multi) or null (single) in either mode.
    emitValue([]);
  }, [emitValue]);

  const handleClearSearch = useCallback(
    (e: MouseEvent) => {
      if (e.currentTarget instanceof HTMLElement) {
        const parentElement = e.currentTarget.parentElement;
        parentElement?.querySelector("input")?.focus();
      }
      setSearchValue("");
    },
    [setSearchValue],
  );

  const handlePanelKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLDivElement>) => {
      const relevantKeys = [
        "ArrowDown",
        "ArrowUp",
        "PageDown",
        "PageUp",
        "Home",
        "End",
      ];
      if (!relevantKeys.includes(e.key)) {
        return;
      }

      if (
        ["Home", "End"].includes(e.key) &&
        document.activeElement === searchRef.current
      ) {
        return;
      }

      const focusableSelector =
        'input[type="search"], input:not([disabled]), button:not([disabled]), .dash-cascader-kbd-row';
      // Columns beyond the first are portaled outside e.currentTarget's (Popover.Content's) DOM
      // subtree (see recomputeFlyoutRects), so search from portalContainer — the real DOM ancestor
      // shared by content and every portaled flyout — instead. That also picks up the trigger
      // button (a portalContainer sibling of content), so exclude it explicitly.
      // Select All / Deselect All are excluded from the vertical (up/down) flow: they form a
      // horizontal group navigated with Left/Right, and ArrowDown from them jumps to the options
      // (see handleActionKeyDown).
      const focusableElements = (
        Array.from(
          portalContainer?.querySelectorAll(focusableSelector) ?? [],
        ) as HTMLElement[]
      ).filter(
        (el) =>
          el !== triggerRef.current &&
          !el.classList.contains("dash-dropdown-action-button"),
      );

      if (focusableElements.length === 0) {
        return;
      }

      e.preventDefault();

      const currentIndex = focusableElements.indexOf(
        document.activeElement as HTMLElement,
      );
      let nextIndex = -1;

      switch (e.key) {
        case "ArrowDown":
          nextIndex =
            currentIndex < focusableElements.length - 1 ? currentIndex + 1 : 0;
          break;
        case "ArrowUp":
          nextIndex =
            currentIndex > 0 ? currentIndex - 1 : focusableElements.length - 1;
          break;
        case "PageDown":
          nextIndex = Math.min(currentIndex + 10, focusableElements.length - 1);
          break;
        case "PageUp":
          nextIndex = Math.max(currentIndex - 10, 0);
          break;
        case "Home":
          nextIndex = 0;
          break;
        case "End":
          nextIndex = focusableElements.length - 1;
          break;
        default:
          break;
      }

      if (nextIndex > -1) {
        focusableElements[nextIndex].focus();
        if (nextIndex === 0) {
          for (const el of portalContainer?.querySelectorAll(
            ".dash-cascader-column, .dash-cascader-results",
          ) ?? []) {
            (el as HTMLElement).scrollTop = 0;
          }
        } else {
          focusableElements[nextIndex].scrollIntoView({
            behavior: "auto",
            block: "nearest",
          });
        }
      }
    },
    [portalContainer],
  );

  // Keyboard nav for the Select All / Deselect All action buttons: Left/Right move within the
  // horizontal group, ArrowDown leaves the group and focuses the first option below.
  const handleActionKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLButtonElement>) => {
      const root = cascaderContentRef.current;
      if (!root) return;
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        e.preventDefault();
        e.stopPropagation();
        const buttons = Array.from(
          root.querySelectorAll<HTMLElement>(".dash-dropdown-action-button"),
        );
        const next =
          buttons[
            buttons.indexOf(e.currentTarget) + (e.key === "ArrowRight" ? 1 : -1)
          ];
        next?.focus();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        e.stopPropagation();
        root
          .querySelector<HTMLElement>(
            '.dash-cascader-column .dash-cascader-kbd-row, .dash-cascader-column input[type="checkbox"]:not([disabled])',
          )
          ?.focus();
      }
    },
    [],
  );

  const handleLeafClick = useCallback(
    (option: CascaderOption) => {
      const { path, key } = option;
      if (multi) {
        const next = selectedSet.has(key)
          ? selectedPaths.filter((_, i) => selectedKeys[i] !== key)
          : [...selectedPaths, path];
        emitValue(next);
      } else {
        // OUTPUT seam: single-select commits immediately (even under debounce). Encode to the wire
        // shape and keep the refs in sync so finalizeClose sees the committed value this tick.
        const wire = toWire([path], multi, full_path) as typeof value;
        localValueRef.current = wire;
        valueRef.current = wire;
        setLocalValue(wire);
        setProps?.({ value: wire });
      }
      if (shouldCloseOnSelect) {
        finalizeClose();
      }
    },
    [
      multi,
      full_path,
      selectedSet,
      selectedPaths,
      selectedKeys,
      emitValue,
      setProps,
      shouldCloseOnSelect,
      finalizeClose,
    ],
  );

  const handleParentClick = useCallback((colIdx: number, rowIdx: number) => {
    setActivePath((prev) => {
      // Toggle closed: clicking the active parent at this column collapses this
      // branch entirely (all deeper segments), not only the deepest column.
      if (prev[colIdx] === rowIdx) {
        return prev.slice(0, colIdx);
      }
      const next = prev.slice(0, colIdx);
      next.push(rowIdx);
      return next;
    });
  }, []);

  const handleArrowRight = useCallback(
    (colIdx: number, rowIdx: number) => {
      if (activePath[colIdx] !== rowIdx) {
        handleParentClick(colIdx, rowIdx);
      }
      pendingFocusRef.current = { colIdx: colIdx + 1 };
      setFocusTick((t) => t + 1);
    },
    [activePath, handleParentClick],
  );

  const handleArrowLeft = useCallback(
    (colIdx: number) => {
      if (colIdx === 0) return;
      const parentRowIdx = activePath[colIdx - 1];
      setActivePath((prev) => prev.slice(0, colIdx - 1));
      pendingFocusRef.current = { colIdx: colIdx - 1, rowIndex: parentRowIdx };
      setFocusTick((t) => t + 1);
    },
    [activePath],
  );

  const handleSearchBranchNavigate = useCallback(
    (branchPath: number[]) => {
      setActivePath(branchPath);
      setSearchValue("");
    },
    [setSearchValue],
  );

  const setParentSelection = useCallback(
    (option: CascaderOption) => {
      const state = parentCheckState(option, selectedSet);
      const leaves = collectLeaves(option);
      let next: Path[];
      if (state === "checked") {
        const leafKeys = new Set(leaves.map((leaf) => leaf.key));
        next = selectedPaths.filter((_, i) => !leafKeys.has(selectedKeys[i]));
      } else {
        const toAdd = leaves.filter((leaf) => !selectedSet.has(leaf.key));
        next = [...selectedPaths, ...toAdd.map((leaf) => leaf.path)];
      }
      emitValue(next);
    },
    [selectedSet, selectedPaths, selectedKeys, emitValue],
  );

  const handleParentCheckbox = useCallback(
    (option: CascaderOption, e: React.ChangeEvent<HTMLInputElement>) => {
      e.stopPropagation();
      setParentSelection(option);
    },
    [setParentSelection],
  );

  // Leaves that Select All / Deselect All act on: search hits when filtering,
  // otherwise every leaf. Shared by both handlers and canDeselectAll.
  const pool = useMemo<CascaderOption[]>(
    () =>
      searchValue
        ? searchResults.filter((r) => r.kind === "leaf").map((r) => r.option)
        : collectAllLeaves(options),
    [searchValue, searchResults, options],
  );
  const poolKeys = useMemo(() => new Set(pool.map((leaf) => leaf.key)), [pool]);

  const handleSelectAll = useCallback(() => {
    const toAdd = pool.filter((leaf) => !selectedSet.has(leaf.key));
    emitValue([...selectedPaths, ...toAdd.map((leaf) => leaf.path)]);
  }, [pool, selectedSet, selectedPaths, emitValue]);

  const handleDeselectAll = useCallback(() => {
    emitValue(selectedPaths.filter((_, i) => !poolKeys.has(selectedKeys[i])));
  }, [poolKeys, selectedPaths, selectedKeys, emitValue]);

  const canClear = clearable && !disabled && selectedPaths.length > 0;

  const canDeselectAll = useMemo(() => {
    if (clearable) return true;
    return !selectedKeys.every((k) => poolKeys.has(k));
  }, [clearable, poolKeys, selectedKeys]);

  const rowStyle: React.CSSProperties | undefined =
    typeof optionHeight === "number" ? { height: optionHeight } : undefined;

  const triggerLabels = useMemo(() => {
    if (selectedPaths.length === 0) return [];
    if (!multi) return [findLabel(selectedPaths[0])];
    return selectedPaths.map(findLabel);
  }, [selectedPaths, multi, findLabel]);

  const contentMaxHeight = maxHeight
    ? `min(${maxHeight}px, calc(100vh - 100px))`
    : "calc(100vh - 100px)";

  const popover = (
    <Popover.Root open={isOpen} onOpenChange={handleOpenChange}>
      <Popover.Trigger asChild>
        <button
          ref={triggerRef}
          id={id}
          type="button"
          disabled={disabled}
          className={`dash-dropdown ${className ?? ""}`}
          aria-labelledby={`${accessibleId}-value-count ${accessibleId}-value`}
          aria-haspopup="listbox"
          aria-expanded={isOpen}
          data-dash-is-loading={loading || undefined}
          onKeyDown={(e) => {
            if (e.key === "ArrowDown" || e.key === "Enter") {
              // Only a keydown that actually started on the trigger should be able
              // to open it; a keyup can otherwise land here after focus returns to
              // the trigger mid-selection (e.g. Enter-selecting a row), which would
              // immediately reopen the panel that selection just closed.
              triggerKeyDownActiveRef.current = true;
              e.preventDefault();
            }
          }}
          onKeyUp={(e) => {
            if (disabled) return;
            if (e.key === "ArrowDown" || e.key === "Enter") {
              if (triggerKeyDownActiveRef.current) {
                setIsOpen(true);
              }
              triggerKeyDownActiveRef.current = false;
            }
            if ((e.key === "Delete" || e.key === "Backspace") && canClear) {
              clearSelection();
            }
            if (e.key.length === 1 && searchable) {
              pendingSearchRef.current += e.key;
              setSearchValue(pendingSearchRef.current);
              setIsOpen(true);
              requestAnimationFrame(() => searchRef.current?.focus());
            }
          }}
        >
          <span className="dash-dropdown-grid-container dash-dropdown-trigger">
            {triggerLabels.length === 0 ? (
              <span
                id={`${accessibleId}-value`}
                className="dash-dropdown-value dash-dropdown-placeholder"
              >
                {placeholder}
              </span>
            ) : (
              <span
                id={`${accessibleId}-value`}
                className="dash-dropdown-value"
              >
                {triggerLabels.map((label, i) => (
                  <span
                    key={selectedKeys[i]}
                    className="dash-dropdown-value-item"
                  >
                    {label}
                  </span>
                ))}
              </span>
            )}
            {multi && selectedPaths.length > 1 && (
              <span
                id={`${accessibleId}-value-count`}
                className="dash-dropdown-value-count"
              >
                {labels.selected_count?.replace(
                  "{num_selected}",
                  `${selectedPaths.length}`,
                )}
              </span>
            )}
            {canClear && (
              <button
                type="button"
                className="dash-dropdown-clear"
                onClick={() => clearSelection()}
                onKeyDown={(e) => {
                  // When the clear button is focused, Enter/Space clears the selection. Stop the
                  // event so it does not bubble to the trigger, whose handler would otherwise open
                  // the panel instead of clearing.
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    e.stopPropagation();
                    clearSelection();
                  }
                }}
                title={labels.clear_selection}
                aria-label={labels.clear_selection}
              >
                <Cross1Icon />
              </button>
            )}
            <CaretDownIcon className="dash-dropdown-trigger-icon" />
          </span>
        </button>
      </Popover.Trigger>

      <Popover.Portal container={portalContainer}>
        <Popover.Content
          ref={cascaderContentRef}
          className="dash-dropdown-content dash-cascader-content"
          align="start"
          // Wider than the shared dropdown chrome's default gap so the panel clearly reads as a
          // separate floating popup rather than an extension of the trigger.
          sideOffset={8}
          tabIndex={-1}
          onOpenAutoFocus={(e) => e.preventDefault()}
          onKeyDown={handlePanelKeyDown}
          // Flyout columns (colIdx > 0) are portaled into portalContainer directly, alongside — not
          // inside — this content node (see recomputeFlyoutRects), so Radix's own DOM-containment
          // check would otherwise treat a click on one as "outside" and dismiss the panel.
          onPointerDownOutside={(e) => {
            if (portalContainer?.contains(e.target as Node)) {
              e.preventDefault();
            }
          }}
          style={{ maxHeight: contentMaxHeight }}
        >
          {searchable && (
            <div className="dash-dropdown-grid-container dash-dropdown-search-container">
              <MagnifyingGlassIcon className="dash-dropdown-search-icon" />
              <input
                ref={searchRef}
                type="search"
                className="dash-dropdown-search"
                placeholder={labels.search}
                value={searchValue}
                autoComplete="off"
                onChange={(e) => setSearchValue(e.target.value)}
                onKeyUp={(e) => {
                  if (
                    !searchValue ||
                    e.key !== "Enter" ||
                    !searchResults.length
                  ) {
                    return;
                  }
                  const first = searchResults.find((r) => !r.option.disabled);
                  if (!first) return;
                  if (first.kind === "leaf") {
                    handleLeafClick(first.option);
                  } else {
                    handleSearchBranchNavigate(first.branchPath);
                  }
                }}
              />
              {searchValue && (
                <button
                  type="button"
                  className="dash-dropdown-clear"
                  onClick={handleClearSearch}
                  aria-label={labels.clear_search}
                >
                  <Cross1Icon />
                </button>
              )}
            </div>
          )}
          {multi && (
            <div className="dash-dropdown-actions">
              <button
                type="button"
                className="dash-dropdown-action-button"
                onClick={handleSelectAll}
                onKeyDown={handleActionKeyDown}
              >
                {labels.select_all}
              </button>
              {canDeselectAll && (
                <button
                  type="button"
                  className="dash-dropdown-action-button"
                  onClick={handleDeselectAll}
                  onKeyDown={handleActionKeyDown}
                >
                  {labels.deselect_all}
                </button>
              )}
            </div>
          )}
          {searchValue ? renderSearchResults() : renderColumns()}
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );

  function renderColumns() {
    return (
      <>
        <div className="dash-cascader-columns">
          {renderColumn(columns[0], 0)}
        </div>
        {portalContainer &&
          columns.slice(1).map((colOptions, i) => {
            const colIdx = i + 1;
            // Render unconditionally, even before flyoutRects[colIdx] is measured (e.g. search
            // navigates straight into a branch 2+ levels deep, adding several columns in one update:
            // column colIdx's rect depends on column colIdx-1's DOM ref, which only exists once
            // colIdx-1 itself has rendered — so gating this on an existing measurement would leave
            // every level past the first stuck at colIdx-1's ref never mounting). The fallback
            // position is corrected by recomputeFlyoutRects's useLayoutEffect before paint.
            return createPortal(
              renderColumn(colOptions, colIdx, flyoutRects[colIdx]),
              portalContainer,
              colOptions.map((o) => String(o.value)).join("|"),
            );
          })}
      </>
    );
  }

  function renderColumn(
    colOptions: CascaderOption[],
    colIdx: number,
    flyoutRect?: { top: number; left: number },
  ) {
    const isFlyout = colIdx > 0;
    return (
      <div
        key={colOptions.map((o) => String(o.value)).join("|")}
        ref={(el) => {
          columnRefs.current[colIdx] = el;
        }}
        data-col-idx={colIdx}
        className={[
          "dash-cascader-column",
          isFlyout ? "dash-cascader-column-flyout" : "",
        ]
          .filter(Boolean)
          .join(" ")}
        style={
          isFlyout
            ? {
                ...(flyoutRect ?? { top: 0, left: 0 }),
                width: columnRefs.current[0]?.getBoundingClientRect().width,
                maxHeight: contentMaxHeight,
              }
            : undefined
        }
      >
        {colOptions.map((opt, rowIdx) => {
          const isActive = activePath[colIdx] === rowIdx;
          const isLeafNode = !opt.children || opt.children.length === 0;
          const isSelected = selectedSet.has(opt.key);

          if (isLeafNode) {
            const kbdRow = !multi && !opt.disabled;
            return (
              // biome-ignore lint/a11y/noStaticElementInteractions: listbox-style option row
              <div
                key={opt.key}
                className={[
                  "dash-cascader-row",
                  isSelected && !multi ? "selected" : "",
                  opt.disabled ? "disabled" : "",
                  kbdRow ? "dash-cascader-kbd-row" : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
                style={rowStyle}
                tabIndex={kbdRow ? 0 : undefined}
                data-row-index={rowIdx}
                onClick={() => !opt.disabled && handleLeafClick(opt)}
                onKeyDown={(e) => {
                  if (opt.disabled) return;
                  // Space is left to the native checkbox toggle in multi mode
                  // (handling it here too would double-toggle); Enter has no
                  // native effect on a checkbox, so it's always ours to handle.
                  if (e.key === "Enter" || (kbdRow && e.key === " ")) {
                    e.preventDefault();
                    handleLeafClick(opt);
                  } else if (e.key === "ArrowLeft" && colIdx > 0) {
                    e.preventDefault();
                    handleArrowLeft(colIdx);
                  }
                }}
              >
                {multi && (
                  <input
                    type="checkbox"
                    className="dash-cascader-checkbox"
                    checked={isSelected}
                    disabled={opt.disabled}
                    onChange={() => handleLeafClick(opt)}
                    onClick={(e) => e.stopPropagation()}
                  />
                )}
                <span className="dash-cascader-row-label">{opt.label}</span>
              </div>
            );
          }

          const checkState = multi
            ? parentCheckState(opt, selectedSet)
            : undefined;
          const kbdRow = !multi && !opt.disabled;
          return (
            // biome-ignore lint/a11y/noStaticElementInteractions: listbox-style parent row
            <div
              key={opt.key}
              className={[
                "dash-cascader-row",
                isActive ? "active" : "",
                opt.disabled ? "disabled" : "",
                kbdRow ? "dash-cascader-kbd-row" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              style={rowStyle}
              tabIndex={kbdRow ? 0 : undefined}
              data-row-index={rowIdx}
              onClick={() => !opt.disabled && handleParentClick(colIdx, rowIdx)}
              onKeyDown={(e) => {
                if (opt.disabled) return;
                if (e.key === "Enter") {
                  e.preventDefault();
                  if (multi) {
                    setParentSelection(opt);
                  } else {
                    handleParentClick(colIdx, rowIdx);
                  }
                } else if (kbdRow && e.key === " ") {
                  e.preventDefault();
                  handleParentClick(colIdx, rowIdx);
                } else if (e.key === "ArrowRight") {
                  e.preventDefault();
                  handleArrowRight(colIdx, rowIdx);
                } else if (e.key === "ArrowLeft" && colIdx > 0) {
                  e.preventDefault();
                  handleArrowLeft(colIdx);
                }
              }}
            >
              {multi && (
                <input
                  type="checkbox"
                  className="dash-cascader-checkbox"
                  checked={checkState === "checked"}
                  ref={(el) => {
                    if (el) el.indeterminate = checkState === "indeterminate";
                  }}
                  disabled={opt.disabled}
                  onChange={(e) => handleParentCheckbox(opt, e)}
                  onClick={(e) => e.stopPropagation()}
                />
              )}
              <span className="dash-cascader-row-label">{opt.label}</span>
              <ChevronRightIcon
                className={[
                  "dash-cascader-chevron",
                  isActive ? "dash-cascader-chevron-expanded" : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
              />
            </div>
          );
        })}
      </div>
    );
  }

  function renderSearchResults() {
    if (searchResults.length === 0) {
      return (
        <div className="dash-cascader-no-results">
          {labels.no_options_found}
        </div>
      );
    }
    return (
      <div className="dash-cascader-results">
        {searchResults.map((result) => {
          const { option } = result;
          const isLeafHit = result.kind === "leaf";
          const isSelected = isLeafHit && selectedSet.has(option.key);
          const rowKey =
            result.kind === "branch"
              ? `branch-${result.branchPath.join("-")}`
              : `leaf-${option.key}`;
          const onRowClick = () => {
            if (option.disabled) return;
            if (result.kind === "branch") {
              handleSearchBranchNavigate(result.branchPath);
            } else {
              handleLeafClick(option);
            }
          };
          const kbdRow = !option.disabled && (!multi || (multi && !isLeafHit));
          return (
            // biome-ignore lint/a11y/noStaticElementInteractions: search result row
            <div
              key={rowKey}
              className={[
                "dash-cascader-result-row",
                result.kind === "branch" && "dash-cascader-result-row-branch",
                isSelected && !multi && "selected",
                kbdRow ? "dash-cascader-kbd-row" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              style={rowStyle}
              tabIndex={kbdRow ? 0 : undefined}
              onClick={onRowClick}
              onKeyDown={(e) => {
                if (option.disabled) return;
                // Space is left to the native checkbox toggle in multi mode
                // (handling it here too would double-toggle); Enter has no
                // native effect on a checkbox, so it's always ours to handle.
                if (e.key === "Enter" || (kbdRow && e.key === " ")) {
                  e.preventDefault();
                  onRowClick();
                }
              }}
            >
              {multi && isLeafHit && (
                <input
                  type="checkbox"
                  className="dash-cascader-checkbox"
                  checked={isSelected}
                  disabled={option.disabled}
                  onChange={() => handleLeafClick(option)}
                  onClick={(e) => e.stopPropagation()}
                />
              )}
              <span className="dash-cascader-row-label">{option.label}</span>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div
      ref={setPortalContainer}
      className="dash-dropdown-wrapper dash-cascader-wrapper"
      style={style}
    >
      {popover}
    </div>
  );
};

export default CascaderFragment;
