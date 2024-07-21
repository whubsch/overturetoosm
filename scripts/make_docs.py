"""Generate the docs."""

from pathlib import Path
import pdoc
import pdoc.render


here = Path(__file__).parent

pdoc.render.configure(
    docformat="google",
    footer_text="overturetoosm",
    favicon="../favicon.ico",
    logo="../logo.svg",
)
pdoc.pdoc("src/overturetoosm", output_directory=here.parent / "docs")
