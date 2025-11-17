# CLI Commands Analysis - Source Project

**Source:** `/home/kenne/resource-library-tools/src/knowledgehub/cli/commands.py`
**Date:** 2025-11-17
**Purpose:** Identify which commands to port vs exclude for Resource Librarian

---

## Command Structure Overview

The source CLI uses **Typer** with the following structure:
- Source main app: `kh` (KnowledgeHub CLI)
- **Our main app: `rl` (Resource Librarian)**
- Sub-apps (command groups): `add`, `fetch`, `chunk`, `catalog`, `video-state`
- Standalone commands: `init`, `status`, `build`, `index`, `search`, `ask`, `convert`, etc.

**Note:** All command examples below use `rl` instead of the source project's `kh`.

---

## Commands to INCLUDE ✅

### 1. **init** - Initialize Library
**Command:** `rl init <path>`

**Purpose:** Initialize a new Resource Library at specified path

**Arguments:**
- `path` (required): Path to initialize the knowledge hub

**What it does:**
- Creates directory structure (books/, videos/, .knowledgehub/)
- **NOTE:** Excludes processed/ directory (vectorization-related)

**Port?** ✅ YES - Essential for library setup
**Changes needed:** Remove processed/ directory creation

---

### 2. **status** - Show Hub Status
**Command:** `rl status [path]`

**Purpose:** Show status of the KnowledgeHub

**Arguments:**
- `path` (optional, default "."): Path to knowledge hub

**What it does:**
- Verifies hub exists
- Counts books and videos
- Displays table with counts

**Port?** ✅ YES - Useful for library overview
**Changes needed:** None

---

### 3. **add book** - Add Single Book
**Command:** `rl add book <file_paths> [options]`

**Purpose:** Add a book to the knowledge hub

**Arguments:**
- `file_paths` (required, list): Path(s) to book file(s) - PDF, EPUB, or Markdown

**Options:**
- `--hub, -h`: Path to knowledge hub (default ".")
- `--title, -t`: Book title (optional, auto-detected)
- `--author, -a`: Book author (optional, auto-detected)
- `--categories, -c`: Comma-separated categories
- `--tags`: Comma-separated tags
- `--isbn`: ISBN number
- `--prefer`: Preferred format for text extraction (epub/pdf/markdown, default "epub")

**What it does:**
- Accepts multiple formats of same book
- Auto-detects metadata if not provided
- Creates manifest and stores in books/ directory

**Port?** ✅ YES - Core book ingestion
**Changes needed:** None

---

### 4. **add book-folder** - Add Book from Folder
**Command:** `rl add book-folder <folder_path> [options]`

**Purpose:** Add a book from a structured folder

**Arguments:**
- `folder_path` (required): Path to book folder

**Options:**
- Same as `add book` command

**What it does:**
- Scans folder for book formats (folder-name.pdf, folder-name.epub, etc.)
- Auto-detects summaries (folder-name-summary-*.pdf, etc.)
- Converts summary PDFs/EPUBs to markdown
- Imports all formats and summaries

**Port?** ✅ YES - Bulk book import
**Changes needed:** None

---

### 5. **fetch video** - Fetch Single YouTube Video
**Command:** `rl fetch video <video_url> [options]`

**Purpose:** Fetch and optionally process a single YouTube video

**Arguments:**
- `video_url` (required): YouTube video ID or URL

**Options:**
- `--hub, -h`: Path to knowledge hub
- `--process-now`: Process video immediately (default for single videos)
- `--save-only`: Save metadata only, don't process
- `--output, -o`: Output file for metadata (required with --save-only)
- `--tags`: Comma-separated tags
- `--categories, -c`: Comma-separated categories

**What it does:**
- Extracts video ID from URL
- Fetches metadata via YouTube API
- Optionally saves to JSON file
- Optionally processes immediately (downloads transcript, creates manifest)

**Port?** ✅ YES - Core video ingestion
**Changes needed:** None

---

### 6. **fetch channel** - Fetch YouTube Channel
**Command:** `rl fetch channel <channel_id> [options]`

**Purpose:** Fetch videos from a YouTube channel

**Arguments:**
- `channel_id` (required): YouTube channel ID

**Options:**
- `--hub, -h`: Path to knowledge hub
- `--process-now`: Process all videos immediately
- `--save-only`: Save metadata only
- `--output, -o`: Output file for metadata (required with --save-only)

**Must specify:** Either --process-now OR --save-only

**What it does:**
- Fetches all videos from channel
- Saves metadata to JSON
- Optionally processes all videos immediately

**Port?** ✅ YES - Bulk video import
**Changes needed:** None

---

### 7. **fetch playlist** - Fetch YouTube Playlist
**Command:** `rl fetch playlist <playlist_id> [options]`

**Purpose:** Fetch videos from a YouTube playlist

**Arguments:**
- `playlist_id` (required): YouTube playlist ID

**Options:**
- Same as `fetch channel`

**What it does:**
- Fetches all videos from playlist
- Saves metadata to JSON
- Optionally processes all videos

**Port?** ✅ YES - Bulk video import
**Changes needed:** None

---

### 8. **add videos** - Process Videos from Metadata File
**Command:** `rl add videos <metadata_file> [options]`

**Purpose:** Process videos from a metadata JSON file

**Arguments:**
- `metadata_file` (required): Path to metadata JSON file

**Options:**
- `--hub, -h`: Path to knowledge hub
- `--limit`: Limit number of videos to process

**What it does:**
- Reads video metadata from JSON file
- **Automatically resumes from where it left off** (resumable batch processing)
- Processes videos one-by-one (downloads transcripts, creates manifests)

**Port?** ✅ YES - Resumable batch processing (key feature!)
**Changes needed:** None

---

### 9. **catalog build** - Build Library Catalog
**Command:** `rl catalog build [options]`

**Purpose:** Build catalog index from all books and videos

**Options:**
- `--hub, -h`: Path to knowledge hub
- `--no-indexes`: Skip generating index.md files in each book folder

**What it does:**
- Scans all manifests
- Creates `.knowledgehub/catalog.json`
- Generates index.md file in each book folder (beautiful navigation)
- Creates master indices (books/_index/authors.md, titles.md)

**Port?** ✅ YES - Core catalog functionality
**Changes needed:** None

---

### 10. **catalog list** - List Books
**Command:** `rl catalog list [options]`

**Purpose:** List all books with optional filters

**Options:**
- `--hub, -h`: Path to knowledge hub
- `--author, -a`: Filter by author
- `--category, -c`: Filter by category
- `--tag, -t`: Filter by tag
- `--title`: Filter by title

**What it does:**
- Queries catalog
- Filters books by metadata
- Displays formatted list

**Port?** ✅ YES - Core browsing functionality
**Changes needed:** None

---

### 11. **catalog authors** - List Authors
**Command:** `rl catalog authors [options]`

**Purpose:** List all unique authors in the library

**Options:**
- `--hub, -h`: Path to knowledge hub

**What it does:**
- Extracts unique authors from catalog
- Displays alphabetically

**Port?** ✅ YES - Browsing helper
**Changes needed:** None

---

### 12. **catalog categories** - List Categories
**Command:** `rl catalog categories [options]`

**Purpose:** List all unique categories in the library

**Options:**
- `--hub, -h`: Path to knowledge hub

**What it does:**
- Extracts unique categories from catalog
- Displays alphabetically

**Port?** ✅ YES - Browsing helper
**Changes needed:** None

---

### 13. **catalog show** - Show Book Details
**Command:** `rl catalog show <book_id> [options]`

**Purpose:** Show detailed information about a specific book

**Arguments:**
- `book_id` (required): Book ID or title substring

**Options:**
- `--hub, -h`: Path to knowledge hub

**What it does:**
- Searches for book by ID or title
- Displays full metadata (author, categories, tags, formats, summaries)

**Port?** ✅ YES - Book detail view
**Changes needed:** None

---

### 14. **catalog formats** - List Book Formats
**Command:** `rl catalog formats <book_id> [options]`

**Purpose:** List available formats for a book

**Arguments:**
- `book_id` (required): Book ID or title substring

**Options:**
- `--hub, -h`: Path to knowledge hub

**What it does:**
- Retrieves all formats for book (PDF, EPUB, Markdown, chapters)
- Separates full-book formats from individual chapters
- Displays paths

**Port?** ✅ YES - Format browsing (key feature!)
**Changes needed:** None

---

### 15. **catalog summaries** - List Book Summaries
**Command:** `rl catalog summaries <book_id> [options]`

**Purpose:** List available summaries for a book

**Arguments:**
- `book_id` (required): Book ID or title substring

**Options:**
- `--hub, -h`: Path to knowledge hub

**What it does:**
- Retrieves all summaries for book
- Displays summary names and paths

**Port?** ✅ YES - Summary browsing (key feature!)
**Changes needed:** None

---

### 16. **catalog get** - Retrieve Book Content
**Command:** `rl catalog get <book_id> [options]`

**Purpose:** Retrieve book content or summary

**Arguments:**
- `book_id` (required): Book ID or title substring

**Options:**
- `--hub, -h`: Path to knowledge hub
- `--format, -f`: Format to retrieve (default "markdown") - can be epub, pdf, chapter-01, etc.
- `--output, -o`: Save to file instead of printing
- `--max-chars`: Truncate output at N characters
- `--summary, -s`: Get a specific summary instead of book content

**What it does:**
- Retrieves content in specified format
- Can get full book or specific chapter
- Can get summary instead
- Outputs to stdout or file

**Port?** ✅ YES - Content retrieval (key feature!)
**Changes needed:** None

---

### 17. **catalog stats** - Show Library Statistics
**Command:** `rl catalog stats [options]`

**Purpose:** Show library statistics

**Options:**
- `--hub, -h`: Path to knowledge hub

**What it does:**
- Shows counts: books, videos, authors, categories, formats, chapters, summaries
- Shows last updated timestamp

**Port?** ✅ YES - Library overview
**Changes needed:** None

---

### 18. **video-state show** - Show Video Processing State
**Command:** `rl video-state show [options]`

**Purpose:** Show video processing state

**Options:**
- `--hub, -h`: Path to knowledge hub

**What it does:**
- Displays which videos have been processed, failed, or pending
- Shows details for recent videos

**Port?** ✅ YES - Resumable processing tracking
**Changes needed:** None

---

### 19. **video-state clear** - Clear Video Processing State
**Command:** `rl video-state clear [options]`

**Purpose:** Clear video processing state

**Options:**
- `--hub, -h`: Path to knowledge hub
- `--video-id`: Clear specific video ID only
- `--yes, -y`: Skip confirmation prompt

**What it does:**
- Clears processed/failed/pending state
- Allows re-adding videos

**Port?** ✅ YES - State management for resumable processing
**Changes needed:** None

---

### 20. **video-state remove** - Remove Video from State
**Command:** `rl video-state remove <video_id> [options]`

**Purpose:** Remove a specific video from processing state

**Arguments:**
- `video_id` (required): Video ID to remove

**Options:**
- `--hub, -h`: Path to knowledge hub

**What it does:**
- Removes video from all state lists
- Allows re-adding that specific video

**Port?** ✅ YES - State management
**Changes needed:** None

---

### 21. **convert** - Convert Between Formats
**Command:** `rl convert <input_file> [options]`

**Purpose:** Convert between Markdown and PDF formats

**Arguments:**
- `input_file` (required): Input file path (.md or .pdf)

**Options:**
- `--output, -o`: Output file path (auto-detected if not provided)

**What it does:**
- Auto-detects format from extension
- .md → .pdf or .pdf → .md
- Uses MarkdownToPDFConverter / PDFToMarkdownConverter

**Port?** ✅ YES - Utility for format conversion
**Changes needed:** None

---

## Commands to EXCLUDE ❌

### 1. **chunk book** - EXCLUDE (Vectorization)
**Command:** `rl chunk book <book_folder>`

**Purpose:** Chunk a book into semantic segments for embedding

**Why exclude?** ❌ This is for vectorization/chunking - outside our scope

---

### 2. **chunk video** - EXCLUDE (Vectorization)
**Command:** `rl chunk video <video_folder>`

**Purpose:** Chunk a video transcript into semantic segments for embedding

**Why exclude?** ❌ Vectorization/chunking

---

### 3. **chunk all** - EXCLUDE (Vectorization)
**Command:** `rl chunk all`

**Purpose:** Chunk all books and videos in the knowledge hub

**Why exclude?** ❌ Vectorization/chunking

---

### 4. **build** - EXCLUDE (Vectorization Pipeline)
**Command:** `rl build [options]`

**Purpose:** Build the full processing pipeline (chunking, embedding, indexing)

**Options:**
- `--skip-chunking`, `--skip-embedding`, `--skip-indexing`
- `--embedding-provider`, `--embedding-model`

**Why exclude?** ❌ This is the entire vectorization pipeline

---

### 5. **index** - EXCLUDE (Vectorization)
**Command:** `rl index [options]`

**Purpose:** Generate human-readable index of all books

**Why exclude?** ❌ WAIT - This might be confusing with catalog!
**NOTE:** This generates INDEX.md with processing status (chunking, embedding)
**Decision:** ❌ EXCLUDE - We have `catalog build` which generates indices

---

### 6. **search** - EXCLUDE (Vector Search)
**Command:** `rl search <query> [options]`

**Purpose:** Search the knowledge hub using semantic vector search

**Options:**
- `--top-k`, `--embedding-provider`, `--embedding-model`

**Why exclude?** ❌ Vector search functionality

---

### 7. **ask** - EXCLUDE (RAG/LLM)
**Command:** `rl ask <query> [options]`

**Purpose:** Ask a question using RAG (Retrieval Augmented Generation)

**Options:**
- `--llm-provider`, `--llm-model`, `--temperature`, `--show-sources`

**Why exclude?** ❌ RAG/LLM functionality

---

### 8. **llm-providers** - EXCLUDE (RAG/LLM)
**Command:** `rl llm-providers`

**Purpose:** List available LLM providers

**Why exclude?** ❌ LLM functionality

---

### 9. **llm-install** - EXCLUDE (RAG/LLM)
**Command:** `rl llm-install <model>`

**Purpose:** Download and install an Ollama model

**Why exclude?** ❌ LLM functionality

---

### 10. **llm-list** - EXCLUDE (RAG/LLM)
**Command:** `rl llm-list`

**Purpose:** List installed Ollama models

**Why exclude?** ❌ LLM functionality

---

## Summary

### Commands to Port: 21 commands ✅

**Setup & Status:**
1. `init` - Initialize hub
2. `status` - Show hub status

**Book Ingestion:**
3. `add book` - Add single book
4. `add book-folder` - Add book from folder

**Video Ingestion:**
5. `fetch video` - Fetch single video
6. `fetch channel` - Fetch channel videos
7. `fetch playlist` - Fetch playlist videos
8. `add videos` - Process videos from file (resumable!)

**Catalog Management:**
9. `catalog build` - Build catalog and indices
10. `catalog list` - List books with filters
11. `catalog authors` - List authors
12. `catalog categories` - List categories
13. `catalog show` - Show book details
14. `catalog formats` - List available formats
15. `catalog summaries` - List summaries
16. `catalog get` - Retrieve content/summary
17. `catalog stats` - Show statistics

**Video State Management:**
18. `video-state show` - Show processing state
19. `video-state clear` - Clear state
20. `video-state remove` - Remove video from state

**Utilities:**
21. `convert` - Convert MD ↔ PDF

### Commands to Exclude: 10 commands ❌

**Chunking:**
- `chunk book`
- `chunk video`
- `chunk all`

**Vectorization:**
- `build` (pipeline)
- `index` (with processing status)
- `search` (vector search)

**RAG/LLM:**
- `ask`
- `llm-providers`
- `llm-install`
- `llm-list`

---

## Command Groups Structure

```
resource-librarian CLI (rl)
├── init                    # Setup
├── status                  # Status
│
├── add/                    # Ingestion group
│   ├── book               # Add single book
│   ├── book-folder        # Add book from folder
│   └── videos             # Process videos from file
│
├── fetch/                  # YouTube group
│   ├── video              # Fetch single video
│   ├── channel            # Fetch channel
│   └── playlist           # Fetch playlist
│
├── catalog/                # Catalog/browsing group
│   ├── build              # Build catalog
│   ├── list               # List books
│   ├── authors            # List authors
│   ├── categories         # List categories
│   ├── show               # Show book details
│   ├── formats            # List formats
│   ├── summaries          # List summaries
│   ├── get                # Get content
│   └── stats              # Statistics
│
├── video-state/            # Video processing state
│   ├── show               # Show state
│   ├── clear              # Clear state
│   └── remove             # Remove video
│
└── convert                 # Utility
```

---

## Next Steps

1. **Technology Deep Dive:**
   - Typer: CLI framework
   - Rich: Terminal output formatting
   - Command structure patterns

2. **Implementation Plan Update:**
   - Add CLI command list to Phase 6
   - Define command priorities (which to implement first)
   - Plan test strategy for each command

3. **User Confirmation:**
   - Review command list
   - Confirm command names and structure
   - Decide on CLI name (kh vs rl vs other)
