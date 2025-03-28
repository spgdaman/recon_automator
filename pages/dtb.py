import streamlit as st
import pandas as pd
import numpy as np
import re
from business_logic.auto import is_valid_csv_file_format, is_valid_excel_file_format, is_valid_pdf_file_format, InvalidFileFormatError, pdf_cleaner

def longest_common_substring(s1, s2):
    """Finds the longest continuous matching substring (word sequence) between two texts."""
    words1 = str(s1).lower().split()
    words2 = str(s2).lower().split()
    
    len1, len2 = len(words1), len(words2)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    
    longest_match = 0  # Length of the longest matching substring

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if words1[i - 1] == words2[j - 1]:  # Check word-by-word match
                dp[i][j] = dp[i - 1][j - 1] + 1
                longest_match = max(longest_match, dp[i][j])

    return longest_match

def regex_match_percentage(erp_text, bank_text):
    """Calculates the match percentage based on the longest common continuous word sequence."""
    if pd.isna(erp_text) or pd.isna(bank_text):
        return 0  # No match if either value is NaN
    
    words_erp = str(erp_text).lower().split()  # Convert to lowercase & split into words
    words_bank = str(bank_text).lower().split()

    if not words_erp:
        return 0  # No words to match

    longest_match_length = longest_common_substring(erp_text, bank_text)  # Get longest match length
    match_percentage = (longest_match_length / len(words_erp)) * 100  # Percentage based on ERP text length

    return round(match_percentage, 2)  # Round to 2 decimal places

st.title("🏦 DTB Reconciliation")

# First file uploader with a unique key
bank_statement = st.file_uploader("⬆️ Upload Bank Statement", type=[".xls", ".xlsx"], key="bank_statement")

# Second file uploader with a unique key
erp_transactions = st.file_uploader("⬆️ Upload BRS File", type=[".xls", ".xlsx"], key="erp_transactions")

# Process files if uploaded
if bank_statement:
    st.success("Bank Statement successfully uploaded!")
    with st.expander("Below is the uploaded Bank Statement", expanded=False, icon="🔽"):
        st.write(f"Bank Statement File: {bank_statement.name}")
        bank_statement = pd.read_excel(bank_statement)
        # bank_statement.columns = bank_statement.columns.str.strip()
        # st.write(bank_statement.columns)
        bank_statement["Debits"] = (
            bank_statement["Debits"]
            .astype(str)  # Ensure it's a string before replacing
            .str.replace(",", "", regex=True)  # Remove commas properly
            .str.replace("'", "", regex=True)  # Remove any single quotes if present
            .replace("-", "0")  # Replace dashes with zero
            .astype(float)  # Convert to float
        )
        bank_statement["Credits"] = (
            bank_statement["Credits"]
            .astype(str)  # Ensure all values are treated as strings
            .str.replace(",", "", regex=True)  # Remove commas
            .replace("-", "0")  # Replace dashes with zero
            .astype(float)  # Convert to float
        )
        bank_statement["Transaction Details"] = bank_statement["Transaction Details"].astype("string")
        # bank_statement["Transaction Date"] = pd.to_datetime(bank_statement["Transaction Date"], format="%d/%m/%Y")
        st.markdown("### 🔽 Below is the uploaded Bank Statement")
        # st.write(bank_statement.columns)
        # st.write(bank_statement.dtypes)
        st.write(bank_statement)

if erp_transactions:
    st.success("BRS file successfully uploaded!")
    with st.expander("Below is the uploaded BRS report", expanded=False, icon="🔽"):
        st.write(f"BRS File: {erp_transactions.name}")
        erp_transactions = pd.read_excel(erp_transactions)
        erp_transactions["VOUCHER_DATE"] = pd.to_datetime(erp_transactions["VOUCHER_DATE"], format="%d/%m/%Y")
        erp_transactions["ENTITY_NAME"] = erp_transactions["ENTITY_NAME"].astype("string")
        erp_transactions["NARRATION"] = erp_transactions["NARRATION"].astype("string")
        st.markdown("### 🔽 Below is the uploaded BRS report")
        st.write(erp_transactions.dtypes)
        st.write(erp_transactions)

# Divider to act as a separator
st.divider()

def reconciler(erp_file, bank_file, match_scale):
    if erp_file is not None and bank_file is not None:
        # Check if there are any nonzero values in the 'Credit' and 'Debit' columns
        if (bank_file["Credits"] != 0).any() and (bank_file["Debits"] != 0).any():
            print("It works!")

            # Add Match_Amount column in bank_file to dynamically pick Credit or Debit
            bank_file["Match_Amount"] = np.where(bank_file["Credits"] != 0, bank_file["Credits"], bank_file["Debits"])

            # Perform the merge (inner join with potential matches)
            merged_df = erp_file.merge(
                bank_file[["TransactionDate", "Credits", "Debits", "Transaction Details", "Match_Amount"]],
                left_on=["VOUCHER_DATE", "AMOUNT_SPECIFIC"],
                right_on=["TransactionDate", "Match_Amount"],
                how="inner",  # Using inner join to prevent mismatches
                suffixes=("_ERP", "_BANK")
            )

            # Apply regex match percentage on both NARRATION and ENTITY_NAME
            merged_df["Regex_Match_Percentage"] = merged_df.apply(
                lambda row: max(
                    regex_match_percentage(row["NARRATION"], row["Transaction Details"]),
                    regex_match_percentage(row["ENTITY_NAME"], row["Transaction Details"])
                ),
                axis=1
            )

            filtered_df = merged_df[merged_df["Regex_Match_Percentage"] >= match_scale].reset_index(drop=True)

            # **Remove matched transactions from bank_file**
            unmatched_df = bank_file[
                ~bank_file[["TransactionDate", "Match_Amount", "Transaction Details"]].apply(tuple, axis=1).isin(
                    filtered_df[["TransactionDate", "Match_Amount", "Transaction Details"]].apply(tuple, axis=1)
                )
            ].reset_index(drop=True)

            # Final output
            print(unmatched_df)
            return (
                st.markdown("### ✅ Matched Transactions"),
                st.write(filtered_df),
                st.markdown("### ❌ Unmatched Transactions"),
                st.write(unmatched_df)
            )

        else:
            print("No matching transactions found.")

    else:
        print("It doesn't work!")
    
if bank_statement is None or erp_transactions is None:
    st.markdown("## ⚠️ :red[Please upload both files (Bank Statement and BRS Report) to get started]")
else:
    st.markdown("### Adjust the slider to filter by the chosen % match.")
    match_scale = st.slider("Slide to select the % match", 0, 100)
    reconciler(erp_transactions, bank_statement, match_scale)