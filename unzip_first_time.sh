find . -name "*.zip" | while read filename; do unzip "$filename" -d "output"; rm -f "$filename"; find "output" -name "*.zip"| while read insidezip ; do mv "$insidezip" .; done; rm -rf "output"; done;
