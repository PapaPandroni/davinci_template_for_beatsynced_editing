import librosa

def timestamps_for_beats(file_path: str) -> list:
    """
    Calculates the bpm and converts beatframes to timestamps
    in the song where beat events are detected
    """
    try:
        y, sr = librosa.load(file_path) #open the song file
    except FileNotFoundError:
        exit("Not a valid file path")
    
    tempo, beatframes = librosa.beat.beat_track(y=y, sr=sr) #extracts beatframes where beat events are detected.
                                                            # also detects bpm, but it is not useful atm

    beat_times = librosa.frames_to_time(beatframes, sr=sr) #converts beatframes to beat times, time stamps in the song.

    print(f"The tempo is {tempo} bpm and timestamps have been calculated.")

    return beat_times


def main():
    file_path = input(f"Enter file path for a song: ")
    timestamps = timestamps_for_beats(file_path=file_path.strip("'").strip('"')) #must remove qutations from the strin for the filepath
    

if __name__ == "__main__":
    main()
