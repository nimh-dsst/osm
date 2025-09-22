#!/usr/bin/env python3
"""
Script to compare two matches parquet files and generate confusion matrices
for key columns using left join on PMID column.
Written with the help of Grok Code Fast 1.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns
    from sklearn.metrics import confusion_matrix
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install required packages:")
    print("pip install pandas numpy scikit-learn matplotlib seaborn")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_parquet_file(file_path: Path) -> Optional[pd.DataFrame]:
    """
    Load parquet file into pandas DataFrame.

    Args:
        file_path: Path to the parquet file

    Returns:
        DataFrame or None if loading fails
    """
    try:
        logger.info(f"Loading parquet file: {file_path}")
        df = pd.read_parquet(file_path)
        logger.info(f"Successfully loaded parquet file. Shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        logger.error(f"Failed to load parquet file {file_path}: {e}")
        return None


def compare_column_names(
    df1: pd.DataFrame, df2: pd.DataFrame, name1: str, name2: str
) -> None:
    """
    Compare column names between two DataFrames and log differences.

    Args:
        df1: First DataFrame
        df2: Second DataFrame
        name1: Name of first dataset
        name2: Name of second dataset
    """
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)

    logger.info("\n=== Column Comparison ===")
    logger.info(f"{name1} columns ({len(cols1)}): {sorted(cols1)}")
    logger.info(f"{name2} columns ({len(cols2)}): {sorted(cols2)}")

    if cols1 == cols2:
        logger.info("✓ Column names match exactly!")
    else:
        only_in_1 = cols1 - cols2
        only_in_2 = cols2 - cols1

        if only_in_1:
            logger.warning(f"Columns only in {name1}: {sorted(only_in_1)}")
        if only_in_2:
            logger.warning(f"Columns only in {name2}: {sorted(only_in_2)}")


def perform_left_join(
    df_ground_truth: pd.DataFrame,
    df_comparison: pd.DataFrame,
    join_column: str = "pmid",
) -> pd.DataFrame:
    """
    Perform left join on the specified column.

    Args:
        df_ground_truth: Ground truth DataFrame (left side)
        df_comparison: Comparison DataFrame (right side)
        join_column: Column to join on

    Returns:
        Merged DataFrame
    """
    logger.info("\n=== Performing Left Join ===")
    logger.info(f"Ground truth shape: {df_ground_truth.shape}")
    logger.info(f"Comparison shape: {df_comparison.shape}")

    # Check if join column exists in both DataFrames
    if join_column not in df_ground_truth.columns:
        raise ValueError(
            f"Join column '{join_column}' not found in ground truth DataFrame"
        )
    if join_column not in df_comparison.columns:
        raise ValueError(
            f"Join column '{join_column}' not found in comparison DataFrame"
        )

    # Perform left join
    merged_df = df_ground_truth.merge(
        df_comparison,
        on=join_column,
        how="left",
        suffixes=("_ground_truth", "_comparison"),
    )

    logger.info(f"Merged shape: {merged_df.shape}")

    # Check for unmatched records (right join columns will be NaN for unmatched left records)
    # Since we're doing left join, we need to check if any of the comparison columns are NaN
    comparison_cols = [col for col in merged_df.columns if col.endswith("_comparison")]
    if comparison_cols:
        unmatched = merged_df[merged_df[comparison_cols[0]].isna()]
        if len(unmatched) > 0:
            logger.warning(
                f"Found {len(unmatched)} unmatched records in comparison dataset"
            )

    return merged_df


def create_confusion_matrix(
    y_true: pd.Series,
    y_pred: pd.Series,
    column_name: str,
    normalize: str = "true",
) -> Dict[str, Any]:
    """
    Create confusion matrix for binary classification.

    Args:
        y_true: Ground truth values
        y_pred: Predicted/comparison values
        column_name: Name of the column being compared
        normalize: Normalization mode for confusion matrix

    Returns:
        Dictionary containing confusion matrix data and metrics
    """
    # Remove NaN values for confusion matrix calculation
    valid_mask = ~(y_true.isna() | y_pred.isna())
    y_true_clean = y_true[valid_mask]
    y_pred_clean = y_pred[valid_mask]

    if len(y_true_clean) == 0:
        logger.warning(f"No valid data for {column_name} after removing NaN values")
        return None

    # Convert to consistent boolean type to handle mixed data types
    try:
        y_true_clean = y_true_clean.astype(bool)
        y_pred_clean = y_pred_clean.astype(bool)
    except (ValueError, TypeError) as e:
        logger.warning(
            f"Could not convert {column_name} to boolean type: {e}. "
            f"Data types: y_true={y_true_clean.dtype}, y_pred={y_pred_clean.dtype}"
        )
        # Try to convert string representations
        y_true_clean = pd.Series(
            [str(x).lower() in ["true", "1", "yes"] for x in y_true_clean]
        )
        y_pred_clean = pd.Series(
            [str(x).lower() in ["true", "1", "yes"] for x in y_pred_clean]
        )

    # Calculate confusion matrix
    cm = confusion_matrix(y_true_clean, y_pred_clean, normalize=normalize)

    # Calculate additional metrics
    accuracy = np.mean(y_true_clean == y_pred_clean)
    true_positives = np.sum((y_true_clean & y_pred_clean))
    true_negatives = np.sum((not y_true_clean) & (not y_pred_clean))
    false_positives = np.sum((not y_true_clean) & (y_pred_clean))
    false_negatives = np.sum((y_true_clean) & (not y_pred_clean))

    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0
    )
    f1_score = (
        2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    )

    return {
        "confusion_matrix": cm,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "true_positives": true_positives,
        "true_negatives": true_negatives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "total_samples": len(y_true_clean),
        "matrix_type": "binary",
    }


def plot_confusion_matrix(
    cm_dict: Dict[str, Any],
    column_name: str,
    save_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
):
    """
    Plot confusion matrix using seaborn.

    Args:
        cm_dict: Dictionary containing confusion matrix data
        column_name: Name of the column
        save_path: Optional path to save the plot
        output_dir: Optional directory to save the plot
    """
    if cm_dict is None:
        return

    cm = cm_dict["confusion_matrix"]

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt=".3f",
        cmap="Blues",
        xticklabels=["False", "True"],
        yticklabels=["False", "True"],
    )

    plt.title(f"Confusion Matrix for {column_name}")
    plt.ylabel("Ground Truth")
    plt.xlabel("Comparison Dataset")

    if save_path:
        plt.savefig(save_path, dpi=600, bbox_inches="tight")
        logger.info(f"Saved confusion matrix plot to {save_path}")
    elif output_dir:
        # If no specific save path but output_dir is provided, create file in output_dir
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(exist_ok=True, parents=True)
        save_path = output_dir_path / f"confusion_matrix_{column_name}.png"
        plt.savefig(save_path, dpi=600, bbox_inches="tight")
        logger.info(f"Saved confusion matrix plot to {save_path}")
    # If neither save_path nor output_dir is provided, don't save the file

    # Don't show plot in headless environments, just save it
    plt.close()


def compare_string_columns(
    y_true: pd.Series, y_pred: pd.Series, column_name: str
) -> Dict[str, Any]:
    """
    Compare string columns and calculate similarity metrics.

    Args:
        y_true: Ground truth values
        y_pred: Comparison values
        column_name: Name of the column

    Returns:
        Dictionary with comparison statistics
    """
    # Remove NaN values
    valid_mask = ~(y_true.isna() | y_pred.isna())
    y_true_clean = y_true[valid_mask]
    y_pred_clean = y_pred[valid_mask]

    if len(y_true_clean) == 0:
        logger.warning(f"No valid data for {column_name} after removing NaN values")
        return None

    try:
        # Handle potential list/array columns by converting to string representation
        y_true_str = y_true_clean.astype(str)
        y_pred_str = y_pred_clean.astype(str)

        # Exact matches
        exact_matches = np.sum(y_true_str == y_pred_str)
        accuracy = exact_matches / len(y_true_clean)

        # Unique values
        unique_ground_truth = y_true_str.nunique()
        unique_comparison = y_pred_str.nunique()

        return {
            "accuracy": accuracy,
            "exact_matches": exact_matches,
            "total_comparisons": len(y_true_clean),
            "unique_ground_truth": unique_ground_truth,
            "unique_comparison": unique_comparison,
        }
    except Exception as e:
        logger.warning(
            f"Error comparing {column_name}: {e}. "
            f"Data types: y_true={y_true_clean.dtype}, y_pred={y_pred_clean.dtype}"
        )
        # Return basic info even if comparison fails
        return {
            "accuracy": 0.0,
            "exact_matches": 0,
            "total_comparisons": len(y_true_clean),
            "unique_ground_truth": 0,
            "unique_comparison": 0,
            "error": str(e),
        }


def generate_comparison_report(
    merged_df: pd.DataFrame,
    columns_to_compare: list,
    ground_truth_suffix: str = "_ground_truth",
    comparison_suffix: str = "_comparison",
    output_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Generate comprehensive comparison report for all specified columns.

    Args:
        merged_df: Merged DataFrame
        columns_to_compare: List of columns to compare
        ground_truth_suffix: Suffix for ground truth columns
        comparison_suffix: Suffix for comparison columns
        output_dir: Optional path to save the output

    Returns:
        DataFrame containing summary metrics for all columns
    """
    logger.info(f"\n{'=' * 50}")
    logger.info("COMPARISON REPORT")
    logger.info(f"{'=' * 50}")

    # Initialize list to collect summary metrics
    summary_metrics = []

    for column in columns_to_compare:
        gt_col = f"{column}{ground_truth_suffix}"
        comp_col = f"{column}{comparison_suffix}"

        # Check if columns exist
        if gt_col not in merged_df.columns:
            logger.warning(f"Ground truth column {gt_col} not found, skipping {column}")
            continue
        if comp_col not in merged_df.columns:
            logger.warning(f"Comparison column {comp_col} not found, skipping {column}")
            continue

        logger.info(f"\n--- Analysis for {column} ---")

        # Get the data
        y_true = merged_df[gt_col]
        y_pred = merged_df[comp_col]

        # Preprocess funder columns to convert empty arrays and NaN values to None
        if column == "funder":
            logger.info("Preprocessing funder column values...")

            # Convert empty arrays to None for both ground truth and comparison
            y_true = y_true.apply(
                lambda x: None
                if isinstance(x, (list, np.ndarray)) and len(x) == 0
                else x
            )
            y_pred = y_pred.apply(
                lambda x: None
                if isinstance(x, (list, np.ndarray)) and len(x) == 0
                else x
            )

        # Initialize metrics dictionary
        metrics = {
            "column": column,
            "data_type": "unknown",
            "total_samples": len(y_true),
            "valid_samples": (~y_true.isna() & ~y_pred.isna()).sum(),
        }

        # Check data types
        if y_true.dtype == "bool" or y_pred.dtype == "bool":
            # Binary classification
            cm_dict = create_confusion_matrix(y_true, y_pred, column)
            if cm_dict:
                logger.info(f"Accuracy: {cm_dict['accuracy']:.4f}")
                logger.info(f"Precision: {cm_dict['precision']:.4f}")
                logger.info(f"Recall: {cm_dict['recall']:.4f}")
                logger.info(f"F1 Score: {cm_dict['f1_score']:.4f}")
                logger.info(f"True Positives: {cm_dict['true_positives']}")
                logger.info(f"True Negatives: {cm_dict['true_negatives']}")
                logger.info(f"False Positives: {cm_dict['false_positives']}")
                logger.info(f"False Negatives: {cm_dict['false_negatives']}")
                logger.info(f"Total valid samples: {cm_dict['total_samples']}")

                # Update metrics
                metrics.update(
                    {
                        "data_type": "binary",
                        "accuracy": cm_dict["accuracy"],
                        "precision": cm_dict["precision"],
                        "recall": cm_dict["recall"],
                        "f1_score": cm_dict["f1_score"],
                        "true_positives": cm_dict["true_positives"],
                        "true_negatives": cm_dict["true_negatives"],
                        "false_positives": cm_dict["false_positives"],
                        "false_negatives": cm_dict["false_negatives"],
                        "exact_match_accuracy": cm_dict[
                            "accuracy"
                        ],  # Same as accuracy for binary
                        "exact_matches": None,
                        "unique_ground_truth": None,
                        "unique_comparison": None,
                    }
                )

                # Generate and save confusion matrix plot
                plot_confusion_matrix(cm_dict, column, None, output_dir)

        else:
            # String/categorical comparison
            comp_dict = compare_string_columns(y_true, y_pred, column)
            if comp_dict and "error" not in comp_dict:
                logger.info(f"Exact Match Accuracy: {comp_dict['accuracy']:.4f}")
                logger.info(f"Exact Matches: {comp_dict['exact_matches']}")
                logger.info(f"Total Comparisons: {comp_dict['total_comparisons']}")
                logger.info(
                    f"Unique values (Ground Truth): {comp_dict['unique_ground_truth']}"
                )
                logger.info(
                    f"Unique values (Comparison): {comp_dict['unique_comparison']}"
                )

                # Update metrics
                metrics.update(
                    {
                        "data_type": "categorical",
                        "accuracy": comp_dict["accuracy"],
                        "precision": None,
                        "recall": None,
                        "f1_score": None,
                        "true_positives": None,
                        "true_negatives": None,
                        "false_positives": None,
                        "false_negatives": None,
                        "exact_match_accuracy": comp_dict["accuracy"],
                        "exact_matches": comp_dict["exact_matches"],
                        "unique_ground_truth": comp_dict["unique_ground_truth"],
                        "unique_comparison": comp_dict["unique_comparison"],
                    }
                )

        # Add metrics to summary list
        summary_metrics.append(metrics)

    # Create summary dataframe
    summary_df = pd.DataFrame(summary_metrics)

    # Save summary to CSV if output_dir is provided
    if output_dir:
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(exist_ok=True, parents=True)
        csv_path = output_dir_path / "comparison_summary.csv"
        summary_df.to_csv(csv_path, index=False)
        logger.info(f"Saved comparison summary to {csv_path}")

    return summary_df


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Compare two parquet files and generate confusion matrices for key columns using left join on PMID column."
    )

    parser.add_argument(
        "--ground-truth",
        type=str,
        required=True,
        help="Path to the ground truth parquet file",
    )

    parser.add_argument(
        "--comparison",
        type=str,
        required=True,
        help="Path to the comparison parquet file",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        help="Optional directory to save confusion matrix plots and merged dataframe",
    )

    parser.add_argument(
        "--save-merged",
        action="store_true",
        help="Save the merged dataframe as a parquet file (requires --output-dir)",
    )

    return parser.parse_args()


def main():
    """Main function to run the comparison analysis."""

    # Parse command line arguments
    args = parse_arguments()

    # Validate arguments
    if args.save_merged and not args.output_dir:
        logger.error("--save-merged requires --output-dir to be specified")
        sys.exit(1)

    # File paths from arguments
    ground_truth_file = Path(args.ground_truth)
    comparison_file = Path(args.comparison)
    output_dir = Path(args.output_dir) if args.output_dir else None

    # Validate input files
    if not ground_truth_file.exists():
        logger.error(f"Ground truth file not found: {ground_truth_file}")
        sys.exit(1)

    if not comparison_file.exists():
        logger.error(f"Comparison file not found: {comparison_file}")
        sys.exit(1)

    # Load data
    logger.info("Loading datasets...")
    df_ground_truth = load_parquet_file(ground_truth_file)
    df_comparison = load_parquet_file(comparison_file)

    if df_ground_truth is None or df_comparison is None:
        logger.error("Failed to load one or both datasets")
        sys.exit(1)

    # Compare column names
    compare_column_names(
        df_ground_truth,
        df_comparison,
        "matches.parquet",
        "matches_new.parquet",
    )

    # Perform left join on PMID
    try:
        merged_df = perform_left_join(
            df_ground_truth, df_comparison, join_column="pmid"
        )
    except ValueError as e:
        logger.error(f"Join failed: {e}")
        sys.exit(1)

    # Columns to compare (as specified in requirements)
    columns_to_compare = [
        "is_open_code",
        "is_open_data",
        "year",
        "journal",
        "affiliation_country",
        "funder",
    ]

    # Generate comparison report
    _ = generate_comparison_report(merged_df, columns_to_compare, output_dir=output_dir)

    # Save merged dataframe if requested
    if args.save_merged:
        output_dir_path = Path(args.output_dir)
        output_dir_path.mkdir(exist_ok=True, parents=True)
        merged_file_path = output_dir_path / "merged_comparison.parquet"
        merged_df.to_parquet(merged_file_path, index=False)
        logger.info(f"Saved merged dataframe to {merged_file_path}")

    logger.info("\nAnalysis completed successfully!")


if __name__ == "__main__":
    main()
