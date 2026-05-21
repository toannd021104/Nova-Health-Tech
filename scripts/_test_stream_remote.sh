#!/bin/bash
# Test streaming on EC2 directly
printf '{"message":"COVID oxygen","emergency":true}' > /tmp/req.json
echo "Request:"
cat /tmp/req.json
echo
echo "---"
echo "Response (first 30 lines):"
curl -sS -N -X POST http://127.0.0.1:80/api/chat/stream \
  -H "Content-Type: application/json" \
  -d @/tmp/req.json 2>&1 | head -30
