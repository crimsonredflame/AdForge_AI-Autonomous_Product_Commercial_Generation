import httpx
import json

async def trigger_colab_gpu(positive_prompt: str, negative_prompt: str, pinggy_url: str):
    # 1. Read the blueprint you downloaded from Colab
    with open("app/workflow_api.json", "r") as f:
        workflow = json.load(f)
        
    # 2. Inject your dynamic prompts into the exact correct Node IDs. 
    try:
        # Node 3 is your Positive Prompt
        workflow["3"]["inputs"]["text"] = positive_prompt
        
        # Node 4 is your Negative Prompt
        workflow["4"]["inputs"]["text"] = negative_prompt
    except KeyError as e:
        print(f"Warning: Node ID {e} not found, check your workflow JSON structure.")

    # 3. Fire it over the tunnel to your Colab instance
    print(f"Sending to GPU at {pinggy_url}...")
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{pinggy_url}/prompt", json={"prompt": workflow})
        
        if response.status_code == 200:
            return response.json()  # Returns the Job ID
        else:
            return {"error": response.text}