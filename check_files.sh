#!/bin/bash

files=(
    "pages/_app.tsx"
    "pages/index.tsx"
    "src/components/sidebar.tsx"
    "src/components/editor.tsx"
    "src/components/code-editor.tsx"
    "src/components/theme-provider.tsx"
    "src/lib/store.ts"
    "src/lib/utils.ts"
    "src/styles/globals.css"
    "next.config.js"
    "tsconfig.json"
    "tailwind.config.js"
)

echo "Checking project files..."
echo "------------------------"

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is missing"
    fi
done

echo "------------------------"
