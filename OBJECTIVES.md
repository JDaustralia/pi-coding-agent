# Project Objectives: JSONL to CSV Conversion

## Source Files
- **Input:** `/home/jd/pi_projects/pca_history2csv/r800_history4hitl/src/example-input.jsonl`
- **Reference Output (DO NOT OVERWRITE):** `/home/jd/pi_projects/pca_history2csv/r800_history4hitl/src/example-output.csv`

## Requirements
- **Output File:** `convert.py` must generate a **NEW** file named `test-output.csv` with rows in chronological order.
- **Column Extraction:**
    1. `modelId`: Extracted from JSON event lines.
    2. `Prompt50`: First ~50 words from the user message text.
    3. `Response50`: First ~50 words from assistant message text (MUST ignore `{"type":"thinking"}` blocks).
    4. `totalTokens`: Extracted from JSON event lines.
    5. `totalCost`: Extracted from the `cost: {total: ...}` field.

## Validation Criteria
- Use `bash` to compare `current-test-output.csv` against the reference `example-output.csv`.
- **CRITICAL:** If `convert.py` modifies or overwrites the reference `example-output.csv`, the task is a FAILURE.
