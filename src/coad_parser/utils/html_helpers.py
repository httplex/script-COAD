from bs4 import BeautifulSoup
from bs4.element import Tag


def encontra_tag_por_label(
    soup: BeautifulSoup,
    label: str,
    tags: tuple[str, ...] = ("p", "div", "td"),
) -> Tag | None:
    label_lower = label.lower()
    return soup.find(
        lambda tag: tag.name in tags
        and label_lower in tag.get_text(" ", strip=True).lower()
    )