# OmniSolve Agent: Efficient Multi-Domain AI

OmniSolve is a high-performance, containerized AI agent built for the AMD Developer Hackathon. It leverages Fireworks AI to efficiently tackle natural language tasks across 8 diverse domains, including math, coding, and logical reasoning, optimizing for token efficiency and accuracy.

## Requirements

- Python 3.11+
- Docker (for evaluating and submitting the agent)
- A Fireworks AI API Key

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install local dependencies (if running without Docker):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   For local testing, create a `.env` file in the root directory and add your credentials:
   ```env
   FIREWORKS_API_KEY="your_actual_api_key_here"
   FIREWORKS_BASE_URL="https://api.fireworks.ai/inference/v1"
   ALLOWED_MODELS="accounts/fireworks/models/llama-v3-70b-instruct"
   ```
   *Note: Ensure the model you specify in `ALLOWED_MODELS` is accessible by your API key.*

## Running Locally (Without Docker)

You can run the script locally to quickly test iterations. It is designed to look for `./input/tasks.json` locally if the absolute Docker path (`/input/tasks.json`) isn't available, and will output the results to `./output/results.json`.

```bash
# Create the necessary folders and a dummy tasks.json
mkdir -p input output
echo '[{"task_id": "t1", "prompt": "Summarize in one sentence: The quick brown fox jumps over the lazy dog."}]' > input/tasks.json

# Run the agent
python main.py
```

## Running with Docker (Evaluation Simulation)

To accurately simulate how the hackathon evaluation harness will execute your agent, build and run the Docker container.

1. **Build the image (Requires linux/amd64 platform):**
   ```bash
   docker buildx build --platform linux/amd64 -t amd-agent:latest .
   ```

2. **Run the container:**
   The hackathon harness expects to mount an `input` and `output` directory to the root of the container and inject environment variables directly. You can test this locally by running:
   ```bash
   docker run -v $(pwd)/input:/input -v $(pwd)/output:/output \
     -e FIREWORKS_API_KEY="your_actual_api_key_here" \
     -e FIREWORKS_BASE_URL="https://api.fireworks.ai/inference/v1" \
     -e ALLOWED_MODELS="accounts/fireworks/models/llama-v3-70b-instruct" \
     amd-agent:latest
   ```

## Technical Decisions
- **Token Efficiency First**: The agent intentionally avoids using a system prompt. It directly forwards the user's prompt to the LLM to minimize token consumption and maximize the token efficiency ranking.
- **Accuracy Optimization**: The LLM `temperature` parameter is strictly set to `0.0`. This ensures deterministic outputs which is critically important for mathematical reasoning, logical deduction, and code debugging tasks.
- **Lightweight Architecture**: The Docker image uses `python:3.11-slim`, significantly reducing the image size to remain well beneath the 10GB restriction, allowing for extremely fast pull and start times.
- **Concurrent Processing**: To ensure the agent finishes within the strict 10-minute timeout for a large number of tasks, it utilizes `concurrent.futures.ThreadPoolExecutor` to process up to 10 tasks in parallel.
