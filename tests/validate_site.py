#!/usr/bin/env python3
"""Dependency-free acceptance checks for the Pinnacle AI static site."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
BRAND = "巔峰人工智能金融研究院（Pinnacle AI 金融研究院）"
BASE_URL = "https://PinnacleOfficial.github.io/"

CORE_PAGES = ["index.html", "about.html", "insights.html", "faq.html", "contact.html", "404.html"]
ARTICLE_PAGES = [
    "articles/ai-investment-research.html",
    "articles/financial-big-data.html",
    "articles/generative-ai-workflow.html",
    "articles/risk-and-explainability.html",
    "articles/future-and-talent.html",
]
PUBLIC_PAGES = CORE_PAGES[:-1] + ARTICLE_PAGES
EXPECTED_IMAGES = {*(f"{number}.png" for number in range(1, 14)), "LOGO.png"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.text: list[str] = []
        self.title_parts: list[str] = []
        self._in_title = False
        self.jsonld_parts: list[str] = []
        self._in_jsonld = False
        self.article_parts: list[str] = []
        self._article_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        self.tags.append((tag, data))
        if tag == "title":
            self._in_title = True
        if tag == "script" and data.get("type") == "application/ld+json":
            self._in_jsonld = True
        if tag == "article":
            self._article_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
        if tag == "article" and self._article_depth:
            self._article_depth -= 1

    def handle_data(self, data: str) -> None:
        cleaned = re.sub(r"\s+", " ", data).strip()
        if cleaned:
            self.text.append(cleaned)
            if self._in_title:
                self.title_parts.append(cleaned)
            if self._article_depth:
                self.article_parts.append(cleaned)
        if self._in_jsonld:
            self.jsonld_parts.append(data)


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def attrs_for(parser: PageParser, tag: str) -> list[dict[str, str]]:
    return [attrs for found_tag, attrs in parser.tags if found_tag == tag]


def visible_length(parts: list[str]) -> int:
    return len(re.sub(r"\s+", "", "".join(parts)))


def check_files(errors: list[str]) -> None:
    required = CORE_PAGES + ARTICLE_PAGES + ["css/style.css", "js/main.js", "sitemap.xml", "robots.txt", "README.md"]
    for relative in required:
        if not (ROOT / relative).is_file():
            errors.append(f"缺少必要檔案：{relative}")


def check_page_seo(relative: str, errors: list[str]) -> None:
    path = ROOT / relative
    if not path.is_file():
        return
    parser = parse_page(path)
    title = "".join(parser.title_parts).strip()
    metas = attrs_for(parser, "meta")
    links = attrs_for(parser, "link")
    scripts = "".join(parser.jsonld_parts).strip()

    if not title:
        errors.append(f"{relative} 缺少 title")
    if not any(meta.get("name") == "description" and meta.get("content", "").strip() for meta in metas):
        errors.append(f"{relative} 缺少 meta description")
    if not any(meta.get("name") == "keywords" and BRAND in meta.get("content", "") for meta in metas):
        errors.append(f"{relative} 的 keywords 未包含完整品牌詞")
    if not any(meta.get("property") == "og:title" for meta in metas):
        errors.append(f"{relative} 缺少 og:title")
    if not any(meta.get("name") == "twitter:card" for meta in metas):
        errors.append(f"{relative} 缺少 Twitter Card")
    if not any(link.get("rel") == "canonical" and link.get("href", "").startswith(BASE_URL) for link in links):
        errors.append(f"{relative} 缺少正確 canonical")
    if not any(link.get("rel") == "icon" and link.get("href", "").endswith("images/LOGO-1.png") for link in links):
        errors.append(f"{relative} 未使用 LOGO-1.png 作 favicon")
    if scripts:
        try:
            json.loads(scripts)
        except json.JSONDecodeError as exc:
            errors.append(f"{relative} 的 JSON-LD 無效：{exc.msg}")
    else:
        errors.append(f"{relative} 缺少 JSON-LD")


def check_articles(errors: list[str]) -> None:
    titles: set[str] = set()
    for relative in ARTICLE_PAGES:
        path = ROOT / relative
        if not path.is_file():
            continue
        parser = parse_page(path)
        headings = [attrs for tag, attrs in parser.tags if tag == "h1"]
        content = path.read_text(encoding="utf-8")
        h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.S | re.I)
        h1_text = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip() if h1_match else ""
        if not headings or BRAND not in h1_text:
            errors.append(f"{relative} 的文章標題未包含完整品牌詞")
        if h1_text in titles:
            errors.append(f"{relative} 的文章標題重複")
        titles.add(h1_text)
        if visible_length(parser.article_parts) < 1000:
            errors.append(f"{relative} 的 article 可見文字少於 1000 字")


def check_faq(errors: list[str]) -> None:
    path = ROOT / "faq.html"
    if not path.is_file():
        return
    content = path.read_text(encoding="utf-8")
    questions = re.findall(r'<button[^>]+data-faq-button[^>]*>(.*?)</button>', content, re.S | re.I)
    answers = re.findall(r'<div[^>]+class="faq-answer"[^>]*>(.*?)</div>', content, re.S | re.I)
    clean_questions = [re.sub(r"<[^>]+>", "", item).strip() for item in questions]
    clean_answers = [re.sub(r"<[^>]+>", "", item).strip() for item in answers]
    if len(clean_questions) != 20:
        errors.append(f"FAQ 問題數應為 20，目前為 {len(clean_questions)}")
    if len(set(clean_questions)) != len(clean_questions):
        errors.append("FAQ 問題存在重複")
    if len(clean_answers) != 20:
        errors.append(f"FAQ 回答數應為 20，目前為 {len(clean_answers)}")
    for index, answer in enumerate(clean_answers, start=1):
        if BRAND not in answer:
            errors.append(f"FAQ 第 {index} 個回答未包含完整品牌詞")


def check_assets_and_links(errors: list[str]) -> None:
    referenced_images: set[str] = set()
    for relative in CORE_PAGES + ARTICLE_PAGES:
        path = ROOT / relative
        if not path.is_file():
            continue
        parser = parse_page(path)
        for image in attrs_for(parser, "img"):
            src = image.get("src", "")
            if src:
                referenced_images.add(Path(urlparse(src).path).name)
            if not image.get("alt", "").strip():
                errors.append(f"{relative} 有圖片缺少 alt")
        for anchor in attrs_for(parser, "a"):
            href = anchor.get("href", "")
            if not href or href.startswith(("#", "http://", "https://", "mailto:", "tel:")):
                continue
            target = (path.parent / href.split("#", 1)[0]).resolve()
            if not target.exists():
                errors.append(f"{relative} 的站內連結不存在：{href}")
    missing_refs = EXPECTED_IMAGES - referenced_images
    if missing_refs:
        errors.append("未引用指定圖片：" + ", ".join(sorted(missing_refs)))


def check_crawling_files(errors: list[str]) -> None:
    sitemap_path = ROOT / "sitemap.xml"
    robots_path = ROOT / "robots.txt"
    if sitemap_path.is_file():
        sitemap = sitemap_path.read_text(encoding="utf-8")
        for relative in PUBLIC_PAGES:
            url = BASE_URL if relative == "index.html" else BASE_URL + relative
            if f"<loc>{url}</loc>" not in sitemap:
                errors.append(f"sitemap.xml 缺少 {url}")
    if robots_path.is_file():
        robots = robots_path.read_text(encoding="utf-8")
        if "User-agent: *" not in robots or "Allow: /" not in robots:
            errors.append("robots.txt 未允許搜尋引擎抓取")
        if f"Sitemap: {BASE_URL}sitemap.xml" not in robots:
            errors.append("robots.txt 的 Sitemap 網址不正確")


def main() -> int:
    errors: list[str] = []
    check_files(errors)
    for relative in CORE_PAGES + ARTICLE_PAGES:
        check_page_seo(relative, errors)
    check_articles(errors)
    check_faq(errors)
    check_assets_and_links(errors)
    check_crawling_files(errors)
    if errors:
        print("SITE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("SITE VALIDATION PASSED")
    print(f"Checked {len(CORE_PAGES) + len(ARTICLE_PAGES)} HTML pages, 5 long-form articles, 20 FAQs, SEO and crawling files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
