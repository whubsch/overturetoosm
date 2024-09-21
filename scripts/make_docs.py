"""Generate the docs."""

from pathlib import Path
import pdoc
import pdoc.render

print("Generating docs...")
here = Path(__file__).parent

pdoc.render.configure(
    docformat="google",
    footer_text="overturetoosm",
    favicon="https://whubsch.github.io/overturetoosm/favicon.ico",
    logo="https://whubsch.github.io/overturetoosm/logo.svg",
)
pdoc.pdoc("src/overturetoosm", output_directory=here.parent / "docs")
print("Done!")
