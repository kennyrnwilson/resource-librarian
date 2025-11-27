# Manual Testing Guide for Resource Librarian

This guide provides step-by-step commands to manually test the Resource Librarian CLI.

## Prerequisites

1. **Set up YouTube API Key** (required for video fetching):
   ```bash
   # Get a YouTube Data API v3 key from: https://console.cloud.google.com/
   export YOUTUBE_API_KEY="your-api-key-here"
   ```

2. **Activate virtual environment**:
   ```bash
   cd /home/kenne/code/resource-librarian
   source venv/bin/activate
   ```

3. **Verify installation**:
   ```bash
   rl --version
   rl --help
   ```

## Test 1: Initialize a Library

```bash
# Create a test library in /tmp
rl init /tmp/test-library

# Expected output:
# - Success message
# - Shows library structure created
# - Shows next steps

# Verify structure was created
ls -la /tmp/test-library/
# Should show: books/, videos/, catalog.yaml, _index/
```

## Test 2: Library Initialization Edge Cases

```bash
# Try to initialize in existing directory (should fail)
rl init /tmp/test-library

# Expected output:
# - Error message about directory already existing

# Initialize with nested path
rl init /tmp/test-library-2/nested/path

# Verify it was created
ls -la /tmp/test-library-2/nested/path/
```

## Test 3: Video Fetch - Single Video

```bash
# Fetch a popular video (Rick Astley - Never Gonna Give You Up)
rl video fetch "dQw4w9WgXcQ" \
  --library /tmp/test-library \
  --categories "Music,Entertainment" \
  --tags "classic,test"

# Expected output:
# - "Fetching YouTube video: dQw4w9WgXcQ"
# - "→ Fetching video metadata..."
# - "→ Fetching transcript..."
# - Success message with video title and channel
# - Shows location in library

# Verify the video was added
ls -la /tmp/test-library/videos/
# Should show a channel folder

# Check video folder structure
find /tmp/test-library/videos -type f | head -20
# Should show:
# - manifest.yaml
# - source/transcript.txt
# - source/video.url
```

## Test 4: Video Fetch - Different URL Formats

```bash
# Standard YouTube URL
rl video fetch "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --library /tmp/test-library

# Short URL
rl video fetch "https://youtu.be/dQw4w9WgXcQ" \
  --library /tmp/test-library

# URL with parameters
rl video fetch "https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share" \
  --library /tmp/test-library

# Expected: All should fail with "Video already exists" error
```

## Test 5: Video Fetch - Error Cases

```bash
# Invalid video ID
rl video fetch "invalid123" \
  --library /tmp/test-library

# Expected: "Invalid YouTube video URL or ID" error

# Nonexistent library
rl video fetch "dQw4w9WgXcQ" \
  --library /tmp/nonexistent

# Expected: "Not a valid Resource Library" error

# Without API key (unset it temporarily)
unset YOUTUBE_API_KEY
rl video fetch "dQw4w9WgXcQ" \
  --library /tmp/test-library

# Expected: "YouTube API key required" error

# Restore API key
export YOUTUBE_API_KEY="your-api-key-here"
```

## Test 6: Video List

```bash
# List all videos in library
rl video list --library /tmp/test-library

# Expected output:
# - Shows video count
# - Table with: Title, Channel, Video ID, Categories, Tags, Published

# Filter by channel
rl video list --library /tmp/test-library --channel "Rick"

# Filter by category
rl video list --library /tmp/test-library --category "Music"

# Filter by tag
rl video list --library /tmp/test-library --tag "classic"

# Filter by title
rl video list --library /tmp/test-library --title "Never"

# Multiple filters
rl video list --library /tmp/test-library \
  --category "Music" \
  --tag "classic"
```

## Test 7: Video Get

```bash
# Get transcript for a video
rl video get "Never Gonna Give You Up" \
  --library /tmp/test-library

# Expected output:
# - Shows video metadata (title, channel, published date)
# - Shows full transcript text

# Save transcript to file
rl video get "Never Gonna Give You Up" \
  --library /tmp/test-library \
  --output /tmp/transcript.txt

# Verify file was created
cat /tmp/transcript.txt

# Case-insensitive search
rl video get "never gonna" \
  --library /tmp/test-library

# Video not found
rl video get "Nonexistent Video" \
  --library /tmp/test-library

# Expected: "Video not found" error
```

## Test 8: Book Add (if you have sample books)

```bash
# Create a sample markdown book
cat > /tmp/sample-book.md <<'EOF'
# Sample Book Title

**Author:** John Doe

## Chapter 1: Introduction

This is the introduction to the sample book.

## Chapter 2: Main Content

This is the main content of the book.
EOF

# Add the book to library
rl book add /tmp/sample-book.md \
  --library /tmp/test-library \
  --author "John Doe" \
  --categories "Tutorial,Programming" \
  --tags "sample,test"

# Expected output:
# - Success message
# - Shows book title and author
# - Shows location in library
```

## Test 9: Book List

```bash
# List all books
rl book list --library /tmp/test-library

# Filter by author
rl book list --library /tmp/test-library --author "John"

# Filter by category
rl book list --library /tmp/test-library --category "Tutorial"

# Filter by tag
rl book list --library /tmp/test-library --tag "sample"
```

## Test 10: Book Get

```bash
# Get book content
rl book get "Sample Book" \
  --library /tmp/test-library

# Save to file
rl book get "Sample Book" \
  --library /tmp/test-library \
  --output /tmp/book-content.md

# Verify file
cat /tmp/book-content.md
```

## Test 11: Catalog Verification

```bash
# Check catalog was updated
cat /tmp/test-library/catalog.yaml

# Should show:
# - version: "1.0"
# - books: [list of books]
# - videos: [list of videos]
# - last_updated: [timestamp]

# Verify video entries have correct structure
grep -A 10 "videos:" /tmp/test-library/catalog.yaml
```

## Test 12: Folder Structure Verification

```bash
# Check complete library structure
tree /tmp/test-library -L 4

# Expected structure:
# /tmp/test-library/
# ├── books/
# │   ├── _index/
# │   └── [author-folders]/
# │       └── [book-folders]/
# │           ├── manifest.yaml
# │           └── formats/
# ├── videos/
# │   ├── _index/
# │   └── [channel-folders]/
# │       └── [video-folders]/
# │           ├── manifest.yaml
# │           ├── source/
# │           │   ├── transcript.txt
# │           │   └── video.url
# │           ├── summaries/
# │           └── pointers/
# ├── catalog.yaml
# └── _index/
```

## Test 13: Multiple Videos from Same Channel

```bash
# Fetch another video from Rick Astley's channel
rl video fetch "https://www.youtube.com/watch?v=yPYZpwSpKmA" \
  --library /tmp/test-library \
  --categories "Music" \
  --tags "80s"

# Expected:
# - Video added to same channel folder
# - Catalog updated with new video

# Verify both videos are in same channel folder
ls -la /tmp/test-library/videos/rick-astley*/
```

## Test 14: Edge Cases and Special Characters

```bash
# Video with special characters in title
rl video fetch "kJQP7kiw5Fk" \
  --library /tmp/test-library

# Expected:
# - Title should be slugified (special chars removed)
# - Folder name should be safe for filesystem

# List to verify
rl video list --library /tmp/test-library
```

## Test 15: Help and Documentation

```bash
# Main help
rl --help

# Video subcommand help
rl video --help

# Specific command help
rl video fetch --help
rl video list --help
rl video get --help

# Book subcommand help
rl book --help
rl book add --help
rl book list --help
rl book get --help
```

## Test 16: Performance Test (Optional)

```bash
# Time a video fetch operation
time rl video fetch "dQw4w9WgXcQ" \
  --library /tmp/test-library-perf

# Expected:
# - Should complete in reasonable time (depends on API response)
# - Transcript fetching is usually fast (no API key needed)
```

## Cleanup

```bash
# Remove test libraries
rm -rf /tmp/test-library
rm -rf /tmp/test-library-2
rm -rf /tmp/test-library-perf
rm -f /tmp/sample-book.md
rm -f /tmp/transcript.txt
rm -f /tmp/book-content.md

# Deactivate virtual environment
deactivate
```

## Common Issues and Solutions

### Issue: "YouTube API key required"
**Solution:** Set the environment variable:
```bash
export YOUTUBE_API_KEY="your-key-here"
```

### Issue: "Video already exists"
**Solution:** This is expected when trying to add the same video twice. Each video can only be added once per library.

### Issue: "No transcript available"
**Solution:** Not all videos have transcripts. Try a different video that has captions/subtitles enabled.

### Issue: "ModuleNotFoundError"
**Solution:** Make sure you're in the virtual environment and dependencies are installed:
```bash
source venv/bin/activate
pip install -e ".[dev]"
```

### Issue: API Quota Exceeded
**Solution:** YouTube Data API has daily quotas. If exceeded, wait 24 hours or use a different API key.

## Sample YouTube Videos for Testing

Here are some good videos for testing (with transcripts available):

1. **Rick Astley - Never Gonna Give You Up**
   - ID: `dQw4w9WgXcQ`
   - Good for: Basic testing, classic video

2. **Luis Fonsi - Despacito**
   - ID: `kJQP7kiw5Fk`
   - Good for: Special characters, non-English content

3. **Ed Sheeran - Shape of You**
   - ID: `JGwWNGJdvx8`
   - Good for: Recent popular music video

4. **TED Talks** (various)
   - Good for: Educational content with clear transcripts

## Success Criteria

All tests should:
- ✅ Complete without errors (except expected error cases)
- ✅ Create proper folder structures
- ✅ Generate valid manifest.yaml files
- ✅ Save transcripts correctly
- ✅ Update catalog.yaml
- ✅ Display formatted output with proper colors/panels
- ✅ Handle edge cases gracefully with clear error messages
