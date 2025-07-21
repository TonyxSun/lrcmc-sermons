#!/bin/bash

# Step 1: Undo the current amended commit (soft reset to keep changes staged)
# git reset --soft HEAD^

# Step 2: Initialize Git LFS (if not already set up)
# git lfs install
# git lfs track "*.mp3" "*.pptx"
# git add .gitattributes
# git commit -m "Add Git LFS tracking for .mp3 and .pptx files"

# Step 3: Stage and commit files by year (2011 to 2020)
for year in {2011..2020}; do
    # Check if the directory for the year exists
    if [ -d "sermons/$year" ]; then
        echo "Committing files for $year..."
        # Stage .mp3 and .pptx files for the specific year
        git add "sermons/$year/*" 2>/dev/null
        # Commit if there are staged files
        if git status --porcelain | grep .; then
            git commit -m "Add sermons (.mp3 and .pptx) for $year"
            git push origin master
        else
            echo "No .mp3 or .pptx files found for $year"
        fi
    else
        echo "Directory sermons/$year does not exist"
    fi
done

# Step 4: Commit any remaining files (e.g., scripts, index.html, .DS_Store)
git add .
if git status --porcelain | grep .; then
    git commit -m "Add remaining files (scripts, index.html, etc.)"
else
    echo "No remaining files to commit"
fi

# Step 5: Push all commits to the remote repository
git push origin master
