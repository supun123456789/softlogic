from flask import Flask, request, jsonify
import requests
from openpyxl import load_workbook
from io import BytesIO
import base64

app = Flask(__name__)

# CONFIGURE
# ========== CONFIGURE HERE ==========
GITHUB_TOKEN = "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"
REPO = "supun123456789/softlogic"
BRANCH = "main"
FILE_PATH = "jobs.xlsx"
# ===================================
GITHUB_API_URL = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

# GET the Excel file from GitHub
def get_excel_file():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(GITHUB_API_URL + f"?ref={BRANCH}", headers=headers)
    r.raise_for_status()
    data = r.json()
    sha = data['sha']
    content = base64.b64decode(data['content'])
    return BytesIO(content), sha

# UPDATE or ADD job
def update_excel(job_data, file_stream):
    wb = load_workbook(file_stream)
    ws = wb.active
    job_numbers = [ws.cell(row=i, column=1).value for i in range(2, ws.max_row+1)]
    if job_data['job_number'] in job_numbers:
        row_idx = job_numbers.index(job_data['job_number']) + 2
    else:
        row_idx = ws.max_row + 1
    ws.cell(row=row_idx, column=1, value=job_data['job_number'])
    ws.cell(row=row_idx, column=2, value=job_data['customer_name'])
    ws.cell(row=row_idx, column=3, value=job_data['job_state'])
    ws.cell(row=row_idx, column=4, value=job_data['job_in_time'])
    ws.cell(row=row_idx, column=5, value=job_data['job_out_time'])
    ws.cell(row=row_idx, column=6, value=job_data['remark'])
    out_stream = BytesIO()
    wb.save(out_stream)
    out_stream.seek(0)
    return out_stream

# PUSH updated Excel back to GitHub
def push_to_github(file_stream, sha):
    content = base64.b64encode(file_stream.read()).decode('utf-8')
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {
        "message": "Update jobs.xlsx",
        "content": content,
        "branch": BRANCH,
        "sha": sha
    }
    r = requests.put(GITHUB_API_URL, headers=headers, json=data)
    r.raise_for_status()

@app.route('/submit_job', methods=['POST'])
def submit_job():
    try:
        job_data = request.json
        file_stream, sha = get_excel_file()
        updated_file = update_excel(job_data, file_stream)
        push_to_github(updated_file, sha)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
