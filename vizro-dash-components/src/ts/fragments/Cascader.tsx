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
  useMemo,
  useRef,
  useState,
} from "react";
import "../css/dropdown-chrome.css";
import "../css/cascader.css";
import { ChevronRightIcon } from "./CascaderIcons";
import {
  buildColumns,
  type CascaderOption,
  type CascaderOptionsRaw,
  type CascaderPath,
  collectAllLeaves,
  collectLeaves,
  normalizeOptions,
  parentCheckState,
  searchOptions,
  serializePath,
} from "./cascaderUtils";

/** A single root-to-leaf selection: the sequence of node `value`s (see cascaderUtils). */
type Path = CascaderPath;

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
  value?: Path | Path[] | null;
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
    // On an options change, drop any selected path that no longer terminates on
    // a leaf (identity is the serialized path, so duplicate labels are safe).
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
    if (multi) {
      if (Array.isArray(value)) {
        const paths = value as Path[];
        const cleaned = paths.filter((p) =>
          allLeafPathsSet.has(serializePath(p)),
        );
        if (cleaned.length !== paths.length) {
          setProps?.({ value: cleaned });
        }
      } else {
        // A non-array value is invalid in multi mode; reset to an empty selection.
        setProps?.({ value: [] });
      }
    } else if (
      !Array.isArray(value) ||
      value.length === 0 ||
      !allLeafPathsSet.has(serializePath(value as Path))
    ) {
      setProps?.({ value: null });
    }
  }, [allLeafPathsSet, value, multi, searchValue, setProps]);

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
    if (isOpen && searchable) {
      requestAnimationFrame(() => searchRef.current?.focus());
    }
  }, [isOpen, searchable]);

  const emitValue = useCallback(
    (next: unknown) => {
      if (debounce) {
        setLocalValue(next as typeof value);
      } else {
        setLocalValue(next as typeof value);
        setProps?.({ value: next });
      }
    },
    [debounce, setProps],
  );

  const selectedPaths: Path[] = useMemo(() => {
    const v = localValue;
    if (v === null || v === undefined) return [];
    // multi: value is a list of paths; single: value is one path.
    if (multi) return Array.isArray(v) ? (v as Path[]) : [];
    // A single path must be a non-empty array; treat [] as no selection.
    return Array.isArray(v) && v.length > 0 ? [v as Path] : [];
  }, [localValue, multi]);

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

  // biome-ignore lint/correctness/useExhaustiveDependencies: re-run on focusTick (bumped whenever a pending focus target is queued), not just when columns changes
  useEffect(() => {
    const pending = pendingFocusRef.current;
    if (!pending) return;
    pendingFocusRef.current = null;
    const root = cascaderContentRef.current;
    if (!root) return;
    const columnEls = root.querySelectorAll<HTMLElement>(
      ".dash-cascader-column",
    );
    const columnEl = columnEls[pending.colIdx];
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
    const next = multi ? [] : null;
    emitValue(next);
  }, [multi, emitValue]);

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
      const focusableElements = e.currentTarget.querySelectorAll(
        focusableSelector,
      ) as NodeListOf<HTMLElement>;

      if (focusableElements.length === 0) {
        return;
      }

      e.preventDefault();

      const currentIndex = Array.from(focusableElements).indexOf(
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
          const root = cascaderContentRef.current;
          if (root) {
            for (const el of root.querySelectorAll(
              ".dash-cascader-column, .dash-cascader-results",
            )) {
              (el as HTMLElement).scrollTop = 0;
            }
          }
        } else {
          focusableElements[nextIndex].scrollIntoView({
            behavior: "auto",
            block: "nearest",
          });
        }
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
        localValueRef.current = path;
        valueRef.current = path;
        setLocalValue(path);
        setProps?.({ value: path });
      }
      if (shouldCloseOnSelect) {
        finalizeClose();
      }
    },
    [
      multi,
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
          sideOffset={5}
          onOpenAutoFocus={(e) => e.preventDefault()}
          onKeyDown={handlePanelKeyDown}
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
              >
                {labels.select_all}
              </button>
              {canDeselectAll && (
                <button
                  type="button"
                  className="dash-dropdown-action-button"
                  onClick={handleDeselectAll}
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
      <div className="dash-cascader-columns">
        {columns.map((colOptions, colIdx) => (
          <div
            key={colOptions.map((o) => String(o.value)).join("|")}
            className="dash-cascader-column"
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
                  onClick={() =>
                    !opt.disabled && handleParentClick(colIdx, rowIdx)
                  }
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
                        if (el)
                          el.indeterminate = checkState === "indeterminate";
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
        ))}
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
          const { option, breadcrumb } = result;
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
              {breadcrumb && (
                <span className="dash-cascader-breadcrumb">{breadcrumb}</span>
              )}
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
