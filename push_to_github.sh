#!/bin/bash
set -e

echo "=== Updating main project ==="
git add .
git commit -m "Update project and tests submodule reference" || echo "No changes in main project"
git push origin main

echo "=== All push operations completed successfully ==="
