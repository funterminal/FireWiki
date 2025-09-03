import os
import sys
import shutil
import json
import hashlib
from datetime import datetime
import readchar

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
    if not os.path.exists(os.path.join(folder, '_versions')):
        os.mkdir(os.path.join(folder, '_versions'))

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
    return [f for f in os.listdir(comm) if f.endswith('.md') and not f.startswith('_')]

def render_markdown(content):
    lines = content.split('\n')
    rendered = []
    in_code_block = False
    in_list = False
    
    for line in lines:
        # Handle code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                rendered.append(ansi(line, '0;37;40'))  # White on black for code blocks
            else:
                rendered.append(ansi(line, '0;37;40'))
            continue
        
        if in_code_block:
            rendered.append(ansi(line, '0;37;40'))
            continue
            
        # Handle headers
        if line.startswith('# '):
            rendered.append(ansi(line[2:], '1;34'))  # Bold blue for H1
        elif line.startswith('## '):
            rendered.append(ansi(line[3:], '1;36'))  # Bold cyan for H2
        elif line.startswith('### '):
            rendered.append(ansi(line[4:], '1;32'))  # Bold green for H3
        # Handle lists
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                in_list = True
            bullet = '• ' if line.startswith('- ') else '◦ '
            rendered.append(ansi(bullet + line[2:], '0;33'))  # Yellow for list items
        elif line.startswith('> '):
            rendered.append(ansi(line, '0;35'))  # Magenta for blockquotes
        # Handle inline code
        elif '`' in line:
            parts = line.split('`')
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Odd parts are inside backticks
                    rendered_part = ansi(part, '0;37;40')  # White on black for inline code
                else:
                    # Handle bold and italic in text
                    part = part.replace('**', '\033[1m').replace('*', '\033[3m') + '\033[0m'
                    rendered_part = part
                if i > 0:
                    rendered[-1] += rendered_part
                else:
                    rendered.append(rendered_part)
        # Handle macros and special tags
        elif line.startswith('@macro '):
            macro_name = line[7:].strip()
            rendered.append(ansi(f'[Macro: {macro_name}]', '1;35'))
            if macro_name in macros:
                macros[macro_name]()
        elif line.startswith('@replay '):
            rendered.append(ansi(f'[Edit Macro: {line[8:]}]', '1;36'))
        elif line.startswith('#tag '):
            rendered.append(ansi(f'[Tag: {line[5:]}]', '1;33'))
        # Handle horizontal rules
        elif line.strip() in ('---', '***', '___'):
            rendered.append(ansi('─' * 40, '0;36'))  # Cyan horizontal rule
        # Handle regular text with formatting
        else:
            if line.strip() == '' and in_list:
                in_list = False
            # Handle bold and italic text
            formatted_line = line.replace('**', '\033[1m').replace('*', '\033[3m') + '\033[0m'
            rendered.append(formatted_line)
    
    return '\n'.join(rendered)

def create_version(comm, page_file, content, operation):
    version_dir = os.path.join(comm, '_versions', page_file)
    if not os.path.exists(version_dir):
        os.makedirs(version_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    version_file = os.path.join(version_dir, f"{timestamp}_{content_hash}_{operation}.md")

    with open(version_file, 'w') as f:
        f.write(content)

    version_log = os.path.join(comm, '_versions', '_version_log.json')
    if os.path.exists(version_log):
        log_data = json.load(open(version_log))
    else:
        log_data = {}

    if page_file not in log_data:
        log_data[page_file] = []

    log_data[page_file].append({
        'timestamp': timestamp,
        'hash': content_hash,
        'operation': operation,
        'version_file': f"{timestamp}_{content_hash}_{operation}.md"
    })

    with open(version_log, 'w') as f:
        json.dump(log_data, f, indent=2)

def get_page_info(comm, page_file):
    info = {
        'name': page_file,
        'size': os.path.getsize(os.path.join(comm, page_file)),
        'created': datetime.fromtimestamp(os.path.getctime(os.path.join(comm, page_file))).strftime("%Y-%m-%d %H:%M:%S"),
        'modified': datetime.fromtimestamp(os.path.getmtime(os.path.join(comm, page_file))).strftime("%Y-%m-%d %H:%M:%S"),
        'versions': 0
    }

    version_log = os.path.join(comm, '_versions', '_version_log.json')
    if os.path.exists(version_log):
        log_data = json.load(open(version_log))
        if page_file in log_data:
            info['versions'] = len(log_data[page_file])
            info['last_version'] = log_data[page_file][-1]['timestamp'] if log_data[page_file] else 'None'

    return info

def show_page_info(comm, page_file):
    info = get_page_info(comm, page_file)
    print(f"\nPage Information: {info['name']}")
    print(f"Size: {info['size']} bytes")
    print(f"Created: {info['created']}")
    print(f"Last Modified: {info['modified']}")
    print(f"Version History: {info['versions']} saved versions")
    if info['versions'] > 0:
        print(f"Last Version: {info['last_version']}")

def view_version_history(comm, page_file):
    version_log = os.path.join(comm, '_versions', '_version_log.json')
    if not os.path.exists(version_log):
        print("No version history available.")
        return

    log_data = json.load(open(version_log))
    if page_file not in log_data or not log_data[page_file]:
        print("No version history for this page.")
        return

    print(f"\nVersion History for {page_file}:")
    for i, version in enumerate(reversed(log_data[page_file])):
        print(f"{i+1}. {version['timestamp']} - {version['operation']} - Hash: {version['hash']}")

def restore_version(comm, page_file):
    version_log = os.path.join(comm, '_versions', '_version_log.json')
    if not os.path.exists(version_log):
        print("No version history available.")
        return

    log_data = json.load(open(version_log))
    if page_file not in log_data or not log_data[page_file]:
        print("No version history for this page.")
        return

    view_version_history(comm, page_file)
    try:
        choice = int(input("\nSelect version to restore (number): "))
        if choice < 1 or choice > len(log_data[page_file]):
            print("Invalid selection.")
            return

        version = list(reversed(log_data[page_file]))[choice-1]
        version_path = os.path.join(comm, '_versions', page_file, version['version_file'])

        if os.path.exists(version_path):
            with open(version_path, 'r') as f:
                content = f.read()

            current_path = os.path.join(comm, page_file)
            with open(current_path, 'w') as f:
                f.write(content)

            create_version(comm, page_file, content, 'restored')
            print(f"Version {version['timestamp']} restored successfully.")
        else:
            print("Version file not found.")
    except ValueError:
        print("Invalid input.")

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

    old_path = os.path.join(comm, old_name)
    new_path = os.path.join(comm, new_name)

    if os.path.exists(old_path):
        with open(old_path, 'r') as f:
            content = f.read()
        create_version(comm, old_name, content, 'rename_old')

    os.rename(old_path, new_path)

    if os.path.exists(new_path):
        with open(new_path, 'r') as f:
            content = f.read()
        create_version(comm, new_name, content, 'rename_new')

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
        create_version(comm, filename, content, 'edit_pre')
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
    new_content = '\n'.join(new_lines)
    with open(path, 'w') as f:
        f.write(new_content)
    create_version(comm, filename, new_content, 'edit_post')
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
        with open(path) as f:
            content = f.read()
        lines = content.split('\n')
        create_version(comm, page_file, content, 'macro_pre')

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

    new_content = '\n'.join(lines)
    with open(path, 'w') as f:
        f.write(new_content)
    create_version(comm, page_file, new_content, 'macro_post')
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
    for line in open(content_path).read().split('\n'):
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
    
    # Vim-style navigation for community management
    print("\nVim-style navigation: j/k to navigate, Enter to select, q to go back")
    options = [
        "Edit Page (e)",
        "Rename Page (r)",
        "View Page (v)",
        "Page Information (i)",
        "Version History (h)",
        "Restore Version (R)",
        "Replay Macro (m)",
        "Export POSIX (x)",
        "Back (q)"
    ]
    
    current_selection = 0
    while True:
        clear()
        print(f"Managing Community: {comm[1:]}")
        print("Select an option:")
        for i, option in enumerate(options):
            prefix = "> " if i == current_selection else "  "
            print(f"{prefix}{option}")
        
        key = readchar.readkey()
        
        if key == 'j' or key == '\x1b[B':  # Down arrow or j
            current_selection = min(current_selection + 1, len(options) - 1)
        elif key == 'k' or key == '\x1b[A':  # Up arrow or k
            current_selection = max(current_selection - 1, 0)
        elif key == '\r' or key == '\n':  # Enter
            if current_selection == 0:  # Edit Page
                edit_page(comm)
                input("Press any key to continue...")
            elif current_selection == 1:  # Rename Page
                rename_page(comm)
                input("Press any key to continue...")
            elif current_selection == 2:  # View Page
                view_page(comm)
                input("Press any key to continue...")
            elif current_selection == 3:  # Page Information
                pages = list_pages(comm)
                if not pages:
                    print("No pages available.")
                    input("Press any key to continue...")
                    continue
                
                # Vim-style page selection
                page_selection = 0
                while True:
                    clear()
                    print("Select a page for information:")
                    for i, p in enumerate(pages):
                        prefix = "> " if i == page_selection else "  "
                        print(f"{prefix}{i+1}. {p}")
                    print("\nNavigation: j/k to navigate, Enter to select, q to go back")
                    
                    key2 = readchar.readkey()
                    if key2 == 'j' or key2 == '\x1b[B':
                        page_selection = min(page_selection + 1, len(pages) - 1)
                    elif key2 == 'k' or key2 == '\x1b[A':
                        page_selection = max(page_selection - 1, 0)
                    elif key2 == '\r' or key2 == '\n':
                        page_file = pages[page_selection]
                        show_page_info(comm, page_file)
                        input("Press any key to continue...")
                        break
                    elif key2 == 'q':
                        break
            elif current_selection == 4:  # Version History
                pages = list_pages(comm)
                if not pages:
                    print("No pages available.")
                    input("Press any key to continue...")
                    continue
                
                # Vim-style page selection
                page_selection = 0
                while True:
                    clear()
                    print("Select a page for version history:")
                    for i, p in enumerate(pages):
                        prefix = "> " if i == page_selection else "  "
                        print(f"{prefix}{i+1}. {p}")
                    print("\nNavigation: j/k to navigate, Enter to select, q to go back")
                    
                    key2 = readchar.readkey()
                    if key2 == 'j' or key2 == '\x1b[B':
                        page_selection = min(page_selection + 1, len(pages) - 1)
                    elif key2 == 'k' or key2 == '\x1b[A':
                        page_selection = max(page_selection - 1, 0)
                    elif key2 == '\r' or key2 == '\n':
                        page_file = pages[page_selection]
                        view_version_history(comm, page_file)
                        input("Press any key to continue...")
                        break
                    elif key2 == 'q':
                        break
            elif current_selection == 5:  # Restore Version
                pages = list_pages(comm)
                if not pages:
                    print("No pages available.")
                    input("Press any key to continue...")
                    continue
                
                # Vim-style page selection
                page_selection = 0
                while True:
                    clear()
                    print("Select a page to restore version:")
                    for i, p in enumerate(pages):
                        prefix = "> " if i == page_selection else "  "
                        print(f"{prefix}{i+1}. {p}")
                    print("\nNavigation: j/k to navigate, Enter to select, q to go back")
                    
                    key2 = readchar.readkey()
                    if key2 == 'j' or key2 == '\x1b[B':
                        page_selection = min(page_selection + 1, len(pages) - 1)
                    elif key2 == 'k' or key2 == '\x1b[A':
                        page_selection = max(page_selection - 1, 0)
                    elif key2 == '\r' or key2 == '\n':
                        page_file = pages[page_selection]
                        restore_version(comm, page_file)
                        input("Press any key to continue...")
                        break
                    elif key2 == 'q':
                        break
            elif current_selection == 6:  # Replay Macro
                pages = list_pages(comm)
                if not pages:
                    print("No pages to apply macro.")
                    input("Press any key to continue...")
                    continue
                
                # Vim-style page selection
                page_selection = 0
                while True:
                    clear()
                    print("Select a page for macro:")
                    for i, p in enumerate(pages):
                        prefix = "> " if i == page_selection else "  "
                        print(f"{prefix}{i+1}. {p}")
                    print("\nNavigation: j/k to navigate, Enter to select, q to go back")
                    
                    key2 = readchar.readkey()
                    if key2 == 'j' or key2 == '\x1b[B':
                        page_selection = min(page_selection + 1, len(pages) - 1)
                    elif key2 == 'k' or key2 == '\x1b[A':
                        page_selection = max(page_selection - 1, 0)
                    elif key2 == '\r' or key2 == '\n':
                        page_file = pages[page_selection]
                        macro_name = input("Enter macro name to replay: ").strip()
                        replay_macro(comm, macro_name, page_file)
                        input("Press any key to continue...")
                        break
                    elif key2 == 'q':
                        break
            elif current_selection == 7:  # Export POSIX
                export_posix(comm)
                input("Press any key to continue...")
            elif current_selection == 8:  # Back
                break
        elif key == 'q':  # Quit
            break
        elif key == 'e':  # Quick key for Edit Page
            edit_page(comm)
            input("Press any key to continue...")
        elif key == 'r':  # Quick key for Rename Page
            rename_page(comm)
            input("Press any key to continue...")
        elif key == 'v':  # Quick key for View Page
            view_page(comm)
            input("Press any key to continue...")
        elif key == 'i':  # Quick key for Page Information
            pages = list_pages(comm)
            if not pages:
                print("No pages available.")
                input("Press any key to continue...")
                continue
            
            # Vim-style page selection
            page_selection = 0
            while True:
                clear()
                print("Select a page for information:")
                for i, p in enumerate(pages):
                    prefix = "> " if i == page_selection else "  "
                    print(f"{prefix}{i+1}. {p}")
                print("\nNavigation: j/k to navigate, Enter to select, q to go back")
                
                key2 = readchar.readkey()
                if key2 == 'j' or key2 == '\x1b[B':
                    page_selection = min(page_selection + 1, len(pages) - 1)
                elif key2 == 'k' or key2 == '\x1b[A':
                    page_selection = max(page_selection - 1, 0)
                elif key2 == '\r' or key2 == '\n':
                    page_file = pages[page_selection]
                    show_page_info(comm, page_file)
                    input("Press any key to continue...")
                    break
                elif key2 == 'q':
                    break
        elif key == 'h':  # Quick key for Version History
            pages = list_pages(comm)
            if not pages:
                print("No pages available.")
                input("Press any key to continue...")
                continue
            
            # Vim-style page selection
            page_selection = 0
            while True:
                clear()
                print("Select a page for version history:")
                for i, p in enumerate(pages):
                    prefix = "> " if i == page_selection else "  "
                    print(f"{prefix}{i+1}. {p}")
                print("\nNavigation: j/k to navigate, Enter to select, q to go back")
                
                key2 = readchar.readkey()
                if key2 == 'j' or key2 == '\x1b[B':
                    page_selection = min(page_selection + 1, len(pages) - 1)
                elif key2 == 'k' or key2 == '\x1b[A':
                    page_selection = max(page_selection - 1, 0)
                elif key2 == '\r' or key2 == '\n':
                    page_file = pages[page_selection]
                    view_version_history(comm, page_file)
                    input("Press any key to continue...")
                    break
                elif key2 == 'q':
                    break
        elif key == 'R':  # Quick key for Restore Version
            pages = list_pages(comm)
            if not pages:
                print("No pages available.")
                input("Press any key to continue...")
                continue
            
            # Vim-style page selection
            page_selection = 0
            while True:
                clear()
                print("Select a page to restore version:")
                for i, p in enumerate(pages):
                    prefix = "> " if i == page_selection else "  "
                    print(f"{prefix}{i+1}. {p}")
                print("\nNavigation: j/k to navigate, Enter to select, q to go back")
                
                key2 = readchar.readkey()
                if key2 == 'j' or key2 == '\x1b[B':
                    page_selection = min(page_selection + 1, len(pages) - 1)
                elif key2 == 'k' or key2 == '\x1b[A':
                    page_selection = max(page_selection - 1, 0)
                elif key2 == '\r' or key2 == '\n':
                    page_file = pages[page_selection]
                    restore_version(comm, page_file)
                    input("Press any key to continue...")
                    break
                elif key2 == 'q':
                    break
        elif key == 'm':  # Quick key for Replay Macro
            pages = list_pages(comm)
            if not pages:
                print("No pages to apply macro.")
                input("Press any key to continue...")
                continue
            
            # Vim-style page selection
            page_selection = 0
            while True:
                clear()
                print("Select a page for macro:")
                for i, p in enumerate(pages):
                    prefix = "> " if i == page_selection else "  "
                    print(f"{prefix}{i+1}. {p}")
                print("\nNavigation: j/k to navigate, Enter to select, q to go back")
                
                key2 = readchar.readkey()
                if key2 == 'j' or key2 == '\x1b[B':
                    page_selection = min(page_selection + 1, len(pages) - 1)
                elif key2 == 'k' or key2 == '\x1b[A':
                    page_selection = max(page_selection - 1, 0)
                elif key2 == '\r' or key2 == '\n':
                    page_file = pages[page_selection]
                    macro_name = input("Enter macro name to replay: ").strip()
                    replay_macro(comm, macro_name, page_file)
                    input("Press any key to continue...")
                    break
                elif key2 == 'q':
                    break
        elif key == 'x':  # Quick key for Export POSIX
            export_posix(comm)
            input("Press any key to continue...")

def main():
    while True:
        clear()
        print(ansi('FireWiki Terminal', '1;31'))
        print("Vim-style navigation: j/k to navigate, Enter to select, q to quit")
        
        options = [
            "Create Community (c)",
            "Delete Community (d)",
            "Rename Community (r)",
            "Manage Community (m)",
            "Exit (q)"
        ]
        
        current_selection = 0
        
        while True:
            clear()
            print(ansi('FireWiki Terminal', '1;31'))
            print("Select an option:")
            for i, option in enumerate(options):
                prefix = "> " if i == current_selection else "  "
                print(f"{prefix}{option}")
            
            key = readchar.readkey()
            
            if key == 'j' or key == '\x1b[B':  # Down arrow or j
                current_selection = min(current_selection + 1, len(options) - 1)
            elif key == 'k' or key == '\x1b[A':  # Up arrow or k
                current_selection = max(current_selection - 1, 0)
            elif key == '\r' or key == '\n':  # Enter
                if current_selection == 0:  # Create Community
                    create_community()
                    input("Press any key to continue...")
                    break
                elif current_selection == 1:  # Delete Community
                    delete_community()
                    input("Press any key to continue...")
                    break
                elif current_selection == 2:  # Rename Community
                    rename_community()
                    input("Press any key to continue...")
                    break
                elif current_selection == 3:  # Manage Community
                    manage_community()
                    break
                elif current_selection == 4:  # Exit
                    sys.exit()
            elif key == 'q':  # Quit
                sys.exit()
            elif key == 'c':  # Quick key for Create Community
                create_community()
                input("Press any key to continue...")
                break
            elif key == 'd':  # Quick key for Delete Community
                delete_community()
                input("Press any key to continue...")
                break
            elif key == 'r':  # Quick key for Rename Community
                rename_community()
                input("Press any key to continue...")
                break
            elif key == 'm':  # Quick key for Manage Community
                manage_community()
                break

if __name__ == '__main__':
    main()
