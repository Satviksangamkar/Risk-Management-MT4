from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
import logging
import re
import numpy as np
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_numeric_value(text):
    """
    Parse numeric value from text, handling various formats including spaces as thousands separators.
    """
    if not text or text.strip() == '':
        return 0.0
    
    try:
        # Convert to string and clean
        text = str(text).strip()
        
        # Remove parentheses and extract the numeric part
        # Handle cases like "1 379.89 (7)" -> extract "1 379.89"
        if '(' in text:
            text = text.split('(')[0].strip()
        
        # Remove currency symbols and other non-numeric characters except dots, spaces, commas, and minus
        cleaned = re.sub(r'[^\d\s.,-]', '', text)
        
        # Replace spaces with empty string (for thousands separator like "1 237.30")
        cleaned = cleaned.replace(' ', '')
        
        # Replace comma with dot for decimal separator
        cleaned = cleaned.replace(',', '.')
        
        # Handle multiple dots (keep only the last one as decimal separator)
        if cleaned.count('.') > 1:
            parts = cleaned.split('.')
            cleaned = ''.join(parts[:-1]) + '.' + parts[-1]
        
        # Handle empty or just decimal point
        if not cleaned or cleaned == '.' or cleaned == '-':
            return 0.0
            
        return float(cleaned)
    except (ValueError, AttributeError) as e:
        logger.warning(f"Could not parse numeric value '{text}': {e}")
        return 0.0

def extract_percentage_and_count(text):
    """
    Extract percentage and count from text like "8 (80.00%)" or "5 (80.00%)"
    Returns tuple (count, percentage)
    """
    if not text:
        return 0, 0.0
    
    # Pattern to match "number (percentage%)"
    match = re.search(r'(\d+)\s*\((\d+\.?\d*)%\)', str(text))
    if match:
        count = int(match.group(1))
        percentage = float(match.group(2))
        return count, percentage
    
    # If no match, try to extract just the number
    return int(parse_numeric_value(text)), 0.0

def extract_consecutive_stats(text):
    """
    Extract consecutive statistics from text like "7 (1 379.89)" or "1 379.89 (7)"
    Returns tuple (count, amount) or (amount, count)
    """
    if not text:
        return 0, 0.0
    
    # Pattern to match "count (amount)" like "7 (1 379.89)"
    match1 = re.search(r'(\d+)\s*\(([\d\s.-]+)\)', str(text))
    if match1:
        count = int(match1.group(1))
        amount = parse_numeric_value(match1.group(2))
        return count, amount
    
    # Pattern to match "amount (count)" like "1 379.89 (7)"
    match2 = re.search(r'([\d\s.-]+)\s*\((\d+)\)', str(text))
    if match2:
        amount = parse_numeric_value(match2.group(1))
        count = int(match2.group(2))
        return count, amount
    
    return 0, 0.0

def extract_account_info(soup):
    """
    Extract account information from the specific HTML structure.
    """
    print("\n1. ACCOUNT INFORMATION:")
    print("-" * 50)
    
    account_info = {}
    
    # Find the account info row
    account_row = soup.find('tr', align='left')
    if account_row:
        # Extract all bold text from the row
        bold_elements = account_row.find_all('b')
        
        for element in bold_elements:
            text = element.get_text().strip()
            
            # Extract Account number
            if text.startswith('Account:'):
                account_num = text.replace('Account:', '').strip()
                account_info['account_number'] = account_num
                print(f"  Account Number: {account_num}")
            
            # Extract Name
            elif text.startswith('Name:'):
                name = text.replace('Name:', '').strip()
                account_info['account_name'] = name
                print(f"  Account Name: {name}")
            
            # Extract Currency
            elif text.startswith('Currency:'):
                currency = text.replace('Currency:', '').strip()
                account_info['currency'] = currency
                print(f"  Currency: {currency}")
            
            # Extract Leverage (handle empty case)
            elif text.startswith('Leverage:'):
                leverage_text = text.replace('Leverage:', '').strip()
                if '<!--LEVERAGE-->' in element.parent.get_text() or not leverage_text:
                    leverage = "Not specified"
                else:
                    leverage = leverage_text
                account_info['leverage'] = leverage
                print(f"  Leverage: {leverage}")
            
            # Extract date/time
            elif re.search(r'\d{4}\s+\w+\s+\d{1,2},\s+\d{1,2}:\d{2}', text):
                account_info['report_date'] = text
                print(f"  Report Date: {text}")
    
    return account_info

def extract_financial_summary(soup):
    """
    Extract financial summary from the specific HTML structure.
    Revised to handle colspan attributes properly.
    """
    print("\n2. FINANCIAL SUMMARY:")
    print("-" * 50)
    
    financial_data = {}
    labels = [
        'Deposit/Withdrawal:', 'Credit Facility:', 'Closed Trade P/L:',
        'Floating P/L:', 'Margin:', 'Balance:', 'Equity:', 'Free Margin:'
    ]
    
    # Find all rows in the document
    rows = soup.find_all('tr')
    
    for row in rows:
        # Only process rows with right alignment
        if 'right' in row.get('align', ''):
            cells = row.find_all(['td', 'th'])
            current_label = None
            
            for cell in cells:
                # Check if cell contains a bold element with a label
                bold = cell.find('b')
                if bold:
                    label_text = bold.get_text().strip()
                    if label_text in labels:
                        current_label = label_text
                
                # Check if cell is a value cell
                if 'mspt' in cell.get('class', []) and current_label:
                    value_text = cell.get_text().strip()
                    value = parse_numeric_value(value_text)
                    
                    # Map labels to keys
                    if current_label == 'Deposit/Withdrawal:':
                        financial_data['deposit_withdrawal'] = value
                        print(f"  Deposit/Withdrawal: {value:,.2f}")
                    elif current_label == 'Credit Facility:':
                        financial_data['credit_facility'] = value
                        print(f"  Credit Facility: {value:,.2f}")
                    elif current_label == 'Closed Trade P/L:':
                        financial_data['closed_trade_pnl'] = value
                        print(f"  Closed Trade P/L: {value:,.2f}")
                    elif current_label == 'Floating P/L:':
                        financial_data['floating_pnl'] = value
                        print(f"  Floating P/L: {value:,.2f}")
                    elif current_label == 'Margin:':
                        financial_data['margin'] = value
                        print(f"  Margin: {value:,.2f}")
                    elif current_label == 'Balance:':
                        financial_data['balance'] = value
                        print(f"  Balance: {value:,.2f}")
                    elif current_label == 'Equity:':
                        financial_data['equity'] = value
                        print(f"  Equity: {value:,.2f}")
                    elif current_label == 'Free Margin:':
                        financial_data['free_margin'] = value
                        print(f"  Free Margin: {value:,.2f}")
                    
                    # Reset current label after processing
                    current_label = None
    
    return financial_data

def extract_performance_metrics(soup):
    """
    Extract performance metrics from the HTML structure.
    Revised to handle combined amount/percentage values.
    """
    print("\n3. PERFORMANCE METRICS:")
    print("-" * 50)
    
    performance_data = {}
    labels = [
        'Gross Profit:', 'Gross Loss:', 'Total Net Profit:', 'Profit Factor:',
        'Expected Payoff:', 'Absolute Drawdown:', 'Maximal Drawdown:', 'Relative Drawdown:'
    ]
    
    # Find all rows in the document
    rows = soup.find_all('tr')
    
    for row in rows:
        # Only process rows with right alignment
        if 'right' in row.get('align', ''):
            cells = row.find_all(['td', 'th'])
            current_label = None
            
            for cell in cells:
                # Check if cell contains a bold element with a label
                bold = cell.find('b')
                if bold:
                    label_text = bold.get_text().strip()
                    if label_text in labels:
                        current_label = label_text
                
                # Check if cell is a value cell
                if 'mspt' in cell.get('class', []) and current_label:
                    value_text = cell.get_text().strip()
                    
                    # Special handling for Maximal Drawdown and Relative Drawdown
                    if current_label == 'Maximal Drawdown:':
                        if '(' in value_text and '%' in value_text:
                            # Format: "40.00 (0.02%)"
                            amount_part = value_text.split('(')[0].strip()
                            percentage_part = value_text.split('(')[1].split('%')[0].strip()
                            amount = parse_numeric_value(amount_part)
                            percentage = parse_numeric_value(percentage_part)
                            performance_data['maximal_drawdown_amount'] = amount
                            performance_data['maximal_drawdown_percentage'] = percentage
                            print(f"  Maximal Drawdown: {amount:,.2f} ({percentage:.2f}%)")
                        else:
                            amount = parse_numeric_value(value_text)
                            performance_data['maximal_drawdown_amount'] = amount
                            print(f"  Maximal Drawdown: {amount:,.2f}")
                    
                    elif current_label == 'Relative Drawdown:':
                        if '(' in value_text and '%' in value_text:
                            # Format: "0.02% (40.00)"
                            if '%' in value_text.split('(')[0]:
                                # Percentage comes first
                                percentage_part = value_text.split('%')[0].strip()
                                amount_part = value_text.split('(')[1].split(')')[0].strip()
                            else:
                                # Amount comes first
                                amount_part = value_text.split('(')[0].strip()
                                percentage_part = value_text.split('(')[1].split('%')[0].strip()
                            amount = parse_numeric_value(amount_part)
                            percentage = parse_numeric_value(percentage_part)
                            performance_data['relative_drawdown_amount'] = amount
                            performance_data['relative_drawdown_percentage'] = percentage
                            print(f"  Relative Drawdown: {percentage:.2f}% ({amount:,.2f})")
                        else:
                            percentage = parse_numeric_value(value_text)
                            performance_data['relative_drawdown_percentage'] = percentage
                            print(f"  Relative Drawdown: {percentage:.2f}%")
                    
                    else:
                        # Regular numeric values
                        value = parse_numeric_value(value_text)
                        
                        if current_label == 'Gross Profit:':
                            performance_data['gross_profit'] = value
                            print(f"  Gross Profit: {value:,.2f}")
                        elif current_label == 'Gross Loss:':
                            performance_data['gross_loss'] = value
                            print(f"  Gross Loss: {value:,.2f}")
                        elif current_label == 'Total Net Profit:':
                            performance_data['total_net_profit'] = value
                            print(f"  Total Net Profit: {value:,.2f}")
                        elif current_label == 'Profit Factor:':
                            performance_data['profit_factor'] = value
                            print(f"  Profit Factor: {value:.2f}")
                        elif current_label == 'Expected Payoff:':
                            performance_data['expected_payoff'] = value
                            print(f"  Expected Payoff: {value:,.2f}")
                        elif current_label == 'Absolute Drawdown:':
                            performance_data['absolute_drawdown'] = value
                            print(f"  Absolute Drawdown: {value:,.2f}")
                    
                    # Reset current label after processing
                    current_label = None
    
    return performance_data

def extract_trade_statistics(soup):
    """
    Extract trade statistics including win/loss ratios and trade details.
    """
    print("\n4. TRADE STATISTICS:")
    print("-" * 50)
    
    trade_stats = {}
    labels = [
        'Total Trades:', 'Short Positions (won %):', 'Long Positions (won %):',
        'Profit Trades (% of total):', 'Loss trades (% of total):'
    ]
    
    # Find all rows in the document
    rows = soup.find_all('tr')
    
    for row in rows:
        # Only process rows with right alignment
        if 'right' in row.get('align', ''):
            cells = row.find_all(['td', 'th'])
            current_label = None
            
            for cell in cells:
                # Check if cell contains a bold element with a label
                bold = cell.find('b')
                if bold:
                    label_text = bold.get_text().strip()
                    if label_text in labels:
                        current_label = label_text
                
                # Check if cell is a value cell
                if 'mspt' in cell.get('class', []) and current_label:
                    value_text = cell.get_text().strip()
                    
                    if current_label == 'Total Trades:':
                        value = int(parse_numeric_value(value_text))
                        trade_stats['total_trades'] = value
                        print(f"  Total Trades: {value}")
                    
                    elif current_label == 'Short Positions (won %):':
                        count, percentage = extract_percentage_and_count(value_text)
                        trade_stats['short_positions_count'] = count
                        trade_stats['short_positions_win_rate'] = percentage
                        print(f"  Short Positions: {count} (Win Rate: {percentage:.2f}%)")
                    
                    elif current_label == 'Long Positions (won %):':
                        count, percentage = extract_percentage_and_count(value_text)
                        trade_stats['long_positions_count'] = count
                        trade_stats['long_positions_win_rate'] = percentage
                        print(f"  Long Positions: {count} (Win Rate: {percentage:.2f}%)")
                    
                    elif current_label == 'Profit Trades (% of total):':
                        count, percentage = extract_percentage_and_count(value_text)
                        trade_stats['profit_trades_count'] = count
                        trade_stats['profit_trades_percentage'] = percentage
                        print(f"  Profit Trades: {count} ({percentage:.2f}% of total)")
                    
                    elif current_label == 'Loss trades (% of total):':
                        count, percentage = extract_percentage_and_count(value_text)
                        trade_stats['loss_trades_count'] = count
                        trade_stats['loss_trades_percentage'] = percentage
                        print(f"  Loss Trades: {count} ({percentage:.2f}% of total)")
                    
                    # Reset current label after processing
                    current_label = None
    
    return trade_stats

def extract_largest_average_trades(soup):
    """
    Extract largest and average trade information.
    Fixed to properly handle the HTML structure with bold values in mspt cells.
    """
    print("\n5. LARGEST & AVERAGE TRADES:")
    print("-" * 50)
    
    trade_data = {}
    
    # Find all rows in the document
    rows = soup.find_all('tr')
    
    for row in rows:
        # Only process rows with right alignment
        if 'right' in row.get('align', ''):
            # Get all text content from the row
            row_text = row.get_text()
            
            # Check for "Largest" trades
            if 'Largest' in row_text:
                # Find all mspt cells with bold content
                mspt_cells = row.find_all('td', class_='mspt')
                
                if len(mspt_cells) >= 2:
                    # Extract values from bold tags within mspt cells
                    profit_bold = mspt_cells[0].find('b')
                    loss_bold = mspt_cells[1].find('b')
                    
                    if profit_bold and loss_bold:
                        profit_value = parse_numeric_value(profit_bold.get_text().strip())
                        loss_value = parse_numeric_value(loss_bold.get_text().strip())
                        
                        trade_data['largest_profit_trade'] = profit_value
                        trade_data['largest_loss_trade'] = loss_value
                        
                        print(f"  Largest Profit Trade: {profit_value:,.2f}")
                        print(f"  Largest Loss Trade: {loss_value:,.2f}")
            
            # Check for "Average" trades
            elif 'Average' in row_text and 'profit trade:' in row_text and 'loss trade:' in row_text:
                # Find all mspt cells with bold content
                mspt_cells = row.find_all('td', class_='mspt')
                
                if len(mspt_cells) >= 2:
                    # Extract values from bold tags within mspt cells
                    profit_bold = mspt_cells[0].find('b')
                    loss_bold = mspt_cells[1].find('b')
                    
                    if profit_bold and loss_bold:
                        profit_value = parse_numeric_value(profit_bold.get_text().strip())
                        loss_value = parse_numeric_value(loss_bold.get_text().strip())
                        
                        trade_data['average_profit_trade'] = profit_value
                        trade_data['average_loss_trade'] = loss_value
                        
                        print(f"  Average Profit Trade: {profit_value:,.2f}")
                        print(f"  Average Loss Trade: {loss_value:,.2f}")
    
    return trade_data

def extract_consecutive_statistics(soup):
    """
    Extract consecutive wins/losses statistics.
    Fixed to properly handle the format: amount (count)
    """
    print("\n6. CONSECUTIVE WINS/LOSSES STATISTICS:")
    print("-" * 50)
    
    consecutive_stats = {}
    
    # Find all rows in the document
    rows = soup.find_all('tr')
    
    for row in rows:
        # Only process rows with right alignment
        if 'right' in row.get('align', ''):
            # Get all text content from the row
            row_text = row.get_text()
            
            # Check for Maximum consecutive wins/losses (format: "7 (1 379.89)")
            if 'Maximum' in row_text and 'consecutive wins' in row_text:
                # Find all value cells
                value_cells = row.find_all('td', class_='mspt')
                
                if len(value_cells) >= 2:
                    # Extract wins value - format is "7 (1 379.89)" -> count (amount)
                    wins_text = value_cells[0].get_text().strip()
                    count_wins, amount_wins = extract_consecutive_stats(wins_text)
                    consecutive_stats['max_consecutive_wins_count'] = count_wins
                    consecutive_stats['max_consecutive_wins_amount'] = amount_wins
                    print(f"  Maximum Consecutive Wins: {count_wins} trades (${amount_wins:,.2f})")
                    
                    # Extract losses value - format is "1 (-40.00)" -> count (amount)
                    losses_text = value_cells[1].get_text().strip()
                    count_losses, amount_losses = extract_consecutive_stats(losses_text)
                    consecutive_stats['max_consecutive_losses_count'] = count_losses
                    consecutive_stats['max_consecutive_losses_amount'] = amount_losses
                    print(f"  Maximum Consecutive Losses: {count_losses} trades (${amount_losses:,.2f})")
            
            # Check for Maximal consecutive profit/loss (format: "1 379.89 (7)")
            elif 'Maximal' in row_text and 'consecutive profit' in row_text:
                # Find all value cells
                value_cells = row.find_all('td', class_='mspt')
                
                if len(value_cells) >= 2:
                    # Extract profit value - format is "1 379.89 (7)" -> amount (count)
                    profit_text = value_cells[0].get_text().strip()
                    
                    # Parse the format: "1 379.89 (7)" -> amount=1379.89, count=7
                    match = re.search(r'([\d\s.-]+)\s*\((\d+)\)', profit_text)
                    if match:
                        amount_profit = parse_numeric_value(match.group(1))
                        count_profit = int(match.group(2))
                        consecutive_stats['maximal_consecutive_profit_amount'] = amount_profit
                        consecutive_stats['maximal_consecutive_profit_count'] = count_profit
                        print(f"  Maximal Consecutive Profit: ${amount_profit:,.2f} ({count_profit} trades)")
                    
                    # Extract loss value - format is "-40.00 (1)" -> amount (count)
                    loss_text = value_cells[1].get_text().strip()
                    
                    # Parse the format: "-40.00 (1)" -> amount=-40.00, count=1
                    match = re.search(r'([\d\s.-]+)\s*\((\d+)\)', loss_text)
                    if match:
                        amount_loss = parse_numeric_value(match.group(1))
                        count_loss = int(match.group(2))
                        consecutive_stats['maximal_consecutive_loss_amount'] = amount_loss
                        consecutive_stats['maximal_consecutive_loss_count'] = count_loss
                        print(f"  Maximal Consecutive Loss: ${amount_loss:,.2f} ({count_loss} trades)")
            
            # Check for average consecutive wins/losses
            elif 'Average' in row_text and 'consecutive wins' in row_text:
                # Find all value cells
                value_cells = row.find_all('td', class_='mspt')
                
                if len(value_cells) >= 2:
                    # Extract wins value - these are just plain numbers, no parentheses
                    wins_value = parse_numeric_value(value_cells[0].get_text().strip())
                    consecutive_stats['average_consecutive_wins'] = wins_value
                    print(f"  Average Consecutive Wins: {wins_value:.0f}")
                    
                    # Extract losses value - these are just plain numbers, no parentheses
                    losses_value = parse_numeric_value(value_cells[1].get_text().strip())
                    consecutive_stats['average_consecutive_losses'] = losses_value
                    print(f"  Average Consecutive Losses: {losses_value:.0f}")
    
    return consecutive_stats


def extract_open_trades(soup):
    print("\n7. OPEN TRADES:")
    print("-" * 50)
    
    open_trades = []
    
    # Find the open trades section by looking for the row with "Open Trades:" text
    open_trades_row = None
    for row in soup.find_all('tr'):
        td = row.find('td')
        if td and td.find('b') and 'Open Trades:' in td.get_text():
            open_trades_row = row
            break
    
    if not open_trades_row:
        print("  No open trades section found.")
        return open_trades
    
    # Find the header row (next row after the "Open Trades:" row)
    header_row = open_trades_row.find_next_sibling('tr')
    if not header_row or header_row.get('bgcolor') != "#C0C0C0":
        print("  No header row found in open trades table.")
        return open_trades
    
    # Get the headers from the header row
    headers = [td.get_text().strip() for td in header_row.find_all('td')]
    print(f"  Found {len(headers)} columns: {headers}")
    
    # Process the data rows (all subsequent rows until we hit another section or end)
    current_row = header_row.find_next_sibling('tr')
    
    while current_row:
        cells = current_row.find_all('td')
        
        # Check if this is a new section header (has colspan or bold text)
        if len(cells) == 1 and cells[0].get('colspan'):
            print(f"  Found new section: {cells[0].get_text().strip()}")
            break
        
        # Check if this row has bold text indicating a new section
        if len(cells) > 0 and cells[0].find('b'):
            print(f"  Found new section with bold text: {cells[0].get_text().strip()}")
            break
        
        # Skip rows that don't have the expected number of cells
        if len(cells) != len(headers):
            print(f"  Skipping row with {len(cells)} cells (expected {len(headers)})")
            current_row = current_row.find_next_sibling('tr')
            continue
        
        # Check if first cell contains a valid ticket number
        ticket_text = cells[0].get_text().strip()
        
        # Remove any title attribute content (like "#235713 Arvinnd")
        # and extract just the numeric part
        if 'title=' in str(cells[0]):
            # The actual ticket number is the text content, not in the title
            ticket_text = cells[0].get_text().strip()
        
        # Validate ticket number (should be numeric)
        if not ticket_text.isdigit():
            print(f"  Skipping row with non-numeric ticket: '{ticket_text}'")
            current_row = current_row.find_next_sibling('tr')
            continue
        
        # Extract trade data
        trade_data = {}
        for i, header in enumerate(headers):
            if i < len(cells):
                value = cells[i].get_text().strip()
                
                # Clean up the header name for dictionary key
                header_key = header.lower().replace(' ', '_').replace('/', '_').replace('&nbsp;', 'current_price')
                
                # Parse numeric values for appropriate columns
                if header in ['Size', 'Price', 'S / L', 'T / P', 'Commission', 'Taxes', 'Swap', 'Profit'] or header_key == 'current_price':
                    trade_data[header_key] = parse_numeric_value(value)
                else:
                    trade_data[header_key] = value
        
        # Only add if we have a valid ticket number
        if trade_data.get('ticket') and trade_data['ticket'].isdigit():
            open_trades.append(trade_data)
            
            # Print trade summary
            item = trade_data.get('item', 'N/A')
            size = trade_data.get('size', 0)
            trade_type = trade_data.get('type', 'N/A')
            profit = trade_data.get('profit', 0)
            print(f"  Trade #{trade_data['ticket']}: {trade_type.upper()} {size} {item.upper()} - "
                  f"P/L: {profit:,.2f}")
        
        current_row = current_row.find_next_sibling('tr')
    
    print(f"  Total Open Trades: {len(open_trades)}")
    return open_trades

    
    # Print detailed breakdown if trades exist
    if open_trades:
        print("\n  Detailed Open Trades:")
        for trade in open_trades:
            print(f"    Ticket: {trade.get('ticket', 'N/A')}")
            print(f"    Open Time: {trade.get('open_time', 'N/A')}")
            print(f"    Type: {trade.get('type', 'N/A').upper()}")
            print(f"    Size: {trade.get('size', 0)}")
            print(f"    Item: {trade.get('item', 'N/A').upper()}")
            print(f"    Open Price: {trade.get('price', 0)}")
            print(f"    Current Price: {trade.get('current_price', 0)}")
            print(f"    S/L: {trade.get('s___l', 0)}")
            print(f"    T/P: {trade.get('t___p', 0)}")
            print(f"    Commission: {trade.get('commission', 0)}")
            print(f"    Taxes: {trade.get('taxes', 0)}")
            print(f"    Swap: {trade.get('swap', 0)}")
            print(f"    Profit: {trade.get('profit', 0):,.2f}")
            print("    " + "-" * 40)
    
    return open_trades
def extract_closed_trades(soup):
    """
    Extract closed trades data from the HTML structure.
    """
    print("\n7. CLOSED TRADES:")
    print("-" * 50)
    
    closed_trades = []
    
    # Find the closed trades section by looking for the row with "Closed Transactions:" text
    closed_trades_row = None
    for row in soup.find_all('tr'):
        td = row.find('td')
        if td and td.find('b') and 'Closed Transactions:' in td.get_text():
            closed_trades_row = row
            break
    
    if not closed_trades_row:
        print("  No closed trades section found.")
        return closed_trades
    
    # Find the header row (next row after the "Closed Transactions:" row)
    header_row = closed_trades_row.find_next_sibling('tr')
    if not header_row or header_row.get('bgcolor') != "#C0C0C0":
        print("  No header row found in closed trades table.")
        return closed_trades
    
    # Get the headers from the header row
    headers = [td.get_text().strip() for td in header_row.find_all('td')]
    print(f"  Found {len(headers)} columns: {headers}")
    
    # Process the data rows (all subsequent rows until we hit another section or summary)
    current_row = header_row.find_next_sibling('tr')
    trade_count = 0
    
    while current_row:
        cells = current_row.find_all('td')
        
        # Stop if we hit a summary row (like "Closed P/L:" or totals)
        if len(cells) > 0:
            first_cell_text = cells[0].get_text().strip()
            
            # Check if this is a summary/total row
            if (first_cell_text == '' and len(cells) > 10) or 'Closed P/L:' in current_row.get_text():
                break
            
            # Check if this is another section header
            if cells[0].find('b') and any(section in cells[0].get_text() for section in ['Open Trades:', 'Working Orders:']):
                break
        
        # Skip rows that don't have the expected number of cells
        if len(cells) != len(headers):
            current_row = current_row.find_next_sibling('tr')
            continue
        
        # Check if first cell contains a valid ticket number (numeric) or is a balance entry
        ticket_text = cells[0].get_text().strip()
        
        # Handle balance entries (they have ticket numbers but different structure)
        if len(cells) >= 13:
            trade_type = cells[2].get_text().strip().lower()
            
            if trade_type == 'balance':
                # This is a balance entry, extract it differently
                trade_data = {
                    'ticket': ticket_text,
                    'open_time': cells[1].get_text().strip(),
                    'type': 'balance',
                    'size': 0,
                    'item': cells[3].get_text().strip(),  # Balance description
                    'price': 0,
                    's_l': 0,
                    't_p': 0,
                    'close_time': '',
                    'close_price': 0,
                    'commission': 0,
                    'taxes': 0,
                    'swap': 0,
                    'profit': parse_numeric_value(cells[-1].get_text().strip())  # Last cell is the balance amount
                }
                
                closed_trades.append(trade_data)
                print(f"  Balance Entry #{ticket_text}: {trade_data['profit']:,.2f}")
                trade_count += 1
                
            elif trade_type in ['buy', 'sell'] and ticket_text.isdigit():
                # This is a regular trade
                trade_data = {}
                for i, header in enumerate(headers):
                    if i < len(cells):
                        value = cells[i].get_text().strip()
                        
                        # Clean up the header name for dictionary key
                        header_key = header.lower().replace(' ', '_').replace('/', '_')
                        
                        # Parse numeric values for appropriate columns
                        if header in ['Size', 'Price', 'S / L', 'T / P', 'Commission', 'Taxes', 'Swap', 'Profit']:
                            trade_data[header_key] = parse_numeric_value(value)
                        else:
                            trade_data[header_key] = value
                
                # Only add if we have a valid ticket number and trade type
                if trade_data.get('ticket') and trade_data['ticket'].isdigit():
                    closed_trades.append(trade_data)
                    
                    # Print trade summary
                    item = trade_data.get('item', 'N/A')
                    size = trade_data.get('size', 0)
                    trade_type = trade_data.get('type', 'N/A')
                    profit = trade_data.get('profit', 0)
                    
                    print(f"  Trade #{trade_data['ticket']}: {trade_type.upper()} {size} {item.upper()} - "
                          f"P/L: {profit:,.2f}")
                    trade_count += 1
        
        current_row = current_row.find_next_sibling('tr')
    
    print(f"  Total Closed Trades: {trade_count}")
    
    # Calculate and print summary statistics
    if closed_trades:
        regular_trades = [t for t in closed_trades if t['type'] in ['buy', 'sell']]
        balance_entries = [t for t in closed_trades if t['type'] == 'balance']
        
        if regular_trades:
            total_profit = sum(t['profit'] for t in regular_trades)
            winning_trades = [t for t in regular_trades if t['profit'] > 0]
            losing_trades = [t for t in regular_trades if t['profit'] < 0]
            
            print(f"\n  Trading Summary:")
            print(f"    Regular Trades: {len(regular_trades)}")
            print(f"    Winning Trades: {len(winning_trades)}")
            print(f"    Losing Trades: {len(losing_trades)}")
            print(f"    Total Trading P/L: {total_profit:,.2f}")
            
            if winning_trades:
                avg_win = sum(t['profit'] for t in winning_trades) / len(winning_trades)
                print(f"    Average Win: {avg_win:,.2f}")
            
            if losing_trades:
                avg_loss = sum(t['profit'] for t in losing_trades) / len(losing_trades)
                print(f"    Average Loss: {avg_loss:,.2f}")
        
        if balance_entries:
            total_deposits = sum(t['profit'] for t in balance_entries)
            print(f"\n  Balance Entries: {len(balance_entries)}")
            print(f"    Total Deposits/Withdrawals: {total_deposits:,.2f}")
    
    return closed_trades

def calculate_additional_metrics(all_data):
    """
    Calculate additional metrics based on extracted data.
    """
    print("\n8. CALCULATED METRICS:")
    print("-" * 50)
    
    calculated = {}
    
    # Extract relevant data
    financial = all_data.get('financial_summary', {})
    performance = all_data.get('performance_metrics', {})
    trade_stats = all_data.get('trade_statistics', {})
    trades = all_data.get('largest_average_trades', {})
    
    # Calculate Return on Investment (ROI)
    initial_deposit = financial.get('deposit_withdrawal', 0)
    closed_pnl = financial.get('closed_trade_pnl', 0)
    if initial_deposit > 0:
        roi = (closed_pnl / initial_deposit) * 100
        calculated['roi_percentage'] = roi
        print(f"  Return on Investment (ROI): {roi:.2f}%")
    
    # Calculate Risk-Reward Ratio
    avg_profit = trades.get('average_profit_trade', 0)
    avg_loss = abs(trades.get('average_loss_trade', 0))
    if avg_loss > 0:
        risk_reward_ratio = avg_profit / avg_loss
        calculated['risk_reward_ratio'] = risk_reward_ratio
        print(f"  Risk-Reward Ratio: {risk_reward_ratio:.2f}:1")
    
    # Calculate Win Rate
    profit_trades = trade_stats.get('profit_trades_count', 0)
    total_trades = trade_stats.get('total_trades', 0)
    if total_trades > 0:
        win_rate = (profit_trades / total_trades) * 100
        calculated['win_rate'] = win_rate
        print(f"  Win Rate: {win_rate:.2f}%")
    
    # Calculate Profit Factor (if not already available)
    if 'profit_factor' not in performance:
        gross_profit = performance.get('gross_profit', 0)
        gross_loss = abs(performance.get('gross_loss', 0))
        if gross_loss > 0:
            profit_factor = gross_profit / gross_loss
            calculated['calculated_profit_factor'] = profit_factor
            print(f"  Calculated Profit Factor: {profit_factor:.2f}")
    
    # Calculate Account Growth
    balance = financial.get('balance', 0)
    if initial_deposit > 0:
        account_growth = ((balance - initial_deposit) / initial_deposit) * 100
        calculated['account_growth_percentage'] = account_growth
        print(f"  Account Growth: {account_growth:.2f}%")
    
    # Calculate Drawdown as % of balance
    max_drawdown = performance.get('maximal_drawdown_amount', 0)
    if balance > 0:
        drawdown_percentage_of_balance = (max_drawdown / balance) * 100
        calculated['drawdown_percentage_of_balance'] = drawdown_percentage_of_balance
        print(f"  Drawdown as % of Current Balance: {drawdown_percentage_of_balance:.2f}%")
    
    return calculated

def process_mt4_html_file(file_path):
    """
    Main function to process MT4 HTML file and extract all data.
    """
    try:
        # Read the HTML file
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            html_content = file.read()
        
        print(f"Successfully loaded HTML file: {file_path}")
        print(f"File size: {len(html_content)} characters")
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        all_data = {}
        
        all_data['account_info'] = extract_account_info(soup)
        all_data['financial_summary'] = extract_financial_summary(soup)
        all_data['performance_metrics'] = extract_performance_metrics(soup)
        all_data['trade_statistics'] = extract_trade_statistics(soup)
        all_data['largest_average_trades'] = extract_largest_average_trades(soup)
        all_data['consecutive_statistics'] = extract_consecutive_statistics(soup)
        all_data['closed_trades'] = extract_closed_trades(soup)
        all_data['open_trades'] = extract_open_trades(soup)
        all_data['calculated_metrics'] = calculate_additional_metrics(all_data)
        
        print("\n" + "="*80)
        print("COMPREHENSIVE DATA SUMMARY")
        print("="*80)
        
        total_open_trades = len(all_data.get('open_trades', []))
        total_closed_trades = len(all_data.get('closed_trades', []))

        for category, data in all_data.items():
            if category == 'open_trades':
                print(f"\n{category.upper().replace('_', ' ')}: {total_open_trades} trades")
                continue
            elif isinstance(data, dict):
                print(f"\n{category.upper().replace('_', ' ')}:")
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        if 'percentage' in key or 'rate' in key:
                            print(f"  {key.replace('_', ' ').title()}: {value:.2f}%")
                        else:
                            print(f"  {key.replace('_', ' ').title()}: {value:,.2f}")
                    else:
                        print(f"  {key.replace('_', ' ').title()}: {value}")
        print(f"TOTAL CLOSED TRADES: {total_closed_trades}")
        print(f"\nOPEN TRADES: {total_open_trades}")
        print(f"PROCESSING COMPLETED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return all_data
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        return {}

def main():
    file_path = r"C:\Users\HP\Desktop\2.htm"
    
    print(f"Processing MT4 HTML file: {file_path}")
    
    if not Path(file_path).exists():
        print(f"Error: File not found - {file_path}")
        print("Please make sure the file exists at the specified location.")
        print("Current working directory:", Path.cwd())
        return
    
    if not file_path.lower().endswith(('.htm', '.html')):
        print(f"Error: File should be an HTML file (.htm or .html)")
        return
    
    print("="*80)
    print(f"File found! Processing...")
    print("="*80)
    
    all_extracted_data = process_mt4_html_file(file_path)
    
    if all_extracted_data:
        print(f"\nData extraction completed successfully!")
    
    else:
        print("Failed to extract data from the HTML file.")

if __name__ == "__main__":
    main()