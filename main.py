import os
import json
import sys
from openai import OpenAI
import concurrent.futures
from dotenv import load_dotenv

def process_task(client, model_id, task):
    task_id = task.get("task_id")
    prompt = task.get("prompt")
    
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        answer = response.choices[0].message.content
    except Exception as e:
        print(f"Error on task {task_id}: {e}")
        answer = ""
        
    return {
        "task_id": task_id,
        "answer": answer
    }

def main():
    load_dotenv()  # Loads variables from .env if it exists
    
    api_key = os.environ.get("FIREWORKS_API_KEY")
    base_url = os.environ.get("FIREWORKS_BASE_URL")
    allowed_models = os.environ.get("ALLOWED_MODELS", "")
    
    if not api_key or not base_url or not allowed_models:
        print("Missing required environment variables.", file=sys.stderr)
        sys.exit(1)
        
    models = allowed_models.split(",")
    model_id = models[0]
    
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        max_retries=2
    )
    
    # Use local directories if the hackathon's absolute paths don't exist
    input_file = "/input/tasks.json" if os.path.exists("/input") else "./input/tasks.json"
    output_file = "/output/results.json" if os.path.exists("/input") else "./output/results.json"
    
    try:
        with open(input_file, "r") as f:
            tasks = json.load(f)
    except Exception as e:
        print(f"Failed to read input tasks: {e}", file=sys.stderr)
        sys.exit(1)
        
    results = []
    
    # Process tasks concurrently to ensure we finish within the 10-minute limit.
    # We use a reasonable max_workers to avoid hitting rate limits too aggressively.
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_task, client, model_id, task) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
        
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        print(f"Failed to write results: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("Successfully processed all tasks.")
    sys.exit(0)

if __name__ == "__main__":
    main()
