// biome-ignore lint/correctness/noUnusedImports: React must be in scope for classic JSX transform
// biome-ignore lint/style/useImportType: React value import required for classic JSX transform ("jsx": "react" in tsconfig)
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import "../css/cascader.css";
import {
  CaretDownIcon,
  ChevronRightIcon,
  Cross1Icon,
  MagnifyingGlassIcon,
} from "./CascaderIcons";
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
  placeholder = "Select...",
  disabled = false,
  maxHeight = 300,
  className,
  style,
  optionHeight = "auto",
  debounce = false,
}: CascaderProps) => {
  const options = useMemo(() => normalizeOptions(optionsRaw), [optionsRaw]);

  const [isOpen, setIsOpen] = useState(false);
  const [activePath, setActivePath] = useState<number[]>([]);
  const [searchValue, setSearchValue] = useState("");
  // Local value state for debounce: tracks selection without firing setProps
  const [localValue, setLocalValue] = useState(value);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  // Sync localValue when external value changes
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  // Reset activePath when options change
  const prevOptionsRef = useRef(options);
  useEffect(() => {
    if (prevOptionsRef.current !== options) {
      prevOptionsRef.current = options;
      setActivePath([]);
    }
  }, [options]);

  // Close panel on outside click — also commits debounced value
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: MouseEvent) => {
      const target = e.target as Node;
      if (wrapperRef.current && !wrapperRef.current.contains(target)) {
        closePanel();
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [isOpen, debounce, localValue, value]);

  // Close on Escape — also commits debounced value
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        closePanel();
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [isOpen, debounce, localValue, value]);

  // Focus search when panel opens
  useEffect(() => {
    if (isOpen && searchable) {
      requestAnimationFrame(() => searchRef.current?.focus());
    }
  }, [isOpen, searchable]);

  // Commit debounced value and close
  const closePanel = useCallback(() => {
    setIsOpen(false);
    setSearchValue("");
    if (debounce && localValue !== value) {
      setProps?.({ value: localValue });
    }
  }, [debounce, localValue, value, setProps]);

  // Fire setProps immediately or defer to close depending on debounce
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

  // Derived values — use localValue so optimistic updates render during debounce
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

  // Find the label for a given value (for trigger display)
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

  // --- Interaction handlers ---

  const handleTriggerClick = useCallback(() => {
    if (disabled) return;
    setIsOpen((prev) => {
      if (prev) {
        // closing via trigger click — commit debounced value
        if (debounce && localValue !== value) {
          setProps?.({ value: localValue });
        }
        setSearchValue("");
      }
      return !prev;
    });
  }, [disabled, debounce, localValue, value, setProps]);

  const handleClear = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      const next = multi ? [] : null;
      setLocalValue(next);
      setProps?.({ value: next });
    },
    [multi, setProps],
  );

  const handleLeafClick = useCallback(
    (leafValue: string | number) => {
      if (multi) {
        const next = selectedSet.has(leafValue)
          ? selectedValues.filter((v) => v !== leafValue)
          : [...selectedValues, leafValue];
        emitValue(next);
      } else {
        // Single-select always commits immediately, even with debounce=true,
        // because the panel closes right away.
        setLocalValue(leafValue);
        setProps?.({ value: leafValue });
        setIsOpen(false);
        setSearchValue("");
      }
    },
    [multi, selectedSet, selectedValues, emitValue, setProps],
  );

  const handleParentClick = useCallback((colIdx: number, rowIdx: number) => {
    setActivePath((prev) => {
      const next = prev.slice(0, colIdx);
      next.push(rowIdx);
      return next;
    });
  }, []);

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
      ? searchResults.map((r) => r.option.value)
      : collectAllLeaves(options);
    const toAdd = pool.filter((v) => !selectedSet.has(v));
    emitValue([...selectedValues, ...toAdd]);
  }, [searchValue, searchResults, options, selectedSet, selectedValues, emitValue]);

  const handleDeselectAll = useCallback(() => {
    const pool = new Set(
      searchValue
        ? searchResults.map((r) => r.option.value)
        : collectAllLeaves(options),
    );
    emitValue(selectedValues.filter((v) => !pool.has(v)));
  }, [searchValue, searchResults, options, selectedValues, emitValue]);

  // --- Render helpers ---

  const canClear = clearable && !disabled && selectedValues.length > 0;

  const rowStyle: React.CSSProperties | undefined =
    typeof optionHeight === "number" ? { height: optionHeight } : undefined;

  const triggerLabels = useMemo(() => {
    if (selectedValues.length === 0) return [];
    if (!multi) return [findLabel(selectedValues[0])];
    return selectedValues.map(findLabel);
  }, [selectedValues, multi, findLabel]);

  const renderTrigger = () => (
    <div
      id={id}
      role="button"
      tabIndex={disabled ? -1 : 0}
      className={`dash-cascader ${disabled ? "disabled" : ""} ${className ?? ""}`}
      aria-expanded={isOpen}
      aria-haspopup="listbox"
      aria-disabled={disabled}
      onClick={handleTriggerClick}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") handleTriggerClick();
      }}
    >
      <span
        className={[
          "dash-cascader-trigger",
          multi && selectedValues.length > 1 ? "has-count" : "",
          canClear ? "has-clear" : "",
        ]
          .filter(Boolean)
          .join(" ")}
      >
        {triggerLabels.length === 0 ? (
          <span className="dash-cascader-value dash-cascader-placeholder">
            {placeholder}
          </span>
        ) : (
          <span className="dash-cascader-value">
            {triggerLabels.map((label, i) => (
              <span key={i} className="dash-cascader-value-item">
                {label}
              </span>
            ))}
          </span>
        )}
        {multi && selectedValues.length > 1 && (
          <span className="dash-cascader-count">
            {selectedValues.length} selected
          </span>
        )}
        {canClear && (
          <button
            type="button"
            className="dash-cascader-clear"
            onClick={handleClear}
            aria-label="Clear selection"
          >
            <Cross1Icon />
          </button>
        )}
        <CaretDownIcon className="dash-cascader-caret" />
      </span>
    </div>
  );

  const renderSearchBar = () => (
    <div className="dash-cascader-search-container">
      <MagnifyingGlassIcon className="dash-cascader-search-icon" />
      <input
        ref={searchRef}
        type="search"
        className="dash-cascader-search-input"
        placeholder="Search..."
        value={searchValue}
        autoComplete="off"
        onChange={(e) => setSearchValue(e.target.value)}
      />
      {searchValue && (
        <button
          type="button"
          className="dash-cascader-clear"
          onClick={() => setSearchValue("")}
          aria-label="Clear search"
        >
          <Cross1Icon />
        </button>
      )}
    </div>
  );

  const renderActionsBar = () => (
    <div className="dash-cascader-actions">
      <button
        type="button"
        className="dash-cascader-action-button"
        onClick={handleSelectAll}
      >
        Select All
      </button>
      <button
        type="button"
        className="dash-cascader-action-button"
        onClick={handleDeselectAll}
      >
        Deselect All
      </button>
    </div>
  );

  const renderColumns = () => (
    <div className="dash-cascader-columns" style={{ maxHeight }}>
      {columns.map((colOptions, colIdx) => (
        <div key={colIdx} className="dash-cascader-column">
          {colOptions.map((opt, rowIdx) => {
            const isActive = activePath[colIdx] === rowIdx;
            const isLeafNode = !opt.children || opt.children.length === 0;
            const isSelected = selectedSet.has(opt.value);

            if (isLeafNode) {
              return (
                <div
                  key={String(opt.value)}
                  className={`dash-cascader-row${isSelected && !multi ? " selected" : ""}${opt.disabled ? " disabled" : ""}`}
                  style={rowStyle}
                  onClick={() => !opt.disabled && handleLeafClick(opt.value)}
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
            return (
              <div
                key={String(opt.value)}
                className={`dash-cascader-row${isActive ? " active" : ""}${opt.disabled ? " disabled" : ""}`}
                style={rowStyle}
                onClick={() =>
                  !opt.disabled && handleParentClick(colIdx, rowIdx)
                }
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
                <ChevronRightIcon className="dash-cascader-chevron" />
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );

  const renderSearchResults = () => {
    if (searchResults.length === 0) {
      return <div className="dash-cascader-no-results">No options found</div>;
    }
    return (
      <div className="dash-cascader-results" style={{ maxHeight }}>
        {searchResults.map(({ option, breadcrumb }) => {
          const isSelected = selectedSet.has(option.value);
          return (
            <div
              key={String(option.value)}
              className={`dash-cascader-result-row${isSelected && !multi ? " selected" : ""}`}
              style={rowStyle}
              onClick={() => !option.disabled && handleLeafClick(option.value)}
            >
              {multi && (
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
  };

  return (
    <div ref={wrapperRef} className="dash-cascader-wrapper" style={style}>
      {renderTrigger()}
      {isOpen && (
        <div className="dash-cascader-panel">
          {searchable && renderSearchBar()}
          {multi && renderActionsBar()}
          {searchValue ? renderSearchResults() : renderColumns()}
        </div>
      )}
    </div>
  );
};

export default CascaderFragment;
