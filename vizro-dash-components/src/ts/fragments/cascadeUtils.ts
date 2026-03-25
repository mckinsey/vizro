export type CascadeOption = {
  label: string;
  value: string | number;
  disabled?: boolean;
  children?: CascadeOption[];
};

/** True if the node has no children (i.e. is a leaf). */
export function isLeaf(option: CascadeOption): boolean {
  return !option.children || option.children.length === 0;
}

/**
 * Walk `options` following `activePath` and return each column's items.
 * Column 0 is always the root. Column N is children of activePath[N-1] in column N-1.
 * If the path becomes invalid (index out of range or node has no children),
 * the walk stops and the path is effectively truncated.
 */
export function buildColumns(
  options: CascadeOption[],
  activePath: number[]
): CascadeOption[][] {
  const columns: CascadeOption[][] = [options];
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
export function collectLeaves(option: CascadeOption): (string | number)[] {
  if (isLeaf(option)) return [option.value];
  return (option.children ?? []).flatMap(collectLeaves);
}

/** Collect all leaf values in the entire options tree. */
export function collectAllLeaves(options: CascadeOption[]): (string | number)[] {
  return options.flatMap(collectLeaves);
}

/**
 * Compute checkbox state for a parent node given selected leaf values.
 * Returns 'checked' | 'indeterminate' | 'unchecked'.
 */
export function parentCheckState(
  option: CascadeOption,
  selectedSet: Set<string | number>
): 'checked' | 'indeterminate' | 'unchecked' {
  const leaves = collectLeaves(option);
  const selectedCount = leaves.filter(v => selectedSet.has(v)).length;
  if (selectedCount === 0) return 'unchecked';
  if (selectedCount === leaves.length) return 'checked';
  return 'indeterminate';
}

/**
 * Flat list of matching leaf nodes for search.
 * Returns {option, breadcrumb} where breadcrumb is e.g. "Asia › China".
 */
export function searchOptions(
  options: CascadeOption[],
  query: string,
  ancestors: string[] = []
): { option: CascadeOption; breadcrumb: string }[] {
  const lower = query.toLowerCase();
  const results: { option: CascadeOption; breadcrumb: string }[] = [];
  for (const opt of options) {
    if (isLeaf(opt)) {
      if (opt.label.toLowerCase().includes(lower)) {
        results.push({
          option: opt,
          breadcrumb: ancestors.join(' › '),
        });
      }
    } else {
      results.push(
        ...searchOptions(opt.children ?? [], query, [...ancestors, opt.label])
      );
    }
  }
  return results;
}
