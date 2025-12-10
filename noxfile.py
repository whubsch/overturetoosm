"""Testing file for nox.

# Run all tests
nox

# Run unit tests
nox -s tests

# Run integration tests for all data types
nox -s integration

# Run integration test for specific data type
nox -s "integration(data_type='place')"
nox -s "integration(data_type='building')"
nox -s "integration(data_type='address')"
"""

import os
import tempfile

import nox


@nox.session(python=["3.10", "3.11", "3.12", "3.13", "3.14"])
def tests(session):
    """Run tests with pytest across multiple Python versions."""
    session.install("pytest", "pydantic")
    session.install(".")
    session.run("python", "-m", "pytest")


@nox.session(python="3.12")
@nox.parametrize("data_type", ["place", "building", "address"])
def integration(session, data_type):
    """Run integration test mimicking GitHub Actions workflow.

    Downloads Overture data and processes it with overturetoosm.
    Uses a temporary directory that is cleaned up automatically.
    """
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as tmpdir:
        session.log(f"Running integration test for data_type: {data_type}")
        session.log(f"Using temporary directory: {tmpdir}")

        # Install dependencies
        session.log("Installing SSL certificates and dependencies...")
        session.install("certifi")

        session.log("Installing overturemaps package...")
        session.install("overturemaps")

        session.log("Installing local package dependencies...")
        session.install(".")

        # Set SSL certificate environment variable to use certifi
        # Get the certifi path from within the nox session
        certifi_path = session.run(
            "python", "-c", "import certifi; print(certifi.where())", silent=True
        ).strip()
        session.env["SSL_CERT_FILE"] = certifi_path
        session.env["REQUESTS_CA_BUNDLE"] = certifi_path
        session.log(f"Using SSL certificates from: {certifi_path}")

        # Download Overture data
        output_file = os.path.join(tmpdir, f"dc_{data_type}.geojson")
        session.log(f"Downloading Overture {data_type} data...")
        session.run(
            "overturemaps",
            "download",
            "--bbox=-77.028151,38.887626,-77.005835,38.898414",
            "-f",
            "geojson",
            f"--type={data_type}",
            "-o",
            output_file,
        )

        # Verify download
        session.log("Verifying download...")
        session.run("ls", "-la", output_file, external=True)
        session.run("head", "-n", "2", output_file, external=True)

        # Process with overturetoosm
        if data_type != "address":
            session.log(f"Processing {data_type} with confidence filter...")
            session.run(
                "python",
                "-m",
                "overturetoosm",
                data_type,
                "-i",
                output_file,
                "--in-place",
                "--confidence",
                "0.9",
            )
        else:
            session.log(f"Processing {data_type} without confidence filter...")
            session.run(
                "python",
                "-m",
                "overturetoosm",
                data_type,
                "-i",
                output_file,
                "--in-place",
            )

        # Verify processing
        session.log("Verifying processing...")
        session.log("Processed file contents (first 20 lines):")
        session.run("head", "-n", "20", output_file, external=True)

        session.log(f"✓ Integration test completed successfully for {data_type}")
        session.log("Temporary files will be cleaned up automatically")
