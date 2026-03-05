#!/usr/bin/env python
import sys
import json
import datetime
from shorthand_lib import ShorthandCompressor

def format_ts(epoch):
    # Handles both 10-digit and 13-digit epochs
    ts = epoch / 1000 if epoch > 10000000000 else epoch
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

def main():
    compressor = ShorthandCompressor()
    
    try:
        # Load the full export
        raw_data = json.load(sys.stdin)
        
        for chat_obj in raw_data:
            messages = chat_obj.get("chat", {}).get("messages", [])
            
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "").strip()
                timestamp = msg.get("timestamp")
                
                if not content:
                    continue
                
                # Create a temporally anchored string for the LLM
                time_str = format_ts(timestamp) if timestamp else "Unknown Time"
                input_text = f"[{time_str}] {role}: {content}"
                
                # Perform semantic compression
                compressed_content = compressor._query_ollama(input_text)
                
                # Output as JSONL
                result = {
                    "ts": timestamp,
                    "role": role,
                    "compressed": compressed_content
                }
                print(json.dumps(result))
                sys.stdout.flush()

    except json.JSONDecodeError:
        print("Error: Input is not valid JSON.", file=sys.stderr)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
