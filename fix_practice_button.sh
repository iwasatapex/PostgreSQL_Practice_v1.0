#!/bin/bash
# Fix the practice button on the portal

sed -i '/Start Practice/,/<\/button>/ {
    s/onclick="[^"]*"//g
    s/<button/<a href="\/practice" target="_blank" style="text-decoration:none;"><button/g
    s/<\/button>/<\/button><\/a>/g
}' templates/portal_complete.html

echo "✅ Practice button fixed"
