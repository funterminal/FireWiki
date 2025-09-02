# FireWiki Terminal 🔥

A sophisticated, feature-rich terminal-based wiki and knowledge management system designed for developers, writers, and organized thinkers who prefer the power and efficiency of the command line.

![Python Version](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Platform Support](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-0078D6?logo=terminal&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-4DAF7C?logo=opensourceinitiative&logoColor=white)
![Version](https://img.shields.io/badge/Version-1.0.0-FF6B6B)
![Code Quality](https://img.shields.io/badge/Code%20Quality-Production%20Ready-27AE60)

## ✨ Overview

FireWiki Terminal revolutionizes knowledge management by bringing the power of modern wiki systems to your terminal. With robust community management, advanced macro capabilities, and beautiful ANSI-rendered content, it combines the efficiency of command-line tools with the organizational power of wiki systems.

## 🚀 Quick Installation

```bash
# One-command installation
wget https://raw.githubusercontent.com/funterminal/FireWiki/refs/heads/main/install.sh
chmod +x install.sh
./install.sh
```

## 📦 Manual Installation

```bash
# Clone the repository
git clone https://github.com/funterminal/FireWiki.git
cd FireWiki

# Run directly (no dependencies required)
python3 firewiki.py
```

### 🏆 Key Features

### Community-Centric Organization

· Multi-Community Support: Create and manage multiple independent wiki communities
· Rich Metadata: Comprehensive metadata system with genre classification, descriptions, and age restrictions
· Isolated Environments: Each community operates in its own namespace with separate configurations

### Advanced Content Management

· Real-time Markdown Rendering: Beautiful ANSI-colored previews while editing
· Macro Recording System: Record and replay complex editing sequences across pages
· Batch Operations: Apply macros and transformations to multiple pages simultaneously
· Intelligent Page Management: Easy creation, renaming, and organization of wiki pages

### Professional-Grade Editing

· Syntax-Aware Rendering: Intelligent parsing of markdown with semantic coloring
· Live Preview: See exactly how your content will appear while you type
· Macro Automation: Automate repetitive editing tasks with custom macros
· Cross-Platform Compatibility: Consistent experience across all major operating systems

### Export and Sharing

· POSIX Script Generation: Export entire communities as portable, interactive shell scripts
· Zero-Dependency Sharing: Share knowledge bases that run anywhere with just a shell
· Metadata Preservation: All community information is maintained in exports

🎨 Visual Design

FireWiki Terminal features a sophisticated ANSI color scheme designed for readability and aesthetic appeal:

· Headers: Hierarchical coloring (Blue → Cyan → Green) for clear information architecture
· Lists: Warm yellow bullets for easy scanning of enumerated content
· Quotes: Distinct magenta styling for highlighted content and references
· Code Blocks: Clean white background with proper formatting for technical content
· Macro Elements: Purple and cyan highlights for automated content features

## 📖 Comprehensive Usage Guide

Creating Your First Community

```bash
# Start FireWiki Terminal
python3 firewiki.py

# Select option 1: Create Community
Community Name: DeveloperNotes
Genre: Software Development
Description: Personal knowledge base for coding techniques and patterns
Age Restriction: [Optional - leave blank for no restrictions]
```

## Advanced Editing with Macros

FireWiki's macro system allows you to automate complex editing tasks:

```markdown
# Recording a formatting macro
:macro format_code_block
:insert ```python
:insert def example_function():
:insert     print("Hello, World!")
:insert ```
:endmacro

# Using the macro in content
@replay format_code_block
```

## Rich Content Creation

```markdown
# Main Header (Blue)
## Section Header (Cyan)
### Subsection Header (Green)

- Bullet point items (Yellow)
- Another list item

> Important quotations and notes (Magenta)
> Spanning multiple lines

`Inline code snippets (White)`

**Bold text** and *italicized content*

@macro dynamic_content  # Execute built-in macros
@replay saved_macro     # Replay recorded sequences
#tag important          # Content tagging system
```

## 🛠️ Macro Command Reference

Macro Recording Syntax

```
:macro macro_name        # Begin recording macro
:insert text             # Insert text at current position
:delete line_number      # Delete specific line
:replace line_number new_content  # Replace line content
:endmacro                # Finish recording
```

# Built-in Macros

· hello: Displays welcome message
· date: Shows current date information
· Custom macros can be defined per-community

## 📁 Project Structure

```
FireWiki/
├── firewiki.py          # Main application entry point
├── install.sh           # Installation script
├── .CommunityName/      # Community directories (hidden)
│   ├── _metadata.json   # Community metadata storage
│   ├── _edit_macros.json # Community-specific macros
│   ├── welcome.md       # Wiki content pages
│   └── documentation.md
└── README.md           # This documentation
```

## 🔧 Technical Architecture

File Format Specifications

· Metadata Storage: JSON-based metadata with extensible schema
· Content Storage: Standard markdown files with FireWiki extensions
· Macro Storage: JSON-serialized macro commands for portability

# ANSI Rendering Engine

· Custom markdown parser with semantic understanding
· Context-aware color application
· Macro execution and content generation system

# Cross-Platform Compatibility

· Automatic terminal detection and configuration
· Consistent behavior across Windows, macOS, and Linux
· No external dependencies beyond Python standard library

## 🌐 Export System

Generate fully functional, self-contained wiki viewers:

```bash
# From within FireWiki management
5. Export POSIX  # Creates CommunityName.sh

# Usage of exported script
./CommunityName.sh
# Presents interactive menu for browsing content
```

## 📊 Performance Characteristics

· Instant Startup: No compilation or heavy initialization
· Efficient Memory Usage: Minimal footprint even with large knowledge bases
· Fast Rendering: Optimized ANSI code generation for smooth scrolling
· Scalable Design: Handles hundreds of pages and communities efficiently

## 🤝 Contributing to FireWiki

We welcome contributions from the community! Here's how you can help:

1. Report Issues: Found a bug? Let us know on GitHub Issues
2. Suggest Features: Have ideas for improvements? Submit feature requests
3. Submit Pull Requests: Implement new features or fix existing issues
4. Improve Documentation: Help make FireWiki more accessible to new users

# Development Setup

```bash
git clone https://github.com/funterminal/FireWiki.git
cd FireWiki
# Start hacking - no complex build system required!
```

## 📚 Learning Resources

· GitHub Wiki: Comprehensive documentation and tutorials
· Example Communities: Sample knowledge bases to learn from
· Community Forum: Connect with other FireWiki users
· Video Tutorials: Step-by-step guidance on advanced features

## 🏢 Enterprise Features

· Access Control: Age-based content restrictions
· Content Portability: Easy migration between instances
· Audit Logging: Track changes and macro usage
· Team Collaboration: Shared community management

## 📄 License Information

FireWiki Terminal is released under the MIT License, allowing both personal and commercial use with minimal restrictions. See the `LICENSE` file for complete details.

## 🌍 Community and Support

· Official Repository: https://github.com/funterminal/FireWiki.git
· Issue Tracker: https://github.com/funterminal/FireWiki/issues
· Documentation: https://github.com/funterminal/FireWiki/wiki
· Discussion Forum: https://github.com/funterminal/FireWiki/discussions

🙏 Acknowledgments

FireWiki Terminal builds upon decades of terminal application development, markdown standardization, and knowledge management best practices. Special thanks to the open-source community for inspiration and guidance.

---

**FireWiki Terminal 🔥** - Where knowledge meets the power of the command line. Transform how you organize, access, and share information with the ultimate terminal-based wiki solution.

Empowering developers, writers, and thinkers to build better knowledge systems, one command at a time.