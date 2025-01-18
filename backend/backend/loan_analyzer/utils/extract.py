import pandas as pd
import numpy as np
import pdfplumber
import re
import pickle
import os

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF bank statement
    Returns concatenated text from all pages
    """
    full_text = ""
    try:
        print(f"File size: {os.path.getsize(pdf_path)} bytes")
        
        with pdfplumber.open(pdf_path) as pdf:
           
            print(f"PDF opened successfully")
            print(f"Number of pages: {len(pdf.pages)}")
            
            if not pdf.pages:
                raise Exception("PDF contains no pages")
                
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    text = page.extract_text()
                    
                    # DEBUGGING SECTION
                    print(f"Page {page_num} text length: {len(text) if text else 0}")
                    if text and len(text.strip()) > 0:
                        full_text += text + "\n"
                    else:
                        print(f"Warning: Page {page_num} contains no readable text")
                except Exception as page_error:
                    print(f"Warning: Error extracting text from page {page_num}: {str(page_error)}")
                    
                    print(f"Page {page_num} properties: {page.attrs if hasattr(page, 'attrs') else 'No attrs'}")
                    continue
                    
        if not full_text.strip():
            raise Exception("No readable text could be extracted from the PDF")
            
        return full_text
        
    except Exception as e:
        print(f"Detailed error while processing PDF: {str(e)}")
        raise Exception(f"Error processing PDF: {str(e)}")

def clean_amount(amount_str):
    """
    Clean and convert amount string to float
    Handles various number formats including European style
    """
    try:
        # Remove any currency symbols and whitespace
        cleaned = re.sub(r'[£$€\s,]', '', str(amount_str))
        
        # Handle negative amounts with parentheses
        if '(' in cleaned and ')' in cleaned:
            cleaned = cleaned.replace('(', '-').replace(')', '')
            
        # Handle European number format (1.234,56 -> 1234.56)
        if ',' in cleaned and '.' in cleaned:
            if cleaned.index(',') > cleaned.index('.'):
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            cleaned = cleaned.replace(',', '.')
            
        return float(cleaned)
    except (ValueError, AttributeError):
        return None

def extract_transactions(pdf_path):
    """
    Extract and structure transaction data from PDF bank statement
    Returns list of transaction dictionaries with specified fields
    """
    transactions = []
    
    statement_text = extract_text_from_pdf(pdf_path)
    
    lines = statement_text.split('\n')
    current_balance = None
    
    # Regular expressions for different date formats
    date_patterns = [
        r'\d{2}\s+[A-Za-z]{3}\s+\d{2}',   # DD MMM YY
        r'\d{2}-[A-Za-z]{3}-\d{4}',        # DD-MMM-YYYY
        r'\d{2}/\d{2}/\d{4}',              # DD/MM/YYYY
        r'\d{2}-\d{2}-\d{4}',              # DD-MM-YYYY
        r'\d{2}\.\d{2}\.\d{4}',            # DD.MM.YYYY
        r'[A-Za-z]{3}\s+\d{2},\s*\d{4}',   # MMM DD, YYYY
        r'\d{1,2}/\d{1,2}/\d{2,4}',        # D/M/YY or DD/MM/YYYY
        r'\d{1,2}-\d{1,2}-\d{2,4}'         # D-M-YY or DD-MM-YYYY
    ]
    date_pattern = '|'.join(date_patterns)
    
    amount_patterns = [
        r'\(?\$?\s*[\d,]+\.?\d*\)?',       # Handles (1234.56) and $1,234.56
        r'\(?\s*[\d,]+\.?\d*\)?',          # Basic number format with optional decimal
        r'\(?\s*[\d\.]+,?\d*\)?',          # European format with optional decimal
        r'\(?\$\s*[\d,]+\.?\d*\)?',        # USD format
        r'\(?\€\s*[\d\.]+,?\d*\)?',        # EUR format
        r'\(?\£\s*[\d,]+\.?\d*\)?',        # GBP format
        r'\(?\d+(?:[.,]\d{2})?\)?'         # Simple number with optional decimals
    ]
    amount_pattern = '|'.join(amount_patterns)

    # Transaction type keywords - expanded
    transaction_keywords = {
        'CASH_OUT': ['ATM', 'WITHDRAWAL', 'WITHDRAW', 'CASH OUT', 'CASHOUT'],
        'CASH_IN': ['DEPOSIT', 'DEP', 'CASH IN', 'CASHIN', 'CREDIT'],
        'DEBIT': ['DEBIT', 'POS', 'PURCHASE', 'PAYMENT TO', 'PAID TO', 'DR'],
        'PAYMENT': ['PAYMENT', 'BILL PAY', 'AUTOPAY', 'PMT', 'FEE', 'DIRECT DEBIT'],
        'TRANSFER': ['TRANSFER', 'TRF', 'XFER', 'ACH', 'IMPS', 'NEFT', 'UPI', 'SWIFT', 'CR']
    }

    # DEBUGGING SECTION 
    total_lines = 0
    lines_with_dates = 0
    lines_with_amounts = 0
    
    for line in lines:
        total_lines += 1
        if not line.strip():
            continue
            
        try:
            date_match = re.search(date_pattern, line)
            if date_match:
                lines_with_dates += 1
            
        
            debit_amount = None
            credit_amount = None
            
            columns = line.split()
            
            is_debit = 'DR' in line.upper() or '(DR)' in line.upper()
            is_credit = 'CR' in line.upper() or '(CR)' in line.upper()
            
            amount_matches = re.findall(amount_pattern, line)
            if amount_matches:
                lines_with_amounts += 1
                
                for amount_str in amount_matches:
                    amount = clean_amount(amount_str)
                    if amount is not None:
                        
                        if is_debit or '(' in amount_str or amount < 0:
                            debit_amount = abs(amount)
                        elif is_credit or amount > 0:
                            credit_amount = abs(amount)
                        else:
                           
                            credit_amount = abs(amount)
            
            if not (date_match and (debit_amount is not None or credit_amount is not None)):
                continue
                
            transaction_date = date_match.group(0)
            
            line_upper = line.upper()
            transaction_type = None
            
            for type_name, keywords in transaction_keywords.items():
                if any(keyword.upper() in line_upper for keyword in keywords):
                    transaction_type = type_name
                    break
            
            if transaction_type is None:
                if debit_amount is not None:
                    transaction_type = 'DEBIT'
                else:
                    transaction_type = 'CASH_IN'
            
            amount = debit_amount if debit_amount is not None else credit_amount
            
            # Calculate balances
            if current_balance is None:
                # Look for balance in the line
                balance_matches = re.findall(amount_pattern, line)
                if balance_matches:
                    current_balance = clean_amount(balance_matches[-1])
                    
            new_balance = current_balance
            if current_balance is not None:
                if debit_amount is not None:
                    old_balance = current_balance + debit_amount
                else:
                    old_balance = current_balance - credit_amount
            else:
                old_balance = 0
                new_balance = 0
            
            transaction = {
                'amount': abs(amount),
                'oldbalanceOrg': old_balance,
                'newbalanceOrig': new_balance,
                'oldbalanceDest': 0,
                'newbalanceDest': 0,
                'type_CASH_IN': 1 if transaction_type == 'CASH_IN' else 0,
                'type_CASH_OUT': 1 if transaction_type == 'CASH_OUT' else 0,
                'type_DEBIT': 1 if transaction_type == 'DEBIT' else 0,
                'type_PAYMENT': 1 if transaction_type == 'PAYMENT' else 0,
                'type_TRANSFER': 1 if transaction_type == 'TRANSFER' else 0,
                'is_large_transaction': abs(amount) >= 5000,
                'balance_difference': new_balance - old_balance,
                'transaction_date': transaction_date,
                'description': line.strip()
            }
            
            transactions.append(transaction)
            current_balance = new_balance
            
        except Exception as e:
            print(f"Error processing line: {line}")
            print(f"Error details: {str(e)}")
            continue
    
    print(f"Processed {total_lines} lines")
    print(f"Found {lines_with_dates} lines with dates")
    print(f"Found {lines_with_amounts} lines with amounts")
    print(f"Extracted {len(transactions)} transactions")
    
    return transactions

def analyze_transactions(transactions):
    """
    Analyze extracted transactions and provide summary statistics
    Also performs fraud detection on each transaction
    """
    if not transactions:
        return {"error": "No transactions found"}
        
    df = pd.DataFrame(transactions)
    
    # Load fraud detection model and column names
    try:
        with open("/home/alex/Documents/loan/backend/backend/loan_analyzer/utils/random_forest_fraud_model.pkl", 'rb') as file:
            fraud_model = pickle.load(file)
        with open("/home/alex/Documents/loan/backend/backend/loan_analyzer/utils/column_names.pkl", 'rb') as file:
            column_names = pickle.load(file)
            
        fraud_check_df = df[['amount', 'oldbalanceOrg', 'newbalanceOrig', 
                            'oldbalanceDest', 'newbalanceDest', 'type_CASH_IN',
                            'type_CASH_OUT', 'type_DEBIT', 'type_PAYMENT',
                            'type_TRANSFER', 'is_large_transaction', 
                            'balance_difference']]
        
        fraud_check_df = fraud_check_df.reindex(columns=column_names, fill_value=0)
        
        fraud_predictions = fraud_model.predict(fraud_check_df)
        fraud_probabilities = fraud_model.predict_proba(fraud_check_df)
        
        fraud_threshold = 0.5  # 50% probability threshold for fraud
        high_risk_transactions = [prob[1] > fraud_threshold for prob in fraud_probabilities]
        fraud_count = sum(high_risk_transactions)
        
        avg_fraud_probability = round(np.mean([prob[1] for prob in fraud_probabilities]) * 100, 2)
        
        summary = {
            'total_transactions': len(df),
            'total_cash_out': df['type_CASH_OUT'].sum(),
            'total_cash_in': df['type_CASH_IN'].sum(),
            'total_transfers': df['type_TRANSFER'].sum(),
            'total_payments': df['type_PAYMENT'].sum(),
            'total_debits': df['type_DEBIT'].sum(),
            'large_transactions': df['is_large_transaction'].sum(),
            'avg_transaction_amount': round(df['amount'].mean(), 2),
            'max_transaction_amount': df['amount'].max(),
            'min_transaction_amount': df['amount'].min(),
            'date_range': f"{df['transaction_date'].iloc[0]} to {df['transaction_date'].iloc[-1]}",
            'total_debit_amount': round(df[df['balance_difference'] < 0]['amount'].sum(), 2),
            'total_credit_amount': round(df[df['balance_difference'] > 0]['amount'].sum(), 2),
            'fraud_analysis': {
                'total_fraudulent': int(fraud_count),
                'fraud_percentage': round((fraud_count / len(df)) * 100, 2),
                'average_fraud_probability': avg_fraud_probability
            }
        }
        
        for i, transaction in enumerate(transactions):
            transaction['is_fraudulent'] = bool(high_risk_transactions[i])
            transaction['fraud_probability'] = round(float(fraud_probabilities[i][1]) * 100, 2)
            
        return summary
        
    except Exception as e:
        print(f"Error in fraud detection: {str(e)}")
        # Return basic summary without fraud analysis
        return {
            'total_transactions': len(df),
            'total_cash_out': df['type_CASH_OUT'].sum(),
            'total_cash_in': df['type_CASH_IN'].sum(),
            'total_transfers': df['type_TRANSFER'].sum(),
            'total_payments': df['type_PAYMENT'].sum(),
            'total_debits': df['type_DEBIT'].sum(),
            'large_transactions': df['is_large_transaction'].sum(),
            'avg_transaction_amount': round(df['amount'].mean(), 2),
            'max_transaction_amount': df['amount'].max(),
            'min_transaction_amount': df['amount'].min(),
            'date_range': f"{df['transaction_date'].iloc[0]} to {df['transaction_date'].iloc[-1]}",
            'total_debit_amount': round(df[df['balance_difference'] < 0]['amount'].sum(), 2),
            'total_credit_amount': round(df[df['balance_difference'] > 0]['amount'].sum(), 2)
        }

def analyze_bank_statement(pdf_path):
    """
    Main function to analyze bank statement PDF
    Returns dictionary containing transactions and summary
    """
    try:
        # Extract transactions
        transactions = extract_transactions(pdf_path)
        
        if not transactions:
            return {
                "error": "No transactions could be extracted from the PDF",
                "transactions": [],
                "summary": None
            }
            
        # Analyze transactions
        summary = analyze_transactions(transactions)
        
        return {
            "transactions": transactions,
            "summary": summary
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "transactions": [],
            "summary": None
        }
    
if __name__ == "__main__":
    pdf_path = "/home/alex/Documents/loan/backend/ml/bank1.pdf"
    result = analyze_bank_statement(pdf_path)
    print(result)