import music21
import random as rnd
from mido import Message, MidiFile, MidiTrack

input_file = 'barbiegirl_mono.mid'
input_file = 'input3.mid'
pat = '_2.mid'

key = music21.converter.parse(input_file).analyze('key')
print(key)

# working tone index
wti = 0

final_chromo_note = []
final_chromo_chord = []

# Ticks or something, idk
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


def update_accord(note):
    if (note % 12) in wti_maj:
        output_track.append([note + x + octave for x in maj_pat])
        final_chromo_chord.append(0)
    elif (note % 12) in wti_min:
        output_track.append([note + x + octave for x in min_pat])
        final_chromo_chord.append(1)
    elif (note % 12) in wti_dim:
        output_track.append([note + x + octave for x in dim_pat])
        final_chromo_chord.append(2)
    else:
        rand = rnd.randint(0, 2)
        final_chromo_chord.append(rand)

        if rand == 0:
            N_note = wti_maj[rnd.randint(0, 2)] + (note // 12 * 12)
            output_track.append([N_note + x + octave for x in maj_pat])
        elif rand == 1:
            N_note = wti_min[rnd.randint(0, 2)] + (note // 12 * 12)
            output_track.append([N_note + x + octave for x in min_pat])
        elif rand == 2:
            N_note = wti_dim[0] + (msg.note // 12 * 12)
            output_track.append([N_note + x + octave for x in dim_pat])
    final_chromo_note.append(note + octave)


for msg in mid.tracks[1]:
    tick += msg.time
    if msg.time == count and msg.type == 'note_on':
        found = True
        print(f"Исключение 2:{msg.note}")

        output_track.append(None)
        final_chromo_note.append(None)
        final_chromo_chord.append(None)
        update_accord(msg.note)
        continue
    elif tick % count == 0 and tick // count > 0:
        found = False
    elif (tick - msg.time) // count < tick // count:
        print(f"Исключение {(tick - msg.time) // count} and {tick // count}")
        found = True
        update_accord(msg.note)
    if found:
        continue
    if msg.type != 'note_on':
        continue
    else:
        found = True
        update_accord(msg.note)

print(output_track)

track = MidiTrack()
mid.tracks.append(track)

print(final_chromo_note)
print(final_chromo_chord)

track.append(mid.tracks[1][0])
track.append(mid.tracks[1][1])

flagged = False
for accord in output_track:
    if accord == None:
        flagged = True
        continue
    if flagged:
        track.append(Message('note_on', note=accord[0], velocity=50, time=count))
        track.append(Message('note_on', note=accord[1], velocity=50, time=0))
        track.append(Message('note_on', note=accord[2], velocity=50, time=0))
        track.append(Message('note_off', note=accord[0], velocity=50, time=count))
        track.append(Message('note_off', note=accord[1], velocity=50, time=0))
        track.append(Message('note_off', note=accord[2], velocity=50, time=0))
        flagged = False
    else:
        track.append(Message('note_on', note=accord[0], velocity=50, time=0))
        track.append(Message('note_on', note=accord[1], velocity=50, time=0))
        track.append(Message('note_on', note=accord[2], velocity=50, time=0))
        track.append(Message('note_off', note=accord[0], velocity=50, time=count))
        track.append(Message('note_off', note=accord[1], velocity=50, time=0))
        track.append(Message('note_off', note=accord[2], velocity=50, time=0))

mid.save(input_file[:-4] + pat)

note_gen = [i for i in range(12)]
chord_gen = [i for i in range(3)]

pop_size = 20


class Chromo:
    def __init__(self, size, gene_p_n, gene_p_c):
        rate = 0
        for obj in final_chromo_chord:
            if obj is not None:
                rate += 2
        print(f"intial rate{rate}")

        self.rating = rate
        self.size = size
        self.gen_note = [[0 for _ in range(size)], [0 for _ in range(size)]]

        if gene_p_n is not None and gene_p_c is not None:
            self.set_rnd_note_chord()
            for i in range(size):
                if final_chromo_chord[i] is not None:
                    if self.gen_note[0][i] == final_chromo_note[i]:
                        self.rating -= 1
                    if self.gen_note[1][i] == final_chromo_chord[i]:
                        self.rating -= 1

    def set_rnd_note_chord(self):
        for i in range(len(final_chromo_note)):
            if final_chromo_note[i] is None:
                self.gen_note[0][i] = None
            else:
                self.gen_note[0][i] = rnd.choice(note_gen)

        for i in range(len(final_chromo_chord)):
            if final_chromo_chord[i] is None:
                self.gen_note[1][i] = None
            else:
                self.gen_note[1][i] = rnd.choice(chord_gen)


def create_pop(chromo_size):
    pop = [None] * pop_size
    for i in range(pop_size):
        pop[i] = Chromo(chromo_size, note_gen, chord_gen)
        #print(f"genom:{pop[i].gen_note} and rating {pop[i].rating}")
    return pop


def sort_pop(pop):
    size = len(pop)
    flag = True
    while flag:
        flag = False
        for i in range(0, size - 1):
            bub = pop[i]
            if (bub.rating > pop[i + 1].rating):
                pop[i] = pop[i + 1]
                pop[i + 1] = bub
                flag = True


def select():
    size = len(survivors)
    for i in range(size):
        survivors[i] = popul[i]





def get_p_i(parents, exclude_index):
    size = len(parents)
    while True:
        index = rnd.randint(0, size - 1)
        if exclude_index is None or exclude_index != index:
            return index


def cross(chromo1, chromo2):
    size = chromo1.size
    point = rnd.randint(0, size - 1)
    child = Chromo(size, None,None)
    for i in range(point):
        child.gen_note[0][i] = chromo1.gen_note[0][i]
        child.gen_note[1][i] = chromo1.gen_note[1][i]
    for i in range(point, size):
        child.gen_note[0][i] = chromo2.gen_note[0][i]
        child.gen_note[1][i] = chromo2.gen_note[1][i]


def repopulate(pop, par, children_count):
    while children_count < pop_size:
        p1_pos = get_p_i(par, None)
        p2_pos = get_p_i(par, p1_pos)
        p1 = par[p1_pos]
        p2 = par[p2_pos]
        pop[children_count] = cross(p1, p2)
        pop[children_count + 1] = cross(p2, p1)
        children_count += 2


def mutate(pop, chromo_c, gene_c):
    for i in range(chromo_c):
        chromo_pos = rnd.randint(0, pop_size - 1)
        chrom = pop[chromo_pos]
        for j in range(gene_c):
            gene_pos = rnd.randint(0, chrom.size - 1)
            chrom.gen_note[0][gene_pos] = rnd.choice(note_gen)
            chrom.gen_note[1][gene_pos] = rnd.choice(chord_gen)


def calc_rating(pop):
    for chromo in pop:
        rate = 0
        for obj in final_chromo_chord:
            if obj is not None:
                rate += 2
        chromo.rating = rate
        for i in range(chromo.size):
            if final_chromo_chord[i] is not None:
                if chromo.gen_note[0][i] == final_chromo_note[i]:
                    chromo.rating -= 1
                if chromo.gen_note[1][i] == final_chromo_chord[i]:
                    chromo.rating -= 1


popul = create_pop(len(final_chromo_chord))
survivors = [None] * (pop_size // 2)

for i in range(1,100):
    print(f"\n{i}")
    calc_rating(popul)
    sort_pop(popul)
    if popul[0].rating == 0:
        break
    select()
    repopulate(popul, survivors, pop_size // 2)
    mutate(popul, 10, 1)
print(f"genom:{popul[i].gen_note} and rating {popul[i].rating}")