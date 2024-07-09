from lxml import etree


def verify_xml_structure(xml_response):
    """Perliminary function for xml parsing verification since TEI schema
    validation fails"""
    xml_tree = etree.fromstring(xml_response)
    # Namespace
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}

    # Root element check
    assert xml_tree.tag == "{http://www.tei-c.org/ns/1.0}TEI"

    # text element check
    text_element = xml_tree.find("tei:text", namespaces=ns)
    assert text_element is not None

    # body element check
    body_element = xml_tree.find(".//tei:body", namespaces=ns)
    assert body_element is not None

    # paragraph element check
    paragraph_element = xml_tree.find(".//tei:p", namespaces=ns)
    assert paragraph_element is not None

    # author elements check
    authors = xml_tree.findall(".//tei:author", namespaces=ns)
    assert len(authors) > 0
    # for author in authors:
    #     pers_name = author.find("tei:persName", namespaces=ns)
    #     assert pers_name is not None
    #     forename = pers_name.find("tei:forename", namespaces=ns)
    #     surname = pers_name.find("tei:surname", namespaces=ns)
    #     assert forename is not None
    #     assert surname is not None

    # monogr elements check
    monogr = xml_tree.find(".//tei:monogr", namespaces=ns)
    assert monogr is not None
    title = monogr.find("tei:title", namespaces=ns)
    assert title is not None
    # assert title.text.strip() == "Nature human behaviour"
    imprint = monogr.find("tei:imprint", namespaces=ns)
    assert imprint is not None
    volume = imprint.find("tei:biblScope[@unit='volume']", namespaces=ns)
    assert volume is not None
    # assert volume.text.strip() == "3"
    # issue = imprint.find("tei:biblScope[@unit='issue']", namespaces=ns)
    # assert issue is not None
    # assert issue.text.strip() == "8"
    date = imprint.find("tei:date[@type='published']", namespaces=ns)
    assert date is not None
    # assert date.get("when") == "2019"

    # Check other elements if necessary
    # ...
