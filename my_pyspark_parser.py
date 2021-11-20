import re
import unidecode


# format elapsed time into h:mm:ss
def time_formater(elapsed_time):
    hour = int(elapsed_time / (60 * 60))
    mins = int((elapsed_time % (60 * 60)) / 60)
    secs = elapsed_time % 60
    return "{}:{:>02}:{:>05.2f}".format(hour, mins, secs)


# removes excess whitespace from string + other stuff
def string_formater(string, basic=True):

    if basic:
        string = unidecode.unidecode(string)
        string = string.lower()
        string = string.replace('noinclude', '')
        string = re.sub(r'[\"\[\]]', ' ', string)
        string = re.sub(r' +', ' ', string)
        string = re.sub(r'[^a-z0-9|()*=]+', ' ', string)
    else:
        string = re.sub(r'{.*?(?=\})',' ', string)
        string = re.sub(r'(?i)< *ref.*< */ *ref',' ', string)

    return string


# extract some informations about writer from writer pages
def extract_writer_page(page):
    page = page.replace('\n', ' ')
    data = re.search('(?i)== *(works|bibliography) *==.*?(?=(  *==[a-zA-Z ]*==))', str(page)).group()

    if data == None:
        return 'writer | '
    else:
        #data = data.group(0)
        data = string_formater(data, False)

    return 'writer | ' + data


# extract data out of infoboxes by using regular expressions
def extract_infobox_data(page):
    data = []

    # select from infobox book or short story
    if re.search('(?i){{Infobox *(book|short story)', page):
        to_save = 'book | '
        data.append(re.findall('(?i)name *=.*?(?=\|)\|', page))
        data.append(re.findall('(?i)author *=.*?(?=\])\] *\|', page))
        data.append(re.findall('(?i)genre *=.*?(?=\])\] *\|', page))
        data.append(re.findall('(?i)pages *=.*?(?=\|)\|', page))

        for item in data:
            to_save += ''.join(item)
        return to_save

    # select from infobox film
    elif re.search('(?i){{Infobox *film', page):
        to_save = 'film | '
        data.append(re.findall('(?i)name *=.*?(?=\|)\|', page))
        data.append(re.findall('(?i)director *=.*?(?=\])\] *\|', page))
        data.append(re.findall('(?i)based_on *=.*?(?=\}\})\}\} *\|', page))

        for item in data:
            to_save += ''.join(item)
        return to_save

    return page


# extract data out of infoboxes by using regular expressions
def extract_navbox_data(page):
    data = []
    to_save = 'navbox | '

    data.append(re.findall('(?i)name *=.*?(?=\|)\|', page))
    data.append(re.findall('(?i)group\d+ *=.*', page))

    for item in data:
        to_save += ''.join(item)
    to_save = re.sub('(?i){{noitalic\|\(\d+\)\}\}', ' ', to_save)
    return to_save


# parse Infoboxes and Navboxes using regular expressions
def select_boxed_data(content):
    buffer = []
    content_parser = False
    content_helper = False

    for line in content.splitlines():
        if re.search('(?i){{Infobox *(book|short story|film)', line) or re.search('(?i){{Navbox', line):
            content_parser = True
            buffer.append(line)
            continue

        if content_parser and re.search('{{', line):
            content_helper = True

        if content_helper and re.search('}}', line):
            content_helper = False
            buffer.append(line)
            continue

        if content_parser and content_helper == False and re.search('}}', line):
            content_parser = False
            content_helper = False
            buffer.append(line)
            continue

        if content_parser:
            buffer.append(line)
            continue

    to_return = ' '.join(buffer).replace('\n', ' ')
    return to_return


# save and extract informations from selected pages, throw away others
def save_page(content):

    # extract information from selected infoboxes
    if re.search('(?i){{Infobox *(book|short story|film)', str(content)):
        content = select_boxed_data(content)
        to_return = extract_infobox_data(content)
        to_return = string_formater(to_return)
        return to_return

    # extract information from selected navboxes
    elif re.search('(?i){{Navbox', str(content)):
        content = select_boxed_data(content)
        to_return = extract_navbox_data(content)
        to_return = string_formater(to_return)
        return to_return

    # extract information from pages about writers (their bibliography)
    elif re.search('(?i)== *(works|bibliography) *==', str(content)):
        to_return = extract_writer_page(content)
        to_return = string_formater(to_return)
        return to_return

    # return None if page not relevant
    return None