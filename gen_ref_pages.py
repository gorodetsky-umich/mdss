"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

package_name = "simulateTestCases"
root = Path(__file__).parent.parent
src = root/package_name

modules_to_skip = [
    "templates", 
    "yaml_config"
]

for path in sorted(src.rglob("*.py")):

    module_path = path.relative_to(src).with_suffix("")  # Path object
    module_name = ".".join(module_path.parts)  # Convert to dotted module name
    doc_path = path.relative_to(src).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    # Skip modules and folders
    if any(module_name.startswith(skip) for skip in modules_to_skip):
        print(f"Skipping module or folder: {module_name}")
        continue

    parts = tuple(module_path.parts)

    # Debugging output
    print(f"Processing file: {path}")
    print(f"Module path: {module_path}")
    print(f"Doc path: {doc_path}")
    print(f"Parts: {parts}")

    # Skip empty parts or adjust for __init__.py
    if not parts or not parts[-1]:  # Empty parts check
        print(f"Skipping file with empty parts: {path}")
        continue

    if parts[-1] == "__init__":
        parts = parts[:-1]  # Drop '__init__' from parts
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")

    elif parts[-1] == "__main__":
        # Skip __main__.py files as they are typically entry points
        print(f"Skipping __main__ file: {path}")
        continue

    try:
        nav[parts] = doc_path.as_posix()
    except ValueError as e:
        print(f"Navigation error for file {path}: {e}")
        continue

    # Generate Markdown for documentation
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"# {ident}\n\n")
        fd.write(f"::: {ident}\n")
        fd.write("\n---\n")

    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

# Generate navigation file
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    navigation = nav.build_literate_nav()
    print(f"Generated Navigation:\n{navigation}")
    nav_file.writelines(navigation)

