"""Branch name normalization and multi-source data merging."""

import pandas as pd

from config import BRANCH_NAME_MAP, PAZ_BRANCHES, MASTER_COLUMNS, MASTER_BRANCH_ORDER


def normalize_branch(name: str, is_paz_context: bool = False) -> str:
    """Map a raw branch name to the master file's branch name."""
    if not name or not isinstance(name, str):
        return name
    name = name.strip()

    # Direct lookup
    if name in BRANCH_NAME_MAP:
        return BRANCH_NAME_MAP[name]

    # Try partial matching for Paz PDF names (which can be messy)
    name_lower = name
    for key, val in BRANCH_NAME_MAP.items():
        if key in name_lower or name_lower in key:
            return val

    return name


def merge_all(
    csv_data: pd.DataFrame,
    avg_trans_data: pd.DataFrame,
    portions_data: pd.DataFrame,
    hourly_data: pd.DataFrame,
    paz_sales_list: list,
    paz_portions_list: list,
) -> pd.DataFrame:
    """Merge all parsed data into a single DataFrame matching master format."""

    # Start with non-Paz branches from CSV
    if csv_data is not None and not csv_data.empty:
        merged = csv_data[["סניף", 'מכר כולל מע"מ']].copy()
    else:
        merged = pd.DataFrame(columns=["סניף", 'מכר כולל מע"מ'])

    # Merge average transactions
    if avg_trans_data is not None and not avg_trans_data.empty:
        avg_cols = ["סניף"]
        if "ממוצע עסקאות" in avg_trans_data.columns:
            avg_cols.append("ממוצע עסקאות")
        if "מס' עסקאות" in avg_trans_data.columns:
            avg_cols.append("מס' עסקאות")
        merged = merged.merge(avg_trans_data[avg_cols], on="סניף", how="outer")

    # Merge portions
    if portions_data is not None and not portions_data.empty:
        merged = merged.merge(
            portions_data[["סניף", "מנות בפיתה", "ארוחות בפיתה"]],
            on="סניף",
            how="outer",
        )

    # Merge hourly (first/last transaction)
    if hourly_data is not None and not hourly_data.empty:
        merged = merged.merge(
            hourly_data[["סניף", "עסקה ראשונה", "עסקה אחרונה"]],
            on="סניף",
            how="outer",
        )

    # Add Paz sales data
    for paz_sales in paz_sales_list:
        if paz_sales is not None and not paz_sales.empty:
            for _, row in paz_sales.iterrows():
                branch = row["סניף"]
                if branch in PAZ_BRANCHES:
                    mask = merged["סניף"] == branch
                    if mask.any():
                        for col in row.index:
                            if col != "סניף" and pd.notna(row[col]):
                                merged.loc[mask, col] = row[col]
                    else:
                        merged = pd.concat(
                            [merged, pd.DataFrame([row])], ignore_index=True
                        )

    # Add Paz portions data
    for paz_portions in paz_portions_list:
        if paz_portions is not None and not paz_portions.empty:
            for _, row in paz_portions.iterrows():
                branch = row["סניף"]
                if branch in PAZ_BRANCHES:
                    mask = merged["סניף"] == branch
                    if mask.any():
                        if pd.notna(row.get("מנות בפיתה")):
                            merged.loc[mask, "מנות בפיתה"] = row["מנות בפיתה"]
                        if pd.notna(row.get("ארוחות בפיתה")):
                            merged.loc[mask, "ארוחות בפיתה"] = row["ארוחות בפיתה"]
                    else:
                        new_row = {
                            "סניף": branch,
                            "מנות בפיתה": row.get("מנות בפיתה", 0),
                            "ארוחות בפיתה": row.get("ארוחות בפיתה", 0),
                        }
                        merged = pd.concat(
                            [merged, pd.DataFrame([new_row])], ignore_index=True
                        )

    # Calculate meal percentage
    merged["אחוז ארוחות מתוך מנות"] = merged.apply(
        lambda r: (
            r["ארוחות בפיתה"] / r["מנות בפיתה"]
            if pd.notna(r.get("מנות בפיתה"))
            and pd.notna(r.get("ארוחות בפיתה"))
            and r["מנות בפיתה"] > 0
            else 0
        ),
        axis=1,
    )

    # Ensure all master columns exist
    for col in MASTER_COLUMNS:
        if col not in merged.columns:
            merged[col] = None

    # Reorder columns
    merged = merged[MASTER_COLUMNS]

    # Sort by master branch order
    order_map = {b: i for i, b in enumerate(MASTER_BRANCH_ORDER)}
    merged["_sort"] = merged["סניף"].map(order_map).fillna(99)
    merged = merged.sort_values("_sort").drop(columns=["_sort"]).reset_index(drop=True)

    # Filter out non-branch rows
    merged = merged[merged["סניף"].notna() & (merged["סניף"] != "")]

    return merged
