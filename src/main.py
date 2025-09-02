import os
import sys
import shutil
import json

macros = {
    'hello': lambda: print("Hello from macro!"),
    'date': lambda: print("This is a simple macro example.")
}

def ansi(text, code='0'):
    return f'\033[{code}m{text}\033[0m'

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def input_optional(prompt):
    val = input(prompt + ' (optional): ')
    return val.strip() if val.strip() else None

def save_community_metadata(name, genre, desc, age):
    folder = f'.{name}'
    if not os.path.exists(folder):
        os.mkdir(folder)
    meta = {'Name': name, 'Genre': genre or '', 'Description': desc or '', 'AgeRestriction': age or ''}
    with open(os.path.join(folder, '_metadata.json'), 'w') as f:
        json.dump(meta, f)
    macro_file = os.path.join(folder, '_edit_macros.json')
    if not os.path.exists(macro_file):
        json.dump({}, open(macro_file, 'w'))

def load_communities():
    return [d for d in os.listdir() if os.path.isdir(d) and d.startswith('.')]

def read_metadata(comm):
    path = os.path.join(comm, '_metadata.json')
    if os.path.exists(path):
        return json.load(open(path))
    return {}

def load_edit_macros(comm):
    path = os.path.join(comm, '_edit_macros.json')
    if os.path.exists(path):
        return json.load(open(path))
    return {}

def save_edit_macros(comm, data):
    path = os.path.join(comm, '_edit_macros.json')
    with open(path, 'w') as f:
        json.dump(data, f)

def list_pages(comm):
    return [f for f in os.listdir(comm) if f.endswith('.md')]

def render_markdown(content):
    lines = content.split('\n')
    rendered = []
    for line in lines:
        if line.startswith('# '):
            rendered.append(ansi(line[2:], '1;34'))
        elif line.startswith('## '):
            rendered.append(ansi(line[3:], '1;36'))
        elif line.startswith('### '):
            rendered.append(ansi(line[4:], '1;32'))
        elif line.startswith('- '):
            rendered.append(ansi('• ' + line[2:], '0;33'))
        elif line.startswith('> '):
            rendered.append(ansi(line, '0;35'))
        elif line.startswith('`') and line.endswith('`'):
            rendered.append(ansi(line[1:-1], '0;37'))
        elif line.startswith('@macro '):
            macro_name = line[7:].strip()
            rendered.append(ansi(f'[Macro: {macro_name}]', '1;35'))
            if macro_name in macros:
                macros[macro_name]()
        elif line.startswith('@replay '):
            rendered.append(ansi(f'[Edit Macro: {line[8:]}]', '1;36'))
        elif line.startswith('#tag '):
            rendered.append(ansi(f'[Tag: {line[5:]}]', '1;33'))
        else:
            tmp = line.replace('**', '\033[1m').replace('*', '\033[3m') + '\033[0m'
            rendered.append(tmp)
    return '\n'.join(rendered)

def create_community():
    name = input('Community Name: ').strip()
    genre = input_optional('Genre')
    desc = input_optional('Description')
    age = input_optional('Age Restriction')
    save_community_metadata(name, genre, desc, age)
    print(f'Community "{name}" created.')

def delete_community():
    communities = load_communities()
    for i, c in enumerate(communities):
        print(f'{i+1}. {c[1:]}')
    idx = int(input('Select community to delete: ')) - 1
    shutil.rmtree(communities[idx])
    print('Deleted.')

def rename_community():
    communities = load_communities()
    for i, c in enumerate(communities):
        print(f'{i+1}. {c[1:]}')
    choice = input('Select community to rename (number or name): ').strip()
    if choice.isdigit():
        idx = int(choice)-1
    else:
        names = [c[1:] for c in communities]
        if choice not in names:
            print("Community not found")
            return
        idx = names.index(choice)
    new_name = input('New name: ').strip()
    os.rename(communities[idx], f'.{new_name}')
    print('Community renamed.')

def rename_page(comm):
    pages = list_pages(comm)
    if not pages:
        print('No pages to rename.')
        return
    for i, p in enumerate(pages):
        print(f'{i+1}. {p}')
    choice = input('Select page to rename (number or name): ').strip()
    if choice.isdigit():
        idx = int(choice)-1
        old_name = pages[idx]
    elif choice in pages:
        old_name = choice
    else:
        print("Page not found")
        return
    new_name = input('New page name (with .md): ').strip()
    os.rename(os.path.join(comm, old_name), os.path.join(comm, new_name))
    print('Page renamed.')

def edit_page(comm):
    pages = list_pages(comm)
    print('Pages:')
    for i, p in enumerate(pages):
        print(f'{i+1}. {p}')
    choice = input('Enter page number or new page name: ').strip()
    if choice.isdigit() and int(choice)-1 < len(pages):
        filename = pages[int(choice)-1]
    else:
        filename = choice if choice.endswith('.md') else choice + '.md'
    path = os.path.join(comm, filename)
    content = ''
    if os.path.exists(path):
        with open(path) as f:
            content = f.read()
    print('--- Current Content ---')
    print(render_markdown(content))
    print('--- Enter new content or macro commands (end with ---) ---')
    lines = content.split('\n') if content else []
    new_lines = []
    recording = False
    macro_name = ''
    edit_macros = load_edit_macros(comm)
    while True:
        line = input()
        if line.strip() == '---':
            break
        if line.startswith(':macro '):
            recording = True
            macro_name = line[7:].strip()
            edit_macros[macro_name] = []
            continue
        elif line.strip() == ':endmacro':
            recording = False
            continue
        elif recording:
            edit_macros[macro_name].append(line)
            continue
        new_lines.append(line)
    with open(path, 'w') as f:
        f.write('\n'.join(new_lines))
    save_edit_macros(comm, edit_macros)
    print('Saved.')

def replay_macro(comm, macro_name, page_file):
    edit_macros = load_edit_macros(comm)
    if macro_name not in edit_macros:
        print("Macro not found.")
        return
    path = os.path.join(comm, page_file)
    lines = []
    if os.path.exists(path):
        lines = open(path).read().split('\n')
    for cmd in edit_macros[macro_name]:
        if cmd.startswith(':insert '):
            lines.append(cmd[8:].strip())
        elif cmd.startswith(':delete '):
            try:
                idx = int(cmd[8:].strip()) - 1
                if 0 <= idx < len(lines):
                    lines.pop(idx)
            except:
                continue
        elif cmd.startswith(':replace '):
            parts = cmd[9:].strip().split(' ', 1)
            if len(parts) == 2:
                try:
                    idx = int(parts[0]) - 1
                    if 0 <= idx < len(lines):
                        lines[idx] = parts[1]
                except:
                    continue
    with open(path, 'w') as f:
        f.write('\n'.join(lines))
    print(f'Macro "{macro_name}" applied to {page_file}.')

def view_page(comm):
    pages = list_pages(comm)
    if not pages:
        print("No pages available.")
        return
    print("Pages:")
    for i, p in enumerate(pages):
        print(f'{i+1}. {p}')
    choice = input("Select page to view (number or name): ").strip()
    if choice.isdigit() and int(choice)-1 < len(pages):
        page_file = pages[int(choice)-1]
    elif choice in pages:
        page_file = choice
    else:
        print("Page not found")
        return
    content_path = os.path.join(comm, page_file)
    content_lines = open(content_path).read().split('\n')
    # Automatically execute any @replay macros in the page
    for i, line in enumerate(content_lines):
        if line.startswith('@replay '):
            replay_macro(comm, line[8:].strip(), page_file)
    with open(content_path) as f:
        print(f'--- {page_file} ---')
        print(render_markdown(f.read()))

def export_posix(comm):
    meta = read_metadata(comm)
    filename = f'{comm[1:]}.sh'
    pages = list_pages(comm)
    with open(filename, 'w') as f:
        f.write('#!/bin/sh\n')
        f.write(f'echo "Community: {meta.get("Name","")}"\n')
        f.write(f'echo "Genre: {meta.get("Genre","")}"\n')
        f.write(f'echo "Description: {meta.get("Description","")}"\n')
        f.write(f'echo "Age Restriction: {meta.get("AgeRestriction","")}"\n')
        f.write('echo ""\n')
        f.write('echo "Pages:"\n')
        for i, p in enumerate(pages):
            f.write(f'echo "{i+1}. {p}"\n')
        f.write('read -p "Select page number: " pg\n')
        f.write('case $pg in\n')
        for i, p in enumerate(pages):
            f.write(f'{i+1}) echo "--- {p} ---"; cat .{comm[1:]}/{p} ;; \n')
        f.write('*) echo "Invalid selection";; esac\n')
    os.chmod(filename, 0o755)
    print(f'Exported interactive POSIX script: {filename}')

def manage_community():
    communities = load_communities()
    if not communities:
        print("No communities available.")
        return
    print("Communities:")
    for i, c in enumerate(communities):
        print(f'{i+1}. {c[1:]}')
    choice = input('Select community (number or name): ').strip()
    if choice.isdigit():
        idx = int(choice)-1
    else:
        names = [c[1:] for c in communities]
        if choice not in names:
            print("Community not found")
            return
        idx = names.index(choice)
    comm = communities[idx]
    while True:
        print('1. Edit Page\n2. Rename Page\n3. View Page\n4. Replay Macro\n5. Export POSIX\n6. Back')
        cmd = input('> ')
        if cmd == '1':
            edit_page(comm)
        elif cmd == '2':
            rename_page(comm)
        elif cmd == '3':
            view_page(comm)
        elif cmd == '4':
            pages = list_pages(comm)
            if not pages:
                print("No pages to apply macro.")
                continue
            for i, p in enumerate(pages):
                print(f'{i+1}. {p}')
            page_choice = input("Select page for macro: ").strip()
            if page_choice.isdigit() and int(page_choice)-1 < len(pages):
                page_file = pages[int(page_choice)-1]
            elif page_choice in pages:
                page_file = page_choice
            else:
                print("Page not found")
                continue
            macro_name = input("Enter macro name to replay: ").strip()
            replay_macro(comm, macro_name, page_file)
        elif cmd == '5':
            export_posix(comm)
        elif cmd == '6':
            break

def main():
    while True:
        clear()
        print(ansi('FireWiki Terminal', '1;31'))
        print('1. Create Community\n2. Delete Community\n3. Rename Community\n4. Manage Community\n5. Exit')
        choice = input('> ')
        if choice == '1':
            create_community()
        elif choice == '2':
            delete_community()
        elif choice == '3':
            rename_community()
        elif choice == '4':
            manage_community()
        elif choice == '5':
            sys.exit()

if __name__ == '__main__':
    main()
