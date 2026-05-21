import re
import csv
import sys
import os

def parse_md_to_csv(md_file_path, csv_file_path):
    """
    Parses a Markdown test case file and exports it to a CSV format.
    """
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {md_file_path}")
        return

    # Extract Main and Sub modules from H1 header dynamically
    # Expected format: # [功能模組] - [功能點] 測試案例
    main_module = "未定義"
    sub_module = "未定義"
    h1_match = re.search(r'^#\s+(.*?)\s*-\s*(.*?)\s*測試案例', content, re.MULTILINE)
    if h1_match:
        main_module = h1_match.group(1).strip()
        sub_module = h1_match.group(2).strip()
    else:
        # Fallback parsing if the format is slightly different
        h1_fallback = re.search(r'^#\s+(.*)', content, re.MULTILINE)
        if h1_fallback:
            title = h1_fallback.group(1).strip()
            parts = title.split('-')
            if len(parts) >= 2:
                main_module = parts[0].strip()
                sub_module = parts[1].replace('測試案例', '').strip()
            else:
                main_module = title.replace('測試案例', '').strip()

    # Regular expression to match each test case block
    tc_pattern = re.compile(
        r'## (TC-\d+): \[(.*?)\] (.*?)\n'
        r'- \*\*類型:\*\* (.*?)\n'
        r'- \*\*優先順序:\*\* (.*?)\n'
        r'- \*\*前置條件:\*\*\n(.*?)\n'
        r'- \*\*步驟\*\*\n(.*?)\n'
        r'- \*\*預期結果:\*\*\n(.*?)'
        r'(?=\n## TC-|\Z)',
        re.DOTALL
    )

    test_cases = []
    for match in tc_pattern.finditer(content):
        tc_id = match.group(1).strip()
        tc_tag = match.group(2).strip()
        tc_name = match.group(3).strip()
        tc_type = match.group(4).strip()
        tc_priority = match.group(5).strip()
        
        # Clean up lists
        preconditions = [line.strip().replace('- ', '', 1) for line in match.group(6).strip().split('\n') if line.strip()]
        steps = [line.strip().replace('步驟: ', '', 1) for line in match.group(7).strip().split('\n') if line.strip()]
        # Remove the leading number and dot from steps (e.g., "1. ")
        steps = [re.sub(r'^\d+\.\s*', '', step) for step in steps]
        
        results = [line.strip().replace('結果: ', '', 1) for line in match.group(8).strip().split('\n') if line.strip()]
        # Remove the leading number and dot from results
        results = [re.sub(r'^\d+\.\s*', '', result) for result in results]

        # Combine tag and name for the summary
        summary = f"[{tc_tag}] {tc_name}"

        # Format preconditions as a single string with newlines
        preconditions_str = "\n".join(preconditions)

        # Determine the maximum number of rows needed for this test case
        max_rows = max(len(steps), len(results), 1)

        for i in range(max_rows):
            step = steps[i] if i < len(steps) else ""
            result = results[i] if i < len(results) else ""
            
            # Only the first row of a test case gets the general info
            if i == 0:
                row = [
                    tc_type,
                    main_module,
                    sub_module,
                    summary,
                    preconditions_str,
                    step,
                    result,
                    "" # Remarks
                ]
            else:
                row = [
                    "", "", "", "", "", step, result, ""
                ]
            test_cases.append(row)

    # Write to CSV
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
    with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['類型', '主要', '次要', '摘要', '前置條件/先決條件', '步驟', '預期結果/檢查點', '備註'])
        writer.writerows(test_cases)
    
    print(f"Successfully exported {len(test_cases)} rows to {csv_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python md_to_csv.py <input_md_file> <output_csv_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    parse_md_to_csv(input_file, output_file)
