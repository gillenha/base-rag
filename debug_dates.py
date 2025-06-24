#!/usr/bin/env python3
"""
Debug script to check date parsing logic.
"""

import os
import glob
from datetime import datetime, timedelta

def debug_date_parsing():
    """Debug the date parsing logic."""
    
    chat_logs_dir = "./chat_logs"
    cutoff_date = datetime.now() - timedelta(days=7)
    
    print(f"Current date: {datetime.now()}")
    print(f"Cutoff date (7 days ago): {cutoff_date}")
    print()
    
    for file_path in glob.glob(os.path.join(chat_logs_dir, "*.md")):
        filename = os.path.basename(file_path)
        print(f"File: {filename}")
        
        try:
            # Remove the .md extension using os.path.splitext
            filename_without_ext = os.path.splitext(filename)[0]
            date_str = filename_without_ext.split('_')[0] + '_' + filename_without_ext.split('_')[1]
            file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
            print(f"  Parsed date: {file_date}")
            print(f"  Is within 7 days: {file_date >= cutoff_date}")
        except (ValueError, IndexError) as e:
            print(f"  Error parsing date: {e}")
        
        print()

if __name__ == "__main__":
    debug_date_parsing() 