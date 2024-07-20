"""Generate the docs."""

from pathlib import Path
import pdoc
import pdoc.render


here = Path(__file__).parent

pdoc.render.configure(
    docformat="google",
    footer_text="overture-to-osm",
)
pdoc.pdoc("src/overture_to_osm/process", output_directory=here.parent / "html")
