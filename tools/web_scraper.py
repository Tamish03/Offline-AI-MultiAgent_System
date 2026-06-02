import urllib.request
import urllib.parse
from html.parser import HTMLParser
import re

class TextExtractParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.tag_stack = []  # list of (tag_name_lower, is_ignored)
        self.title = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        
        # Check if parent is ignored
        parent_ignored = self.tag_stack[-1][1] if self.tag_stack else False
        
        # Determine if this tag itself should be ignored
        ignored = parent_ignored or self._should_ignore_tag(t, attrs)
        
        self.tag_stack.append((t, ignored))
        
        if t == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        t = tag.lower()
        if self.tag_stack:
            # Find the last occurrence of this tag to close it
            idx = -1
            for i in range(len(self.tag_stack) - 1, -1, -1):
                if self.tag_stack[i][0] == t:
                    idx = i
                    break
            if idx != -1:
                self.tag_stack = self.tag_stack[:idx]
            else:
                self.tag_stack.pop() if self.tag_stack else None
                
        if t == "title":
            self.in_title = False

    def handle_data(self, data):
        # Check if currently ignoring
        is_ignored = self.tag_stack[-1][1] if self.tag_stack else False
        if is_ignored:
            return
            
        if self.in_title:
            self.title += data
        else:
            self.text_parts.append(data)

    def _should_ignore_tag(self, tag, attrs):
        ignored_tag_names = {
            "script", "style", "noscript", "iframe", "svg", 
            "nav", "footer", "header", "aside", "form", "button", "input"
        }
        if tag in ignored_tag_names:
            return True
            
        ignored_keywords = {
            "sidebar", "nav", "menu", "footer", "header", "toc", 
            "table-of-contents", "languages", "lang-list", "mw-panel", 
            "vector-menu", "vector-toc", "banner", "popup", "cookie", 
            "advertisement", "widget", "social-share", "breadcrumb", "top-bar"
        }
        for name, value in attrs:
            if name in ("class", "id") and value:
                val_lower = value.lower()
                if any(kw in val_lower for kw in ignored_keywords):
                    return True
        return False

    def get_text(self):
        text = " ".join(self.text_parts)
        # Collapse multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

def scrape_url(url: str):
    """
    Fetches the content of a URL and returns a dict (success, title, content, url/error)
    using only standard library packages.
    """
    try:
        # Validate URL
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            # Try to prepend https:// if missing
            url = "https://" + url
            parsed = urllib.parse.urlparse(url)
            
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            charset = response.headers.get_content_charset() or 'utf-8'
            html_data = response.read().decode(charset, errors='replace')
            
        parser = TextExtractParser()
        parser.feed(html_data)
        
        title = parser.title.strip() or parsed.netloc
        text = parser.get_text()
        
        return {
            "success": True,
            "title": title,
            "content": text,
            "url": url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }
