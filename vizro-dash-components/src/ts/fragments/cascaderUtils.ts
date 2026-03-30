export type CascaderOption = {
  label: string;
  value: string | number;
  disabled?: boolean;
  children?: CascaderOption[];
  title?: string;
  search?: string;
};

/**
 * The raw `options` type accepted by the Cascader component.
 * In addition to the standard list-of-dicts format, the shorthand
 * nested dict/list notation is also supported:
 *   { "Asia": ["Japan", "China"], "Europe": { "Western": ["France"] } }
 * Each dict key becomes a parent node (label = value = key).
 * List items become leaves; scalars use the scalar as both label and value.
 * Fully-specified option dicts inside lists are passed through unchanged.
 */
export type CascaderOptionsRaw = CascaderOption[] | CascaderOptionsDict;
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface CascaderOptionsDict
  extends Record<
    string,
    CascaderOptionsRaw | (string | number | CascaderOption)[]
  > {}

function normalizeLeaf(item: string | number | CascaderOption): CascaderOption {
  if (typeof item === "object") return item;
  return { label: String(item), value: item };
}

export function normalizeOptions(raw: CascaderOptionsRaw): CascaderOption[] {
  if (Array.isArray(raw)) {
    return raw as CascaderOption[];
  }
  return Object.entries(raw).map(([key, value]) => {
    if (Array.isArray(value)) {
      return {
        label: key,
        value: key,
        children: value.map(normalizeLeaf),
      };
    }
    return {
      label: key,
      value: key,
      children: normalizeOptions(value as CascaderOptionsRaw),
    };
  });
}

/** True if the node has no children (i.e. is a leaf). */
export function isLeaf(option: CascaderOption): boolean {
  return !option.children || option.children.length === 0;
}

/**
 * Walk `options` following `activePath` and return each column's items.
 * Column 0 is always the root. Column N is children of activePath[N-1] in column N-1.
 * If the path becomes invalid (index out of range or node has no children),
 * the walk stops and the path is effectively truncated.
 */
export function buildColumns(
  options: CascaderOption[],
  activePath: number[],
): CascaderOption[][] {
  const columns: CascaderOption[][] = [options];
  let current = options;
  for (const idx of activePath) {
    const node = current[idx];
    if (!node || !node.children || node.children.length === 0) break;
    columns.push(node.children);
    current = node.children;
  }
  return columns;
}

/** Collect all leaf values under a node (depth-first). */
export function collectLeaves(option: CascaderOption): (string | number)[] {
  if (isLeaf(option)) return [option.value];
  return (option.children ?? []).flatMap(collectLeaves);
}

/** Collect all leaf values in the entire options tree. */
export function collectAllLeaves(
  options: CascaderOption[],
): (string | number)[] {
  return options.flatMap(collectLeaves);
}

/**
 * Compute checkbox state for a parent node given selected leaf values.
 * Returns 'checked' | 'indeterminate' | 'unchecked'.
 */
export function parentCheckState(
  option: CascaderOption,
  selectedSet: Set<string | number>,
): "checked" | "indeterminate" | "unchecked" {
  const leaves = collectLeaves(option);
  const selectedCount = leaves.filter((v) => selectedSet.has(v)).length;
  if (selectedCount === 0) return "unchecked";
  if (selectedCount === leaves.length) return "checked";
  return "indeterminate";
}

export type CascaderSearchResult =
  | {
      kind: "leaf";
      option: CascaderOption;
      breadcrumb: string;
    }
  | {
      kind: "branch";
      option: CascaderOption;
      breadcrumb: string;
      branchPath: number[];
    };

/**
 * Flat list of matching nodes for search (leaves and non-leaf branches).
 * Breadcrumb is ancestor labels above the node (not including the node itself).
 * Branch hits include branchPath (indices from root) to open the column view.
 */
export function searchOptions(
  options: CascaderOption[],
  query: string,
  ancestors: string[] = [],
  pathPrefix: number[] = [],
): CascaderSearchResult[] {
  const lower = query.toLowerCase();
  const results: CascaderSearchResult[] = [];
  for (let i = 0; i < options.length; i++) {
    const opt = options[i];
    const myPath = [...pathPrefix, i];
    const breadcrumb = ancestors.join(" › ");

    if (isLeaf(opt)) {
      const searchTarget = (opt.search ?? opt.label).toLowerCase();
      if (searchTarget.includes(lower)) {
        results.push({ kind: "leaf", option: opt, breadcrumb });
      }
    } else {
      const searchTarget = (opt.search ?? opt.label).toLowerCase();
      if (searchTarget.includes(lower) && !opt.disabled) {
        results.push({
          kind: "branch",
          option: opt,
          breadcrumb,
          branchPath: myPath,
        });
      }
      results.push(
        ...searchOptions(
          opt.children ?? [],
          query,
          [...ancestors, opt.label],
          myPath,
        ),
      );
    }
  }
  return results;
}
