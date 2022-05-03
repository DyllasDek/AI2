import music21
import random as rnd
from mido import Message, MidiFile, MidiTrack

input_file = 'barbiegirl_mono.mid'
#input_file = 'input1.mid'
pat = '_2.mid'

key = music21.converter.parse(input_file).analyze('key')
print(key)

# working tone index
wti = 0

count = 1536

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
t_maj = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]
t_min = [9, 4, 11, 6, 1, 8, 3, 10, 5, 0, 7, 2]
t_dim = [11, 6, 1, 8, 3, 10, 5, 0, 7, 2, 9, 4]

octave = - 1 * 12

if key.mode == "minor":
    wti = t_min.index(piano[key.tonic.name])
else:
    wti = t_maj.index(piano[key.tonic.name])

wti_dim = [t_dim[wti]]
wti_maj = []
wti_min = []
wti_test = []

if wti == 0:
    wti_maj = [t_maj[11], t_maj[0], t_maj[1]]
    wti_min = [t_min[11], t_min[0], t_min[1]]
    print(f"tone major are {t_maj[11]} , {t_maj[0]}, {t_maj[1]}")
    print(f"tone minor are {t_min[11]} , {t_min[0]}, {t_min[1]}")
elif wti == 11:
    wti_maj = [t_maj[10], t_maj[11], t_maj[0]]
    wti_min = [t_min[10], t_min[11], t_min[0]]
    print(f"tone major are {t_maj[10]} , {t_maj[11]}, {t_maj[0]}")
    print(f"tone minor are {t_min[10]} , {t_min[11]}, {t_min[0]}")
else:
    wti_maj = t_maj[wti - 1:wti + 2]
    wti_min = t_min[wti - 1:wti + 2]
    print(f"tone major are {t_maj[wti - 1]} , {t_maj[wti]}, {t_maj[wti + 1]}")
    print(f"tone minor are {t_min[wti - 1]} , {t_min[wti]}, {t_min[wti + 1]}")

maj_pat = [0, 4, 7]
min_pat = [0, 3, 7]
dim_pat = [0, 3, 6]

mid = MidiFile(input_file)
output_track = []

tick = 0
found = False

for msg in mid.tracks[1]:
    tick += msg.time
    if tick % count == 0 and tick // count > 0:
        found = False
    elif (tick - msg.time)//count < tick//count:
        print(f"Исключение {(tick - msg.time)//count} and {tick//count}")
        found = True
        print()
        print(msg.note)
        if (msg.note % 12) in wti_maj:
            output_track.append([msg.note + x + octave for x in maj_pat])
        elif (msg.note % 12) in wti_min:
            output_track.append([msg.note + x + octave for x in min_pat])
        elif (msg.note % 12) in wti_dim:
            output_track.append([msg.note + x + octave for x in dim_pat])
        else:
            '''
            output_track.append([msg.note + x + octave for x in min_pat])
            '''
            rand = rnd.randint(0, 2)
            if rand == 0:
                note = wti_maj[rnd.randint(0, 2)] + 60
                output_track.append([note + x + octave for x in maj_pat])
            elif rand == 1:
                note = wti_min[rnd.randint(0, 2)] + 60
                output_track.append([note + x + octave for x in min_pat])
            elif rand == 2:
                note = wti_dim[0] + 60
                output_track.append([note + x + octave for x in dim_pat])

    print(msg)
    if found:
        continue
    if msg.type != 'note_on':
        continue
    else:
        found = True
        print()
        print(msg.note)
        if (msg.note % 12) in wti_maj:
            output_track.append([msg.note + x + octave for x in maj_pat])
        elif (msg.note % 12) in wti_min:
            output_track.append([msg.note + x + octave for x in min_pat])
        elif (msg.note % 12) in wti_dim:
            output_track.append([msg.note + x + octave for x in dim_pat])
        else:
            rand = rnd.randint(0, 2)
            if rand == 0:
                note = wti_maj[rnd.randint(0, 2)] + 60
                output_track.append([note + x + octave for x in maj_pat])
            elif rand == 1:
                note = wti_min[rnd.randint(0, 2)] + 60
                output_track.append([note + x + octave for x in min_pat])
            elif rand == 2:
                note = wti_dim[0] + 60
                output_track.append([note + x + octave for x in dim_pat])

print(output_track)

track = MidiTrack()
mid.tracks.append(track)

track.append(mid.tracks[1][0])
track.append(mid.tracks[1][1])
for accord in output_track:
    track.append(Message('note_on', note=accord[0], velocity=50, time=0))
    track.append(Message('note_on', note=accord[1], velocity=50, time=0))
    track.append(Message('note_on', note=accord[2], velocity=50, time=0))
    track.append(Message('note_off', note=accord[0], velocity=50, time=count))
    track.append(Message('note_off', note=accord[1], velocity=50, time=0))
    track.append(Message('note_off', note=accord[2], velocity=50, time=0))

mid.save(input_file[:-4] + pat)
