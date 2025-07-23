# deep-crawl CLI

> A powerful CLI tool for generating LLM-ready documentation from websites

Built on [crawl4ai](https://github.com/unclecode/crawl4ai) with smart defaults for documentation sites. Perfect for creating focused, clean content for LLM context windows.

## ✨ Features

- **Smart defaults** - Just provide a URL and get clean LLM-ready content
- **Deep crawling** - Multi-page crawling with configurable depth and page limits
- **Token counting** - Built-in OpenAI token counting with tiktoken
- **Built-in content filtering** - Removes boilerplate and extracts meaningful content
- **Section filtering** - Include or exclude specific documentation sections
- **Authentication support** - Headers, cookies, custom user agents
- **Progress reporting** - Real-time crawling progress with statistics
- **JavaScript execution** - Custom JS code execution for dynamic content
- **Screenshots** - Optional page screenshots for debugging

## 🚀 Installation

### Prerequisites

- Python 3.11+
- uv
- Playwright

#### Installing `playwright` cli

```bash
npm install -g playwright
playwright install
```

[Playwright Installation Guide](https://playwright.dev/docs/intro#installing-playwright)


### Option 1: Install with uv

```bash
# Install using uv (handles all dependencies automatically)
uv tool install git+https://github.com/ASRagab/deep-crawl.git

# Or if published to PyPI
uv tool install deep-crawl


```

This creates an isolated environment and gives you a `deep-crawl` command that works regardless of your local Python setup.

### Option 2: Local development

```bash
git clone https://github.com/ASRagab/deep-crawl.git
cd deep-crawl
uv run deep-crawl --help
```

## 📖 Usage

### Simple Usage

```bash
# Crawl a single documentation page
deep-crawl https://docs.stripe.com

# Deep crawl with default settings (3 levels, max 30 pages)
deep-crawl https://docs.react.dev

# Output: docs-react-dev.md with clean, LLM-ready content + token count
```

### Common Examples

```bash
# Control crawling depth and scope
deep-crawl https://docs.python.org --max-depth 2 --max-pages 50

# Include only specific sections
deep-crawl https://docs.python.org --sections "tutorial,library,reference"

# Exclude unwanted sections
deep-crawl https://docs.aws.amazon.com --exclude-sections "blog,news,events"

# Use with authentication for internal docs
deep-crawl https://internal-docs.com \
  --auth-header "Authorization: Bearer your-token" \
  --max-depth 4

# Custom output location with metadata
deep-crawl https://api.example.com \
  --output my-docs.md \
  --sections "reference,guides" \
  --include-metadata
```

### Advanced Usage

```bash
# Comprehensive crawl with authentication and filtering
deep-crawl https://private-docs.example.com \
  --auth-header "Authorization: Bearer token123" \
  --cookies "session=abc123; user=dev" \
  --sections "api,tutorials" \
  --exclude-sections "changelog,blog" \
  --max-depth 5 \
  --max-pages 100 \
  --custom-exclude-selectors ".promo,.sidebar" \
  --screenshot \
  --include-metadata \
  --verbose
```

## 🎛️ CLI Options

### Basic Options

| Option         | Default        | Description      |
| -------------- | -------------- | ---------------- |
| `url`          | required       | URL to crawl     |
| `-o, --output` | auto-generated | Output file path |

### Filtering Options

| Option        | Default | Description            |
| ------------- | ------- | ---------------------- |
| `--max-depth` | `3`     | Maximum crawling depth |
| `--max-pages` | `30`    | Maximum pages to crawl |

### Content Filtering

| Option                       | Default | Description                                   |
| ---------------------------- | ------- | --------------------------------------------- |
| `--sections`                 | none    | Include only these sections (comma-separated) |
| `--exclude-sections`         | none    | Exclude these sections (comma-separated)      |
| `--word-threshold`           | `200`   | Minimum words per content block               |
| `--include-images`           | `false` | Include image descriptions                    |
| `--custom-exclude-selectors` | none    | Additional CSS selectors to exclude           |

### Authentication

| Option          | Description                  |
| --------------- | ---------------------------- |
| `--auth-header` | Custom authentication header |
| `--cookies`     | Cookie string or file path   |
| `--user-agent`  | Custom user agent string     |

### Output Control

| Option               | Description                      |
| -------------------- | -------------------------------- |
| `-v, --verbose`      | Show detailed progress           |
| `-q, --quiet`        | Minimal output                   |
| `--no-progress`      | Disable progress indicators      |
| `--include-metadata` | Include crawl metadata in output |

### Advanced Options

| Option         | Default | Description                  |
| -------------- | ------- | ---------------------------- |
| `--js-code`    | none    | Custom JavaScript to execute |
| `--wait-for`   | none    | CSS selector to wait for     |
| `--screenshot` | `false` | Save page screenshots        |
| `--timeout`    | `30`    | Page load timeout (seconds)  |

## 📁 Output Format

### Markdown with Metadata (Default)

Clean, LLM-ready markdown with optional metadata header:

```markdown
# Documentation Crawl Report

**Source:** https://docs.example.com
**Crawled:** 2024-01-15 10:30:00
**Pages:** 15
**Strategy:** BFS

---

# API Documentation

...

# Getting Started Guide

...
```

### File Naming Convention

- **With "docs" in domain**: `docs-stripe-com.md`
- **Without "docs"**: `docs-react-dev.md`
- **Custom output**: Use `--output custom-name.md`

## 🔢 Token Counting

Built-in token counting using OpenAI's `tiktoken` library:

```bash
✅ Crawl completed successfully!
📊 Stats: 15,420 words in 45.2s
💾 Output saved to: docs-stripe-com.md
📁 File size: 87,234 bytes
🔢 Token count: 23,456
```

Perfect for understanding LLM context window usage before feeding content to models.

## 🛡️ Built-in Safeguards

- **Smart content filtering** - Automatically removes navigation, ads, boilerplate
- **Reasonable defaults** - Max 30 pages, depth 3 to prevent runaway crawls
- **Configurable limits** - Adjust depth and page count based on your needs
- **Error handling** - Graceful failures with clear error messages
- **Progress tracking** - Shows what's happening during crawls

## 🎯 Perfect For

- **LLM context preparation** - Clean, focused documentation with token counts
- **Documentation archival** - Comprehensive site crawling with depth control
- **API reference extraction** - Multi-page crawling of structured documentation
- **Knowledge base creation** - Extract entire documentation trees
- **Content analysis** - Deep analysis of documentation sites

## 🔧 Configuration

The tool uses CLI arguments only (no config files needed), but you can create shell aliases for common patterns:

```bash
# Add to your .bashrc/.zshrc
alias crawl-deep="deep-crawl --max-depth 5 --max-pages 100 --include-metadata"
alias crawl-api="deep-crawl --sections 'api,reference' --max-depth 2"
alias crawl-quick="deep-crawl --max-depth 1 --max-pages 10"

# Usage
crawl-deep https://docs.stripe.com
crawl-api https://docs.react.dev
crawl-quick https://docs.example.com
```

## 🐛 Troubleshooting

### Deep Crawling Issues

```bash
# Reduce scope for large sites
deep-crawl https://huge-docs.com --max-depth 2 --max-pages 20

# Focus on specific sections
deep-crawl https://complex-site.com --sections "getting-started" --max-depth 3
```

### Authentication Issues

```bash
# Try different auth methods
deep-crawl https://example.com --auth-header "Authorization: Bearer token"
deep-crawl https://example.com --cookies "session=abc123"
deep-crawl https://example.com --user-agent "MyBot/1.0"
```

### Timeout Issues

```bash
# Increase timeout for slow sites
deep-crawl https://example.com --timeout 60
```

### Debug Mode

```bash
# Get detailed information about the crawling process
deep-crawl https://example.com --verbose --no-progress
```

## 📊 Examples by Documentation Type

### API Documentation (Stripe, Twilio)

```bash
deep-crawl https://docs.stripe.com \
  --sections "api" \
  --max-depth 3 \
  --include-metadata
```

### Framework Docs (React, Vue)

```bash
deep-crawl https://docs.react.dev \
  --exclude-sections "blog,community" \
  --max-depth 4 \
  --max-pages 50
```

### Cloud Provider Docs (AWS, GCP)

```bash
deep-crawl https://docs.aws.amazon.com \
  --sections "documentation" \
  --max-depth 2 \
  --max-pages 100
```

### Internal Company Wikis

```bash
deep-crawl https://wiki.company.com \
  --auth-header "Authorization: Bearer internal-token" \
  --sections "engineering,apis" \
  --max-depth 3
```

## 🚧 Current Limitations

- **Markdown output only** - Currently only outputs markdown format
- **JavaScript-heavy SPAs** - Some dynamic content may require custom `--js-code`
- **Section detection** - Uses simple header-based section filtering
- **Authentication complexity** - Only supports basic auth methods

## 🗺️ Roadmap

- **Multiple output formats** - JSON and XML output options
- **Advanced content filtering** - More sophisticated content extraction
- **Enhanced section detection** - Better automatic section identification
- **Config files** - Optional configuration file support
- **Parallel crawling** - Faster crawling with concurrent requests

## 🤝 Contributing

```bash
git clone https://github.com/ASRagab/deep-crawl.git
cd deep-crawl
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"
```

## 📦 Dependencies

- **crawl4ai** - Core crawling engine
- **tiktoken** - OpenAI token counting
- **Python 3.11+** - Modern Python features

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built on the excellent [crawl4ai](https://github.com/unclecode/crawl4ai) library by [@unclecode](https://github.com/unclecode).
