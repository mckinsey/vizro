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
  collectAllLeaves,
  collectLeaves,
  normalizeOptions,
  parentCheckState,
  searchOptions,
} from "./cascaderUtils";

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
  value?: string | number | null | (string | number)[];
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

  const allLeaves = useMemo(
    () => new Set(collectAllLeaves(options)),
    [options],
  );
  const prevAllLeavesRef = useRef(allLeaves);
  useEffect(() => {
    if (
      prevAllLeavesRef.current === allLeaves ||
      searchValue ||
      value === null ||
      value === undefined
    ) {
      prevAllLeavesRef.current = allLeaves;
      return;
    }
    prevAllLeavesRef.current = allLeaves;
    if (Array.isArray(value)) {
      if (multi) {
        const invalids = value.filter((v) => !allLeaves.has(v));
        if (invalids.length) {
          const cleaned = value.filter((v) => allLeaves.has(v));
          setProps?.({ value: cleaned });
        }
      }
    } else {
      if (!allLeaves.has(value)) {
        setProps?.({ value: null });
      }
    }
  }, [allLeaves, value, multi, searchValue, setProps]);

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

  const selectedValues: (string | number)[] = useMemo(() => {
    const v = localValue;
    if (v === null || v === undefined) return [];
    if (Array.isArray(v)) return v;
    return [v];
  }, [localValue]);

  const selectedSet = useMemo(
    () => new Set<string | number>(selectedValues),
    [selectedValues],
  );

  const columns = useMemo(
    () => buildColumns(options, activePath),
    [options, activePath],
  );

  const searchResults = useMemo(() => {
    if (!searchValue) return [];
    return searchOptions(options, searchValue);
  }, [options, searchValue]);

  const findLabel = useCallback(
    (val: string | number): string => {
      const find = (opts: CascaderOption[]): string | undefined => {
        for (const opt of opts) {
          if (opt.value === val) return opt.label;
          if (opt.children) {
            const found = find(opt.children);
            if (found !== undefined) return found;
          }
        }
        return undefined;
      };
      return find(options) ?? String(val);
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
          cascaderContentRef.current?.scrollTo({ top: 0 });
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
    (leafValue: string | number) => {
      if (multi) {
        const next = selectedSet.has(leafValue)
          ? selectedValues.filter((v) => v !== leafValue)
          : [...selectedValues, leafValue];
        emitValue(next);
      } else {
        localValueRef.current = leafValue;
        valueRef.current = leafValue as typeof value;
        setLocalValue(leafValue);
        setProps?.({ value: leafValue });
      }
      if (shouldCloseOnSelect) {
        finalizeClose();
      }
    },
    [
      multi,
      selectedSet,
      selectedValues,
      emitValue,
      setProps,
      shouldCloseOnSelect,
      finalizeClose,
    ],
  );

  const handleParentClick = useCallback((colIdx: number, rowIdx: number) => {
    setActivePath((prev) => {
      if (prev[colIdx] === rowIdx && prev.length === colIdx + 1) {
        return prev.slice(0, colIdx);
      }
      const next = prev.slice(0, colIdx);
      next.push(rowIdx);
      return next;
    });
  }, []);

  const handleSearchBranchNavigate = useCallback(
    (branchPath: number[]) => {
      setActivePath(branchPath);
      setSearchValue("");
    },
    [setSearchValue],
  );

  const handleParentCheckbox = useCallback(
    (option: CascaderOption, e: React.ChangeEvent<HTMLInputElement>) => {
      e.stopPropagation();
      const state = parentCheckState(option, selectedSet);
      const leaves = collectLeaves(option);
      let next: (string | number)[];
      if (state === "checked") {
        next = selectedValues.filter((v) => !leaves.includes(v));
      } else {
        const toAdd = leaves.filter((v) => !selectedSet.has(v));
        next = [...selectedValues, ...toAdd];
      }
      emitValue(next);
    },
    [selectedSet, selectedValues, emitValue],
  );

  const handleSelectAll = useCallback(() => {
    const pool = searchValue
      ? searchResults
          .filter((r) => r.kind === "leaf")
          .map((r) => r.option.value)
      : collectAllLeaves(options);
    const toAdd = pool.filter((v) => !selectedSet.has(v));
    emitValue([...selectedValues, ...toAdd]);
  }, [
    searchValue,
    searchResults,
    options,
    selectedSet,
    selectedValues,
    emitValue,
  ]);

  const handleDeselectAll = useCallback(() => {
    const pool = new Set(
      searchValue
        ? searchResults
            .filter((r) => r.kind === "leaf")
            .map((r) => r.option.value)
        : collectAllLeaves(options),
    );
    emitValue(selectedValues.filter((v) => !pool.has(v)));
  }, [searchValue, searchResults, options, selectedValues, emitValue]);

  const canClear = clearable && !disabled && selectedValues.length > 0;

  const canDeselectAll = useMemo(() => {
    if (clearable) return true;
    const pool = searchValue
      ? searchResults
          .filter((r) => r.kind === "leaf")
          .map((r) => r.option.value)
      : collectAllLeaves(options);
    return !selectedValues.every((v) => pool.includes(v));
  }, [clearable, searchValue, searchResults, options, selectedValues]);

  const rowStyle: React.CSSProperties | undefined =
    typeof optionHeight === "number" ? { height: optionHeight } : undefined;

  const triggerLabels = useMemo(() => {
    if (selectedValues.length === 0) return [];
    if (!multi) return [findLabel(selectedValues[0])];
    return selectedValues.map(findLabel);
  }, [selectedValues, multi, findLabel]);

  const contentMaxHeight = maxHeight
    ? `min(${maxHeight}px, calc(100vh - 100px))`
    : "calc(100vh - 100px)";

  const popover = (
    <Popover.Root open={isOpen} onOpenChange={handleOpenChange}>
      <Popover.Trigger asChild>
        <button
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
              e.preventDefault();
            }
          }}
          onKeyUp={(e) => {
            if (disabled) return;
            if (e.key === "ArrowDown" || e.key === "Enter") {
              setIsOpen(true);
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
                    key={String(selectedValues[i])}
                    className="dash-dropdown-value-item"
                  >
                    {label}
                  </span>
                ))}
              </span>
            )}
            {multi && selectedValues.length > 1 && (
              <span
                id={`${accessibleId}-value-count`}
                className="dash-dropdown-value-count"
              >
                {labels.selected_count?.replace(
                  "{num_selected}",
                  `${selectedValues.length}`,
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
                  const firstLeaf = searchResults.find(
                    (r) => r.kind === "leaf",
                  );
                  if (firstLeaf) {
                    handleLeafClick(firstLeaf.option.value);
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
      <div className="dash-cascader-columns" style={{ maxHeight }}>
        {columns.map((colOptions, colIdx) => (
          <div
            key={colOptions.map((o) => String(o.value)).join("|")}
            className="dash-cascader-column"
          >
            {colOptions.map((opt, rowIdx) => {
              const isActive = activePath[colIdx] === rowIdx;
              const isLeafNode = !opt.children || opt.children.length === 0;
              const isSelected = selectedSet.has(opt.value);

              if (isLeafNode) {
                const kbdRow = !multi && !opt.disabled;
                return (
                  // biome-ignore lint/a11y/noStaticElementInteractions: listbox-style option row
                  <div
                    key={String(opt.value)}
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
                    onClick={() => !opt.disabled && handleLeafClick(opt.value)}
                    onKeyDown={(e) => {
                      if (kbdRow && (e.key === "Enter" || e.key === " ")) {
                        e.preventDefault();
                        handleLeafClick(opt.value);
                      }
                    }}
                  >
                    {multi && (
                      <input
                        type="checkbox"
                        className="dash-cascader-checkbox"
                        checked={isSelected}
                        disabled={opt.disabled}
                        onChange={() => handleLeafClick(opt.value)}
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
                  key={String(opt.value)}
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
                  onClick={() =>
                    !opt.disabled && handleParentClick(colIdx, rowIdx)
                  }
                  onKeyDown={(e) => {
                    if (kbdRow && (e.key === "Enter" || e.key === " ")) {
                      e.preventDefault();
                      handleParentClick(colIdx, rowIdx);
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
      <div className="dash-cascader-results" style={{ maxHeight }}>
        {searchResults.map((result) => {
          const { option, breadcrumb } = result;
          const isLeafHit = result.kind === "leaf";
          const isSelected = isLeafHit && selectedSet.has(option.value);
          const rowKey =
            result.kind === "branch"
              ? `branch-${result.branchPath.join("-")}`
              : `leaf-${breadcrumb}-${String(option.value)}`;
          const onRowClick = () => {
            if (option.disabled) return;
            if (result.kind === "branch") {
              handleSearchBranchNavigate(result.branchPath);
            } else {
              handleLeafClick(option.value);
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
                if (kbdRow && (e.key === "Enter" || e.key === " ")) {
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
                  onChange={() => handleLeafClick(option.value)}
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
