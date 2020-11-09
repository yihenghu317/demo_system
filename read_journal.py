import lxml.etree as ET
import sys


# read journal from j_name conference published after nyear

def generate_file(path, j_name, nyear):
    # context = ET.iterparse('./data/test_dblp.xml',events=("end",),recover=True)
    # context = ET.iterparse('new_dblp.xml',events=("end",),recover=True)
    context = ET.iterparse(path, events=("end",), recover=True)
    context = iter(context)

    # new_file_name = "dblp_" + "".join([n[0] for n in j_name]) + ".xml"
    new_file_name = "dblp_" + '_'.join(j_name) + '_' + str(nyear) + '.xml'
    # with open(new_file_name,'wb') as doc:
    #     doc.write(ET.tostring(root,pretty_print=True))
    root = ET.Element("dblp")

    authors = []
    # count = 0

    title = ""
    year = 0
    journal = ""
    book_title = ""

    for event, element in context:
        # if i > 100:
        #     break
        # i += 1
        if element.text is None:
            continue

        text = element.text

        if element.tag == 'author':

            authors.append(text)
        if element.tag == 'title':
            title = text
        if element.tag == "journal":
            journal = text
        if element.tag == "booktitle":
            book_title = text
        if element.tag == "year":
            year = text

        if len(element) >= 2:

            if journal == "" and book_title == "":
                authors = []
                title = ""
                journal = ""
                year = ""
                continue

            if year == "" or (int)(year) < (int)(nyear):
                authors = []
                title = ""
                journal = ""
                year = ""
                continue

            if_go_article = False
            #
            for i in j_name:
                if i.lower() in (journal+" "+book_title).lower():
                    if_go_article = True
                    break

            if if_go_article:

                try:
                    d = ET.SubElement(root, element.tag)
                    d.text = element.text

                    for i in authors:
                        child = ET.SubElement(d, 'author')
                        child.text = i
                    # print(title)

                    t = ET.SubElement(d, 'title')
                    t.text = title
                    # print(authors)

                    # print()
                except:
                    pass
                    # print("character error")

            authors = []
            title = ""
            journal = ""
            year = ""

    with open(new_file_name, 'wb') as doc:
        doc.write(ET.tostring(root, pretty_print=True))
    return new_file_name


if len(sys.argv) <= 2:
    print("Input arguments format: <path of data file> <year> <journal name> ...")
else:
    path = sys.argv[1]
    year = sys.argv[2]
    name = sys.argv[3:]
    newfn = generate_file(path, name, year)
    print("Your new generated file is", newfn)
