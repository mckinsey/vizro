// biome-ignore lint/correctness/noUnusedImports: React must be in scope for classic JSX transform
// biome-ignore lint/style/useImportType: React value import required for classic JSX transform ("jsx": "react" in tsconfig)
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import "../css/cascade.css";
import {
  CaretDownIcon,
  ChevronRightIcon,
  Cross1Icon,
  MagnifyingGlassIcon,
} from "./CascadeIcons";
import {
  buildColumns,
  type CascadeOption,
  collectAllLeaves,
  collectLeaves,
  parentCheckState,
  searchOptions,
} from "./cascadeUtils";

export type CascadeProps = {
  id?: string;
  setProps?: (props: Record<string, unknown>) => void;
  options: CascadeOption[];
  value?: string | number | null | (string | number)[];
  multi?: boolean;
  searchable?: boolean;
  clearable?: boolean;
  placeholder?: string;
  disabled?: boolean;
  maxHeight?: number;
  className?: string;
  style?: React.CSSProperties;
};

const CascadeFragment = ({
  id,
  setProps,
  options,
  value,
  multi = false,
  searchable = true,
  clearable = true,
  placeholder = "Select...",
  disabled = false,
  maxHeight = 300,
  className,
  style,
}: CascadeProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activePath, setActivePath] = useState<number[]>([]);
  const [searchValue, setSearchValue] = useState("");
  const wrapperRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  // Reset activePath when options change
  const prevOptionsRef = useRef(options);
  useEffect(() => {
    if (prevOptionsRef.current !== options) {
      prevOptionsRef.current = options;
      setActivePath([]);
    }
  }, [options]);

  // Close panel on outside click
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: MouseEvent) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
        setSearchValue("");
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [isOpen]);

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsOpen(false);
        setSearchValue("");
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [isOpen]);

  // Focus search when panel opens
  useEffect(() => {
    if (isOpen && searchable) {
      requestAnimationFrame(() => searchRef.current?.focus());
    }
  }, [isOpen, searchable]);

  // Derived values
  const selectedValues: (string | number)[] = useMemo(() => {
    if (value === null || value === undefined) return [];
    if (Array.isArray(value)) return value;
    return [value];
  }, [value]);

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
      const find = (opts: CascadeOption[]): string | undefined => {
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
    setIsOpen((prev) => !prev);
  }, [disabled]);

  const handleClear = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      setProps({ value: multi ? [] : null });
    },
    [multi, setProps],
  );

  const handleLeafClick = useCallback(
    (leafValue: string | number) => {
      if (multi) {
        const next = selectedSet.has(leafValue)
          ? selectedValues.filter((v) => v !== leafValue)
          : [...selectedValues, leafValue];
        setProps({ value: next });
      } else {
        setProps({ value: leafValue });
        setIsOpen(false);
        setSearchValue("");
      }
    },
    [multi, selectedSet, selectedValues, setProps],
  );

  const handleParentClick = useCallback((colIdx: number, rowIdx: number) => {
    // Clicking the row (not checkbox) expands the column — only when not searching
    setActivePath((prev) => {
      const next = prev.slice(0, colIdx);
      next.push(rowIdx);
      return next;
    });
  }, []);

  const handleParentCheckbox = useCallback(
    (option: CascadeOption, e: React.ChangeEvent<HTMLInputElement>) => {
      e.stopPropagation();
      const state = parentCheckState(option, selectedSet);
      const leaves = collectLeaves(option);
      let next: (string | number)[];
      if (state === "checked") {
        // checked → remove all
        next = selectedValues.filter((v) => !leaves.includes(v));
      } else {
        // unchecked or indeterminate → add all missing
        const toAdd = leaves.filter((v) => !selectedSet.has(v));
        next = [...selectedValues, ...toAdd];
      }
      setProps({ value: next });
    },
    [selectedSet, selectedValues, setProps],
  );

  const handleSelectAll = useCallback(() => {
    const pool = searchValue
      ? searchResults.map((r) => r.option.value)
      : collectAllLeaves(options);
    const toAdd = pool.filter((v) => !selectedSet.has(v));
    setProps({ value: [...selectedValues, ...toAdd] });
  }, [
    searchValue,
    searchResults,
    options,
    selectedSet,
    selectedValues,
    setProps,
  ]);

  const handleDeselectAll = useCallback(() => {
    const pool = new Set(
      searchValue
        ? searchResults.map((r) => r.option.value)
        : collectAllLeaves(options),
    );
    setProps({ value: selectedValues.filter((v) => !pool.has(v)) });
  }, [searchValue, searchResults, options, selectedValues, setProps]);

  // --- Render helpers ---

  const canClear = clearable && !disabled && selectedValues.length > 0;

  const triggerLabel = useMemo(() => {
    if (selectedValues.length === 0) return null;
    if (!multi) return findLabel(selectedValues[0]);
    if (selectedValues.length === 1) return findLabel(selectedValues[0]);
    return findLabel(selectedValues[0]); // first label; badge shows count
  }, [selectedValues, multi, findLabel]);

  const renderTrigger = () => (
    <button
      id={id}
      type="button"
      className={`dash-cascade ${className ?? ""}`}
      disabled={disabled}
      aria-expanded={isOpen}
      aria-haspopup="listbox"
      onClick={handleTriggerClick}
    >
      <span className={`dash-cascade-trigger ${canClear ? "has-clear" : ""}`}>
        <span
          className={
            triggerLabel
              ? "dash-cascade-value"
              : "dash-cascade-value dash-cascade-placeholder"
          }
        >
          {triggerLabel ?? placeholder}
        </span>
        {multi && selectedValues.length > 1 && (
          <span className="dash-cascade-count">
            {selectedValues.length} selected
          </span>
        )}
        {canClear && (
          <button
            type="button"
            className="dash-cascade-clear"
            onClick={handleClear}
            aria-label="Clear selection"
          >
            <Cross1Icon />
          </button>
        )}
        <CaretDownIcon className="dash-cascade-caret" />
      </span>
    </button>
  );

  const renderSearchBar = () => (
    <div className="dash-cascade-search-container">
      <MagnifyingGlassIcon className="dash-cascade-search-icon" />
      <input
        ref={searchRef}
        type="search"
        className="dash-cascade-search-input"
        placeholder="Search..."
        value={searchValue}
        autoComplete="off"
        onChange={(e) => setSearchValue(e.target.value)}
      />
      {searchValue && (
        <button
          type="button"
          className="dash-cascade-clear"
          onClick={() => setSearchValue("")}
          aria-label="Clear search"
        >
          <Cross1Icon />
        </button>
      )}
    </div>
  );

  const renderActionsBar = () => (
    <div className="dash-cascade-actions">
      <button
        type="button"
        className="dash-cascade-action-button"
        onClick={handleSelectAll}
      >
        Select all
      </button>
      <button
        type="button"
        className="dash-cascade-action-button"
        onClick={handleDeselectAll}
      >
        Deselect all
      </button>
    </div>
  );

  const renderColumns = () => (
    <div className="dash-cascade-columns" style={{ maxHeight }}>
      {columns.map((colOptions, colIdx) => (
        <div key={colIdx} className="dash-cascade-column">
          {colOptions.map((opt, rowIdx) => {
            const isActive = activePath[colIdx] === rowIdx;
            const isLeafNode = !opt.children || opt.children.length === 0;
            const isSelected = selectedSet.has(opt.value);

            if (isLeafNode) {
              // Leaf row
              return (
                <div
                  key={String(opt.value)}
                  className={`dash-cascade-row${isSelected && !multi ? " selected" : ""}${opt.disabled ? " disabled" : ""}`}
                  onClick={() => !opt.disabled && handleLeafClick(opt.value)}
                >
                  {multi && (
                    <input
                      type="checkbox"
                      className="dash-cascade-checkbox"
                      checked={isSelected}
                      disabled={opt.disabled}
                      onChange={() => handleLeafClick(opt.value)}
                      onClick={(e) => e.stopPropagation()}
                    />
                  )}
                  <span className="dash-cascade-row-label">{opt.label}</span>
                </div>
              );
            }

            // Parent row
            const checkState = multi
              ? parentCheckState(opt, selectedSet)
              : undefined;
            return (
              <div
                key={String(opt.value)}
                className={`dash-cascade-row${isActive ? " active" : ""}${opt.disabled ? " disabled" : ""}`}
                onClick={() =>
                  !opt.disabled && handleParentClick(colIdx, rowIdx)
                }
              >
                {multi && (
                  <input
                    type="checkbox"
                    className="dash-cascade-checkbox"
                    checked={checkState === "checked"}
                    ref={(el) => {
                      if (el) el.indeterminate = checkState === "indeterminate";
                    }}
                    disabled={opt.disabled}
                    onChange={(e) => handleParentCheckbox(opt, e)}
                    onClick={(e) => e.stopPropagation()}
                  />
                )}
                <span className="dash-cascade-row-label">{opt.label}</span>
                <ChevronRightIcon className="dash-cascade-chevron" />
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );

  const renderSearchResults = () => {
    if (searchResults.length === 0) {
      return <div className="dash-cascade-no-results">No options found</div>;
    }
    return (
      <div className="dash-cascade-results" style={{ maxHeight }}>
        {searchResults.map(({ option, breadcrumb }) => {
          const isSelected = selectedSet.has(option.value);
          return (
            <div
              key={String(option.value)}
              className={`dash-cascade-result-row${isSelected && !multi ? " selected" : ""}`}
              onClick={() => !option.disabled && handleLeafClick(option.value)}
            >
              {multi && (
                <input
                  type="checkbox"
                  className="dash-cascade-checkbox"
                  checked={isSelected}
                  disabled={option.disabled}
                  onChange={() => handleLeafClick(option.value)}
                  onClick={(e) => e.stopPropagation()}
                />
              )}
              <span className="dash-cascade-row-label">{option.label}</span>
              {breadcrumb && (
                <span className="dash-cascade-breadcrumb">{breadcrumb}</span>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div ref={wrapperRef} className="dash-cascade-wrapper" style={style}>
      {renderTrigger()}
      {isOpen && (
        <div className="dash-cascade-panel">
          {searchable && renderSearchBar()}
          {multi && renderActionsBar()}
          {searchValue ? renderSearchResults() : renderColumns()}
        </div>
      )}
    </div>
  );
};

export default CascadeFragment;
