"""Generate the docs."""

from pathlib import Path
import pdoc
import pdoc.render


here = Path(__file__).parent

pdoc.render.configure(
    docformat="google",
    footer_text="overturetoosm",
)
pdoc.pdoc("src/overturetoosm/process", output_directory=here.parent / "html")
