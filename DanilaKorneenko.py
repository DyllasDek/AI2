import music21
from mido import MidiFile

input = 'barbiegirl_mono.mid'

score = music21.converter.parse(input)
key = score.analyze('key')
print(key.tonic.name, key.mode)


piano = {'C': 0,
         'C#': 1,
         'Db': 1,
         'D': 2,
         'D#': 3,
         'Db': 3,
         'E': 4,
         'F': 5,
         'F#': 6,
         'Gb': 6,
         'G': 7,
         'G#': 8,
         'Ab': 8,
         'A': 9,
         'A#': 10,
         'Bb': 10,
         'B': 11
}


if key.mode == 'minor':
    tone_minor = piano[key.tonic.name]
    tone_major = (piano[key.tonic.name] + 3) % 12
else:
    tone_major = piano[key.tonic.name]
    if piano[key.tonic.name] - 3 < 0:
        kek = 12 + (piano[key.tonic.name] - 3)
    tone_minor = kek


print(tone_minor)
print(tone_major)


mid = MidiFile(input)
for i, track in enumerate(mid.tracks):
    print('Track {}: {}'.format(i, track.name))
    for msg in track:
        print(msg)
