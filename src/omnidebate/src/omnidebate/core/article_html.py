"""Read article markup without fetching embedded resources."""

from lxml import etree, html


def article_document(markup: str):
    try:
        document = html.document_fromstring(
            markup.encode("utf-8"), parser=html.HTMLParser(encoding="utf-8", no_network=True)
        )
    except etree.ParserError:
        document = html.Element("html")
    for hidden in document.xpath("//script | //style | //template"):
        hidden.drop_tree()
    return document


def visible_text(element, separator: str = "") -> str:
    return separator.join(part.strip() for part in element.itertext() if part.strip())
