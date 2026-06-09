import librosa

# ── RESOLVE CONNECTION ────────────────────────────────────────────────────────

def connect_to_resolve():
    """Connect to a running Resolve instance. Works both inside and outside the console."""
    # External (terminal): DaVinciResolveScript is on PYTHONPATH
    try:
        import DaVinciResolveScript as dvr
        resolve = dvr.scriptapp("Resolve")
        if resolve:
            return resolve
    except ImportError:
        pass

    # Internal (Workspace -> Scripts / Console): bmd is a Resolve builtin,
    # not an importable module -- reference it directly and catch NameError.
    try:
        resolve = bmd.scriptapp("Resolve")  # noqa: F821
        if resolve:
            return resolve
    except NameError:
        pass

    raise RuntimeError("Could not connect to DaVinci Resolve -- make sure it is running.")


def create_timeline (resolve, audio_file: str, black_video: str): #you need to pass a resolve object
    #First part creates the timeline.
    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()
    media_pool = project.GetMediaPool()
    media_pool.CreateEmptyTimeline("Beatsync") 
    
    #This part imports the music and black video
    media_pool.ImportMedia([audio_file, black_video])


    #This part adds (the black video and) the music to the timeline
    """ 
    I noticed when creating the timeline that it is easier to 
    have the black placeholder video in the media pool and create 
    in/outs and place many smaller clips on the timeline, instead of
    adding the video to the timeline and then cut it up according to timestamps
    """
    root = media_pool.GetRootFolder()
    clip_list = root.GetClipList()
    #media_pool.AppendToTimeline(clip_list[1]) #the timeline is the first ([0]) object, this is black video

    #This is needed so the music isnt added at the end of the video
    """
    Might not be needed anymore, but it's very explicit and robust
    """
    audio_clip_info = {
        "mediaPoolItem": clip_list[2],
        "startFrame": 0,
        "trackIndex": 1,
        "mediaType": 2  # 2 = audio
    }

    media_pool.AppendToTimeline([audio_clip_info])

def add_cuts(resolve, beat_times):

    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()
    media_pool = project.GetMediaPool()
    timeline = project.GetCurrentTimeline()
    fps = float(timeline.GetSetting("timelineFrameRate"))

    root = media_pool.GetRootFolder()
    clip_list = root.GetClipList()
    black_video = clip_list[1] #the timeline is the first ([0]) object, this is the black placeholder video

    offset = timeline.GetStartFrame() #needed to do floating point maths. the timeline starts at 1hour instead of 00:00:00:00

    #print(f"offset is {offset}") debug

    """
    If the first beat isnt detected at the start of the music. Like if there is an intro or
    silence at the start. We need to place a longer placeholder video at the beginning to get the timing right.
    The timing we get from the first timestamp from the beat detection in librosa.
    """
    intro_clip_info = {
    "mediaPoolItem": black_video,
    "startFrame": 0,
    "endFrame": int(beat_times[0] * fps),
    "mediaType": 1,
    "trackIndex": 1
    }
    media_pool.AppendToTimeline([intro_clip_info])

    """
    Generate clips for every 4th beat. 
    """
    for i in range(0, len(beat_times) - 4, 4):
        start_frame = int(beat_times[i] * fps)
        end_frame = int(beat_times[i + 4] * fps)

        clip_info = {
            "mediaPoolItem": black_video,
            "startFrame": start_frame,
            "endFrame": end_frame,
            "mediaType": 1,
            "trackIndex": 1
        }
        media_pool.AppendToTimeline([clip_info])

def timestamps_for_beats(file_path: str) -> list:
    """
    Calculates the bpm and converts beatframes to timestamps
    in the song where beat events are detected
    """
    try:
        y, sr = librosa.load(file_path) #open the song file
    except FileNotFoundError:
        exit("Not a valid file path")
     
    """
    extracts beatframes where beat events are detected.
    also detects bpm, but it is not useful atm
    """
    tempo, beatframes = librosa.beat.beat_track(y=y, sr=sr) 

    beat_times = librosa.frames_to_time(beatframes, sr=sr) #converts beatframes to beat times, time stamps in the song.

    print(f"The tempo is {tempo} bpm and timestamps have been calculated.")
    #print(beat_times)
    print(f"First beat: {beat_times[0]}, frames: {int(beat_times[0] * 25)}")

    return beat_times


def main():
    audio_file = input(f"Enter file path for a song: ")
    black_video = input("Enter filepath for black video: ")

    timestamps = timestamps_for_beats(file_path=audio_file.strip("'").strip('"')) #must remove qutations from the string for the filepath

    resolve = connect_to_resolve()

    create_timeline(resolve, audio_file.strip("'").strip('"'), black_video.strip("'").strip('"'))

    add_cuts(resolve, timestamps)


if __name__ == "__main__":
    main()
