#!/bin/bash
cd /Users/am/clawd/SiriBridge/worker
echo "$1" | wrangler secret put "$2"
