import argparse
import openephys_to_dh
from openephys_to_dh import oe_to_dh
from pathlib import Path
from open_ephys.analysis.session import Session


def main():
    # oe-to-dh.exe --output-folder <output_folder> --config <config.json> --tdr <path_to_tdr_file> <oe-session>
    parser = argparse.ArgumentParser(
        description="Convert Open Ephys recordings to DH5 format."
    )

    parser.add_argument(
        "oe_session", type=str, help="Path to the Open Ephys session folder."
    )
    parser.add_argument(
        "--output-folder",
        type=str,
        default=None,
        help="Output folder for the DH5 file. Defaults to the parent folder of oe_session.",
    )

    parser.add_argument(
        "--config", type=str, help="Path to the configuration JSON file."
    )
    parser.add_argument("--tdr", type=str, help="Path to the TDR file.")

    args = parser.parse_args()

    oe_session_path = Path(args.oe_session)
    if not oe_session_path.exists():
        raise FileNotFoundError(
            f"Open Ephys session folder not found: {oe_session_path}"
        )

    session = Session(oe_session_path)
    recording = session.recordnodes[0].recordings[0]

    if args.output_folder is None:
        output_folder = oe_session_path.parent
    else:
        output_folder = Path(args.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    session_name = oe_session_path.name

    recording_index = 0
    for node in session.recordnodes:
        for recording in node.recordings:
            oe_to_dh(
                recording=recording,
                session_name=str(output_folder / session_name),
                recording_index=recording_index,
            )
            recording_index += 1


if __name__ == "__main__":
    main()
