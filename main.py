#!/usr/bin/env python3
"""
deep-crawl CLI - A powerful tool for generating LLM-ready documentation from websites.

Built on crawl4ai with smart defaults for documentation sites.
"""

import asyncio
import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
import tiktoken


def count_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def create_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser with comprehensive options."""
    parser = argparse.ArgumentParser(
        description="A powerful CLI tool for generating LLM-ready documentation from websites.\n\n"
        "Simply provide a URL and get clean, structured content suitable for LLM context.\n"
        "Built on crawl4ai with smart defaults for documentation sites.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  deep-crawl https://docs.stripe.com
  deep-crawl https://docs.react.dev --format json
  deep-crawl https://api.example.com --sections "reference,guides" --auth-header "Bearer token"
  deep-crawl https://docs.python.org --exclude-sections "download,community"
  deep-crawl https://internal-docs.com --cookies "session=abc123"
        """,
    )

    # Required arguments
    parser.add_argument("url", help="URL to crawl")

    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "-o", "--output", help="Output file path (default: auto-generated from URL)"
    )

    filter_group = parser.add_argument_group("Filtering Options")
    filter_group.add_argument(
        "--max-depth",
        type=int,
        default=3,
        help="Maximum depth to crawl (default: 3)",
    )
    filter_group.add_argument(
        "--max-pages",
        type=int,
        default=30,
        help="Maximum pages to crawl (default: 30)",
    )

    # Content filtering
    filter_group = parser.add_argument_group("Content Filtering")
    filter_group.add_argument(
        "--sections",
        help="Include only these sections (comma-separated, e.g., 'api,reference,guides')",
    )
    filter_group.add_argument(
        "--exclude-sections",
        help="Exclude these sections (comma-separated, e.g., 'blog,changelog,download')",
    )
    filter_group.add_argument(
        "--word-threshold",
        type=int,
        default=200,
        help="Minimum words per content block (default: 200)",
    )
    filter_group.add_argument(
        "--include-images",
        action="store_true",
        help="Include image descriptions and alt text (default: False)",
    )
    filter_group.add_argument(
        "--custom-exclude-selectors",
        help="Additional CSS selectors to exclude (comma-separated)",
    )

    # Authentication
    auth_group = parser.add_argument_group("Authentication")
    auth_group.add_argument(
        "--auth-header",
        help="Custom authentication header (e.g., 'Authorization: Bearer token')",
    )
    auth_group.add_argument("--cookies", help="Cookie string or file path")
    auth_group.add_argument("--user-agent", help="Custom user agent string")

    # Output control
    control_group = parser.add_argument_group("Output Control")
    control_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed progress and debug information",
    )
    control_group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Minimal output (only errors and final result)",
    )
    control_group.add_argument(
        "--no-progress", action="store_true", help="Disable progress indicators"
    )

    control_group.add_argument(
        "--include-metadata",
        action="store_true",
        help="Include metadata in the output",
    )

    # Advanced options
    advanced_group = parser.add_argument_group("Advanced Options")
    advanced_group.add_argument(
        "--js-code", help="Custom JavaScript code to execute on each page"
    )
    advanced_group.add_argument(
        "--wait-for",
        help="CSS selector or condition to wait for before extracting content",
    )
    advanced_group.add_argument(
        "--screenshot", action="store_true", help="Save screenshots of crawled pages"
    )
    advanced_group.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Page load timeout in seconds (default: 30)",
    )

    return parser


def generate_output_filename(url: str, format: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "").replace(".", "-")

    domain = re.sub(r"[^\w\-]", "", domain)

    extensions = {"markdown": "md", "json": "json", "xml": "xml"}

    domain = domain if "docs" in domain else f"docs-{domain}"

    return f"{domain}.{extensions[format]}"


def parse_sections(sections_str: Optional[str]) -> List[str]:
    """Parse comma-separated sections string into list."""
    if not sections_str:
        return []
    return [s.strip().lower() for s in sections_str.split(",") if s.strip()]


def parse_cookies(cookies_str: Optional[str]) -> Optional[List[Dict[str, Any]]]:
    """Parse cookies from string or file."""
    if not cookies_str:
        return None

    # Check if it's a file path
    if Path(cookies_str).exists():
        try:
            with open(cookies_str, "r") as f:
                return json.load(f)
        except Exception:
            print(f"Warning: Could not parse cookie file {cookies_str}")
            return None

    # Parse as cookie string (simplified)
    cookies = []
    for cookie in cookies_str.split(";"):
        if "=" in cookie:
            name, value = cookie.split("=", 1)
            cookies.append(
                {
                    "name": name.strip(),
                    "value": value.strip(),
                    "domain": "",  # Will be set by the browser
                    "path": "/",
                }
            )

    return cookies if cookies else None


def parse_auth_header(auth_header: Optional[str]) -> Optional[Dict[str, str]]:
    """Parse authentication header string."""
    if not auth_header:
        return None

    if ":" in auth_header:
        key, value = auth_header.split(":", 1)
        return {key.strip(): value.strip()}

    print(f"Warning: Invalid auth header format: {auth_header}")
    return None


def format_results(results: list[Any], include_metadata: bool = True) -> str:
    """Format the crawl result according to the specified format."""

    def format_result(result: Any) -> str:
        output = result.markdown

        if include_metadata:
            metadata = result._crawl_metadata
            header = "# Documentation Crawl Report\n\n"
            header += f"**Source:** {metadata.get('url', 'Unknown')}\n"
            header += f"**Crawled:** {metadata.get('timestamp', 'Unknown')}\n"
            header += f"**Pages:** {metadata.get('page_count', 'Unknown')}\n"
            header += f"**Strategy:** {metadata.get('strategy', 'Unknown')}\n\n"
            header += "---\n\n"
            output = header + output

        return output

    return "\n".join([format_result(result) for result in results])


async def main(args):
    """Main crawling function."""    
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
        from crawl4ai.content_filter_strategy import PruningContentFilter
        from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
        from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
        from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

    except ImportError as e:
        print(f"Error: Required dependency not found: {e}")
        print("Please install with: uv tool install deep-crawl")
        sys.exit(1)

    # Set up browser configuration
    headers = {}
    if args.auth_header:
        auth_headers = parse_auth_header(args.auth_header)
        if auth_headers:
            headers.update(auth_headers)

    cookies = parse_cookies(args.cookies)

    # Only pass user_agent if one was provided to avoid None issues
    browser_kwargs = {
        "headless": True,
        "cookies": cookies,
        "headers": headers if headers else None,
        "verbose": args.verbose,
    }
    if args.user_agent:
        browser_kwargs["user_agent"] = args.user_agent

    browser_config = BrowserConfig(**browser_kwargs)

    # Set up content filtering
    content_filter = PruningContentFilter(
        min_word_threshold=args.word_threshold,
        threshold_type="word_count",
    )

    # Create markdown generator with filtering
    markdown_generator = DefaultMarkdownGenerator(
        content_filter=content_filter,
    )

    # Set up crawler config
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=args.max_depth,
            max_pages=args.max_pages,
        ),
        markdown_generator=markdown_generator,
        cache_mode=CacheMode.BYPASS,
        screenshot=args.screenshot,
        js_code=args.js_code,
        wait_until="networkidle",
        wait_for=args.wait_for,
        verbose=args.verbose,
        page_timeout=args.timeout * 1000,  # Convert to milliseconds
        scraping_strategy=LXMLWebScrapingStrategy(),
    )

    if not args.quiet:
        print(f"🕷️  Starting crawl of {args.url}")
        print(f"⏱️  Page timeout: {args.timeout}s")
        if args.sections:
            print(f"🎯 Including sections: {args.sections}")
        if args.exclude_sections:
            print(f"🚫 Excluding sections: {args.exclude_sections}")
        print()

    start_time = time.time()

    async with AsyncWebCrawler(config=browser_config) as crawler:
        try:
            if not args.quiet and not args.no_progress:
                print("🔄 Crawling in progress...")

            collected_results = []

            results = await crawler.arun(args.url, config=config)
            for result in results:
                if result.success:
                    content = result.markdown
                    if args.sections or args.exclude_sections:
                        content = filter_sections(
                            content, args.sections, args.exclude_sections
                        )
                        result.markdown = content

                    # Add metadata
                    result._crawl_metadata = {
                        "url": args.url,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "page_count": 1,
                        "strategy": "single-page",
                    }
                    collected_results.append(result)
                else:
                    print(
                        f"❌ Crawl failed: {getattr(result, 'error_message', 'Unknown error')}"
                    )

                end_time = time.time()

            if not args.quiet:
                print()  # New line after progress
                word_count = sum(
                    len(result.markdown.split()) for result in collected_results
                )
                print("✅ Crawl completed successfully!")
                print(f"📊 Stats: {word_count:,} words in {end_time - start_time:.1f}s")

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)

        output_file = args.output or generate_output_filename(args.url, "markdown")

        formatted_output = format_results(
            collected_results, include_metadata=args.include_metadata
        )

        token_count = count_tokens(formatted_output)

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(formatted_output)

            if not args.quiet:
                print(f"💾 Output saved to: {output_file}")
                print(f"📁 File size: {len(formatted_output.encode('utf-8')):,} bytes")
                print(f"🔢 Token count: {token_count:,}")
        except Exception as e:
            print(f"❌ Error saving output: {e}")
            sys.exit(1)


def filter_sections(
    content: str, include_sections: Optional[str], exclude_sections: Optional[str]
) -> str:
    """Filter content based on section includes/excludes."""
    if not content:
        return content

    # Simple section filtering based on headers
    # This is a basic implementation - could be enhanced with more sophisticated parsing

    lines = content.split("\n")
    filtered_lines = []
    include_current = True

    include_list = parse_sections(include_sections)
    exclude_list = parse_sections(exclude_sections)

    for line in lines:
        # Check if this is a header line
        if line.startswith("#"):
            header_text = line.lstrip("#").strip().lower()

            # Determine if we should include this section
            if include_list:
                include_current = any(
                    section in header_text for section in include_list
                )
            elif exclude_list:
                include_current = not any(
                    section in header_text for section in exclude_list
                )
            else:
                include_current = True

        if include_current:
            filtered_lines.append(line)

    return "\n".join(filtered_lines)


def cli():
    """CLI entry point for uv tool install."""
    parser = create_parser()
    args = parser.parse_args()

    # Validate conflicting options
    if args.quiet and args.verbose:
        print("Error: Cannot use both --quiet and --verbose")
        sys.exit(1)

    # Run the async main function
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("\n❌ Crawl interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    cli()
