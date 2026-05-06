import urllib.request
import xml.etree.ElementTree as ET
import re

RSS_URL = "https://store.steampowered.com/feeds/news/app/4371150/?l=english"
HTML_FILE = "index.html"
MORE_URL = "https://store.steampowered.com/news/app/4371150"
MAX_ENTRIES = 5


def fetch_rss(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        return response.read()


def parse_rss(xml_data):
    root = ET.fromstring(xml_data)
    channel = root.find("channel")
    entries = []
    for item in channel.findall("item")[:MAX_ENTRIES]:
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub_date = item.findtext("pubDate", "").strip()
        entries.append({"title": title, "link": link, "pub_date": pub_date})
    return entries


def build_script_block(entries):
    lines = ["        // hardcode news entries\n"]
    for e in entries:
        title = e["title"].replace("\\", "\\\\").replace('"', '\\"')
        lines.append(
            f'\n        createNewsEntry(\n'
            f'            "{title}",\n'
            f'            "{e["link"]}",\n'
            f'            new Date("{e["pub_date"]}")\n'
            f'        );'
        )
    lines.append(f'\n        createNewsEntry("View more...", "{MORE_URL}");')
    return "".join(lines)


def update_html(html_path, new_block):
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"        // hardcode news entries.*?(?=\n    </script>)"
    new_content, count = re.subn(pattern, new_block, content, flags=re.DOTALL)

    if count == 0:
        raise RuntimeError("Could not find the news block in index.html")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)


if __name__ == "__main__":
    xml_data = fetch_rss(RSS_URL)
    entries = parse_rss(xml_data)
    new_block = build_script_block(entries)
    update_html(HTML_FILE, new_block)
    print(f"Updated {HTML_FILE} with {len(entries)} news entries:")
    for e in entries:
        print(f"  - {e['title']}")
