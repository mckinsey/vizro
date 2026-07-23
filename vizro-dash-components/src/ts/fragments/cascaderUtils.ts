/**
 * A root-to-leaf path: the sequence of node `value`s from the root down to a
 * node (inclusive). Segments are scalars; booleans are supported because Vizro
 * allows boolean leaf values.
 */
export type CascaderPath = (string | number | boolean)[];

export type CascaderOption = {
  label: string;
  value: string | number | boolean;
  /**
   * Root-to-this-node path of `value`s (inclusive), computed by `normalizeOptions`.
   * This is the identity used on the wire, so duplicate leaf labels across
   * different branches are addressed unambiguously.
   */
  path: CascaderPath;
  /** Precomputed `serializePath(path)`; the stable Set/Map/React key for this node. */
  key: string;
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
 *
 * Raw options do not carry a `path`; it is computed during normalization.
 */
export type CascaderOptionsRaw = CascaderOptionRaw[] | CascaderOptionsDict;

/** A raw option node as supplied by the user (before `path`/`key` are computed). */
export type CascaderOptionRaw = Omit<
  CascaderOption,
  "path" | "key" | "children"
> & {
  children?: CascaderOptionRaw[];
};

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface CascaderOptionsDict
  extends Record<
    string,
    CascaderOptionsRaw | (string | number | boolean | CascaderOptionRaw)[]
  > {}

/** Normalize a single raw node (scalar leaf or option dict), computing its `path`/`key`. */
function normalizeNode(
  item: string | number | boolean | CascaderOptionRaw,
  parentPath: CascaderPath,
): CascaderOption {
  // Any non-object scalar (string, number, or boolean) is a leaf value.
  if (typeof item !== "object") {
    const path = [...parentPath, item];
    return { label: String(item), value: item, path, key: serializePath(path) };
  }
  const path = [...parentPath, item.value];
  const { children: rawChildren, ...rest } = item;
  const node: CascaderOption = { ...rest, path, key: serializePath(path) };
  if (rawChildren?.length) {
    node.children = rawChildren.map((child) => normalizeNode(child, path));
  }
  return node;
}

/**
 * Normalize `options` into `CascaderOption[]`, computing a root-to-node `path`
 * of `value`s for every node. `parentPath` is the path of the parent node and
 * is used to prefix each child's path during recursion.
 */
export function normalizeOptions(
  raw: CascaderOptionsRaw,
  parentPath: CascaderPath = [],
): CascaderOption[] {
  if (Array.isArray(raw)) {
    return raw.map((item) => normalizeNode(item, parentPath));
  }
  return Object.entries(raw).map(([key, value]) => {
    const path = [...parentPath, key];
    const nodeKey = serializePath(path);
    if (Array.isArray(value)) {
      return {
        label: key,
        value: key,
        path,
        key: nodeKey,
        children: value.map((leaf) => normalizeNode(leaf, path)),
      };
    }
    return {
      label: key,
      value: key,
      path,
      key: nodeKey,
      children: normalizeOptions(value as CascaderOptionsRaw, path),
    };
  });
}

/** True if the node has no children (that is, is a leaf). */
export function isLeaf(option: CascaderOption): boolean {
  return !option.children || option.children.length === 0;
}

/** Stable serialization of a path, usable as a Set/Map key or React key. */
export function serializePath(path: CascaderPath): string {
  return JSON.stringify(path);
}

/** A leaf scalar value (the wire form of a selection in leaf mode). */
export type CascaderScalar = string | number | boolean;

/**
 * Stable serialization of a single leaf scalar, usable as a Map/Set key. Typed
 * (`1` and `"1"`, `true` and `"true"` serialize differently) so leaf identity is exact.
 */
export function serializeLeaf(leaf: unknown): string {
  return JSON.stringify(leaf);
}

/**
 * Map each leaf's scalar `value` to its full root-to-leaf `path`. Used by leaf mode
 * (`full_path=false`) to resolve a bare leaf on the wire back to its internal path.
 * Only unambiguous when leaf values are unique (see `findDuplicateLeafValues`): a later
 * duplicate overwrites an earlier one (last-wins), matching the component's degrade-not-crash policy.
 */
export function buildLeafToPath(
  options: CascaderOption[],
): Map<string, CascaderPath> {
  const map = new Map<string, CascaderPath>();
  for (const leaf of collectAllLeaves(options)) {
    map.set(serializeLeaf(leaf.value), leaf.path);
  }
  return map;
}

/**
 * Leaf `value`s that appear on more than one leaf (in tree order of the first repeat).
 * Leaf mode requires unique leaf values; the component logs (does not throw) when this is non-empty.
 */
export function findDuplicateLeafValues(
  options: CascaderOption[],
): CascaderScalar[] {
  const seen = new Set<string>();
  const duplicates: CascaderScalar[] = [];
  for (const leaf of collectAllLeaves(options)) {
    const key = serializeLeaf(leaf.value);
    if (seen.has(key)) {
      duplicates.push(leaf.value);
    } else {
      seen.add(key);
    }
  }
  return duplicates;
}

/**
 * OUTPUT boundary: convert the internal selection (always a list of paths) into the wire `value`.
 * - `full_path=true`: pass paths through unchanged — a list of paths (multi) or a single path / `null` (single).
 * - `full_path=false`: emit bare leaf scalars — a list of leaves (multi) or a single leaf / `null` (single).
 */
export function toWire(
  paths: CascaderPath[],
  multi: boolean,
  fullPath: boolean,
): CascaderPath | CascaderPath[] | CascaderScalar | CascaderScalar[] | null {
  const leafOf = (path: CascaderPath): CascaderScalar => path[path.length - 1];
  if (multi) {
    return fullPath ? paths : paths.map(leafOf);
  }
  if (paths.length === 0) return null;
  return fullPath ? paths[0] : leafOf(paths[0]);
}

/**
 * INPUT boundary: normalize an incoming wire `value` into the internal list-of-paths form.
 * - `full_path=true`: `value` already carries paths (a single path or a list of paths).
 * - `full_path=false`: `value` carries leaf scalars; each is resolved to its path via `leafToPath`.
 *
 * Tolerant by design: any leaf/path that does not resolve to a current leaf is dropped (multi) or
 * yields no selection (single), so a stale persisted value of the wrong shape degrades gracefully
 * rather than crashing.
 */
export function fromWire(
  value: unknown,
  leafToPath: Map<string, CascaderPath>,
  multi: boolean,
  fullPath: boolean,
): CascaderPath[] {
  if (value === null || value === undefined) return [];
  if (fullPath) {
    if (multi) return Array.isArray(value) ? (value as CascaderPath[]) : [];
    // A single path must be a non-empty array; treat [] as no selection.
    return Array.isArray(value) && value.length > 0
      ? [value as CascaderPath]
      : [];
  }
  // Leaf mode: resolve each bare leaf scalar to its full path.
  const resolve = (leaf: unknown): CascaderPath | undefined =>
    leafToPath.get(serializeLeaf(leaf));
  if (multi) {
    if (!Array.isArray(value)) return [];
    return (value as unknown[])
      .map(resolve)
      .filter((p): p is CascaderPath => p !== undefined);
  }
  const path = resolve(value);
  return path ? [path] : [];
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

/** Collect all leaf nodes under a node (depth-first). Each carries its `path`/`key`. */
export function collectLeaves(option: CascaderOption): CascaderOption[] {
  if (isLeaf(option)) return [option];
  return (option.children ?? []).flatMap(collectLeaves);
}

/** Collect all leaf nodes in the entire options tree (depth-first). */
export function collectAllLeaves(options: CascaderOption[]): CascaderOption[] {
  return options.flatMap(collectLeaves);
}

/**
 * Compute checkbox state for a parent node given the set of selected paths.
 * `selectedPathSet` holds serialized paths (see `serializePath`).
 * Returns 'checked' | 'indeterminate' | 'unchecked'.
 */
export function parentCheckState(
  option: CascaderOption,
  selectedPathSet: Set<string>,
): "checked" | "indeterminate" | "unchecked" {
  const leaves = collectLeaves(option);
  const selectedCount = leaves.filter((leaf) =>
    selectedPathSet.has(leaf.key),
  ).length;
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
 * Leaf hits are identified by their `option.path` (identity-safe for duplicate labels).
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
