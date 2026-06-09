# DaVinci Resolve Beat-Synced Editing Template

A Python script that automatically builds a beat-synced edit template in DaVinci Resolve. It analyzes a music track, detects beats using librosa, and populates a timeline with placeholder clips cut on every 4th beat — ready for you to swap in your actual footage.

## The Idea

Manually cutting a highlight reel to music is tedious. This script does the structural work for you:

1. Analyze the audio track and detect beat timestamps with librosa
2. Build a DaVinci Resolve timeline with a black placeholder video cut into beat-interval clips
3. Use DaVinci's built-in **Replace Clip** to swap each placeholder with your actual footage

The result is a beat-synced edit structure without touching the timeline manually.

## How It Works

### Beat Detection — `timestamps_for_beats`
The audio file is loaded with [librosa](https://librosa.org/) and analyzed with its beat tracker. This produces *librosa frames* — short fixed-length audio analysis windows (~23ms each) that are completely unrelated to video frames. These are converted to real timestamps in seconds via `librosa.frames_to_time`. The script then cuts on every 4th beat, corresponding to the downbeat of each bar, giving one clip per bar rather than one per individual beat.

> librosa's beat tracker finds beats but has no concept of bar boundaries. If cuts feel off by one or two beats, adjust the start offset in the `range()` call inside `add_cuts`.

### Timeline Creation — `create_timeline`
The script connects to a running DaVinci Resolve instance via its scripting API, creates a new timeline called *Beatsync*, and imports both the audio file and the black placeholder video into the media pool. The audio is placed on A1 using an explicit `clipInfo` dict with `mediaType: 2`.

> Using a bare `AppendToTimeline(clip)` call ignores track placement entirely — you must pass a `clipInfo` dict to control which track a clip lands on.

### Cutting the Timeline — `add_cuts`
Beat timestamps (seconds) are converted to frames by multiplying by the project FPS. The placeholder video is sliced into beat-interval clips by passing `startFrame`/`endFrame` source in/out points in the `clipInfo` dict to `AppendToTimeline`. An intro clip is added first to cover any silence before the first detected beat.

A few things worth knowing about the Resolve API here:

- **`startFrame`/`endFrame` in `clipInfo` are source in/out points** within the media file, not positions on the timeline. `AppendToTimeline` always places clips sequentially from the current end of the track — timeline position is not directly controllable via this method.
- **Resolve's default timeline start is `1:00:00:00`** (a broadcast convention), not `00:00:00:00`. `timeline.GetStartFrame()` returns this offset (90000 frames at 25fps). This only matters if you need absolute timeline frame references — `AppendToTimeline` handles placement automatically and doesn't require it.
- **The placeholder video must match the timeline framerate.** A mismatch causes Resolve to silently reinterpret source frame counts in the wrong timebase, producing clips of the wrong length.

## Requirements

- DaVinci Resolve 18+ (free or Studio) running on the same machine
- Python installed from [python.org](https://www.python.org/downloads/) — Resolve requires the official framework installation at `/Library/Frameworks/Python.framework/` and will not find Homebrew or system Python
- [uv](https://github.com/astral-sh/uv) for dependency management
- A black placeholder video matching your target framerate — `Placeholder.mp4` (25fps) is included in the repo

## Setup

```bash
git clone https://github.com/PapaPandroni/davinci_template_for_beatsynced_editing
cd davinci_template_for_beatsynced_editing
uv sync
```

## Usage

1. Open DaVinci Resolve with a project open
2. Run from the terminal while Resolve is open:

```bash
uv run main.py
```

3. Enter file paths to a music file and a placeholder media.

The script creates a *Beatsync* timeline in your current project, analyzes the audio, and populates it with beat-synced placeholder clips.

4. In DaVinci Resolve, right-click any placeholder clip and use **Replace Clip** to swap it with your footage.

## Roadmap

- [ ] Native UI inside DaVinci Resolve (via the Resolve scripting UI API)

**THIS README IS CO-WRITTEN WITH AI**
