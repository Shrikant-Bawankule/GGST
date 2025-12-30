def load_reference_from_single_file(ref_file_path, audio_filename):
    """
    ref_file_path: path to single reference.txt
    audio_filename: Hindi_0001.wav
    """

    # Read all lines
    with open(ref_file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Extract index from filename
    # Hindi_0001.wav -> 1 -> index 0
    index = int(audio_filename.split("_")[1].split(".")[0]) - 1

    return lines[index]
