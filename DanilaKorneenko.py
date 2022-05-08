import music21
import random as rnd
from mido import Message, MidiFile, MidiTrack

# Variables for files
input_file = 'input1.mid'
mid = MidiFile(input_file)
pat = 'DanilaKorneenkoOutput'+str(1)+'.mid'
vel = int(mid.tracks[1][4].velocity) - 20

# Variables for evalutionary algorithm
note_gen = [i for i in range(12)]
chord_gen = [i for i in range(3)]
pop_size = 32
final_genom_note = []
final_genom_chord = []

# Ticks or something, idk
count = 1536

# To take tonality
key = music21.converter.parse(input_file).analyze('key')
print(key)

# To take best notes in tonality
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

# working tone index
if key.mode == "minor":
    wti = t_min.index(piano[key.tonic.name])
else:
    wti = t_maj.index(piano[key.tonic.name])
wti_dim = [t_dim[wti]]
wti_maj = []
wti_min = []

#Remember working tonality (and exception as we working with lists, not circle
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

# Paterns for chords
maj_pat = [0, 4, 7]
min_pat = [0, 3, 7]
dim_pat = [0, 3, 6]
all_chords = [maj_pat, min_pat, dim_pat]

# Remember octave of each chord
octave = []

# Add info of the chord
def update_accord(note):
    if (note % 12) in wti_maj:
        final_genom_chord.append(0)
    elif (note % 12) in wti_min:
        final_genom_chord.append(1)
    elif (note % 12) in wti_dim:
        final_genom_chord.append(2)
    else:
        rand = rnd.randint(0, 2)
        final_genom_chord.append(rand)
    final_genom_note.append(note % 12)
    octave.append(note // 12 - 1)

# Variables for searching first notes in each count(maybe, i'm not good in terminology)
tick = 0
found = False

# Parsing MIDI and find good chords
for msg in mid.tracks[1]:
    tick += msg.time
    # If we have empty count
    if msg.time == count and msg.type == 'note_on':

        found = True

        final_genom_note.append(None)
        final_genom_chord.append(None)
        octave.append(None)

        update_accord(msg.note)
        continue
    # If we in the beginning of the count
    elif tick % count == 0 and tick // count > 0:
        found = False
    # If note between two octaves
    elif (tick - msg.time) // count < tick // count:
        found = True
        update_accord(msg.note)
    # If we already found note or it's not needable message - skip
    if found or msg.type != 'note_on':
        continue
    else:
        found = True
        update_accord(msg.note)

'''
Well, well, it's just a class for our chromosome of the chord.
It collects number of the chords as size, rating regarding best chords and genes (Notes and type of chords)
'''
class Chromosome:
    def __init__(self, size, gene_p_n, gene_p_c):
        rate = 0
        for obj in final_genom_chord:
            if obj is not None:
                rate += 2

        self.rating = rate
        self.size = size
        self.gen_note = [[0 for _ in range(size)], [0 for _ in range(size)]]

        #Recalculate rating after initialize
        if gene_p_n is not None and gene_p_c is not None:
            self.set_rnd_note_chord()
            for i in range(self.size):
                if final_genom_chord[i] is not None:
                    if self.gen_note[0][i] == final_genom_note[i]:
                        self.rating -= 1
                    if self.gen_note[1][i] == final_genom_chord[i]:
                        self.rating -= 1
    #Generate random genes (both notes and type of chords)
    def set_rnd_note_chord(self):
        for i in range(len(final_genom_note)):
            if final_genom_note[i] is None:
                self.gen_note[0][i] = None
            else:
                self.gen_note[0][i] = rnd.choice(note_gen)

        for i in range(len(final_genom_chord)):
            if final_genom_chord[i] is None:
                self.gen_note[1][i] = None
            else:
                self.gen_note[1][i] = rnd.choice(chord_gen)

# Create(initiate) population for algorithm
def create_pop(chromo_size):
    pop = []
    for _ in range(pop_size):
        pop.append(Chromosome(chromo_size, note_gen, chord_gen))
    print(len(pop))
    return pop

# Just sort population (with upgraded bubble sort)
def sort_pop(pop):
    flag = True
    while flag:
        flag = False
        for i in range(0, len(pop) - 1):
            bub = pop[i]
            if bub.rating > pop[i + 1].rating:
                pop[i] = pop[i + 1]
                pop[i + 1] = bub
                flag = True


# Choose best
def best_individs(pop):
    for i in range(len(survivors)):
        survivors[i] = pop[i]


# Get random parent
def get_p_i(parents, ex_par):
    while True:
        ind = rnd.randint(0, len(parents) - 1)
        if ex_par is None or ex_par != ind:
            return ind


# Make crossover
def cross(gen1: object, gen2: object) -> object:
    # Find division index
    div = rnd.randint(0, gen1.size - 1)

    # Make an empty child
    child = Chromosome(gen1.size, None, None)

    # First part of the children genome from first parent
    for i in range(div):
        child.gen_note[0][i] = gen1.gen_note[0][i]
        child.gen_note[1][i] = gen1.gen_note[1][i]

    # Second part of the children genome from second parent
    for i in range(div, gen1.size):
        child.gen_note[0][i] = gen2.gen_note[0][i]
        child.gen_note[1][i] = gen2.gen_note[1][i]
    return child

# Make new childs and add them into existing generation
def new_gen(population, parent, children_count):
    while children_count < pop_size:
        #get index of random parents
        first_ind = get_p_i(parent, None)
        second_ind = get_p_i(parent, first_ind)
        #get parents
        p1 = parent[first_ind]
        p2 = parent[second_ind]

        '''
        p1: Let's make a child!
        p2: Two children, honey!
        '''

        population[children_count] = cross(p1, p2)
        population[children_count + 1] = cross(p2, p1)
        children_count += 2

# Mutatuion of 'individs_count' number of individs with 'changes_count' in their chromosome
def mutate(pop, individs_count, changes_count):
    for i in range(individs_count):
        x_gen_index = rnd.randint(0, pop_size - 1)
        chrom = pop[x_gen_index]
        for j in range(changes_count):
            gene_pos = rnd.randint(0, chrom.size - 1)
            while chrom.gen_note[0][gene_pos] is None:
                gene_pos = rnd.randint(0, chrom.size - 1)
            chrom.gen_note[0][gene_pos] = rnd.choice(note_gen)
            chrom.gen_note[1][gene_pos] = rnd.choice(chord_gen)

# Recalculate rating of each individ
def calc_rating(pop):
    for x_gen in pop:
        rate = 0
        for obj in final_genom_chord:
            if obj is not None:
                rate += 2
        x_gen.rating = rate
        for i in range(x_gen.size):
            if final_genom_chord[i] is not None:
                if x_gen.gen_note[0][i] == final_genom_note[i]:
                    x_gen.rating -= 1
                if x_gen.gen_note[1][i] == final_genom_chord[i]:
                    x_gen.rating -= 1


# Initial variables for work
popul = create_pop(len(final_genom_chord))
survivors = [0] * (pop_size // 2)
gener_num = 1000

# Loop for our evolutionary algorithm
for i in range(1000):
    # Calculate rating of each genome
    calc_rating(popul)

    # Sort in decreasing order (best of them are first)
    sort_pop(popul)

    # Print our generation
    print(f"{i}th generation. Best genom in generation:{popul[0].gen_note} and its rating {popul[0].rating}")

    # If we've found best member - leave
    if popul[0].rating == 0:
        print("\nI've found the best!")
        break

    # Choose best of the generation (1/2 of the population)
    best_individs(popul)

    # Generate new childrens and make it as new generation
    new_gen(popul, survivors, pop_size // 2)

    # Mutate some members in random
    mutate(popul, 16, 1)

# Output best genome
print(f"Output genome:{popul[0].gen_note} and rating {popul[0].rating}")

# Get all info in one list
final_comp = []
for i in range(len(final_genom_chord)):
    final_comp.append([popul[0].gen_note[0][i], popul[0].gen_note[1][i], octave[i]])

# Output pipi-pupu check
track = MidiTrack()
mid.tracks.append(track)

# Metadata for track from original track
track.append(mid.tracks[1][0])
track.append(mid.tracks[1][1])

# Input data in MIDI format
flagged = False
for accord in final_comp:
    if accord[0] is None:
        flagged = True
        continue
    if flagged:
        track.append(Message('note_on', note=accord[0]  # our note within octave
                                             + all_chords[accord[1]][0]  # add value to get accord
                                             + accord[2] * 12, velocity=vel, time=count))  # add octave
        track.append(Message('note_on', note=accord[0]  # our note within octave
                                             + all_chords[accord[1]][1]  # add value to get accord
                                             + accord[2] * 12, velocity=vel, time=0))
        track.append(Message('note_on', note=accord[0]  # our note within octave
                                             + all_chords[accord[1]][2]  # add value to get accord
                                             + accord[2] * 12, velocity=vel, time=0))
        track.append(Message('note_off', note=accord[0]  # our note within octave
                                              + all_chords[accord[1]][0]  # add value to get accord
                                              + accord[2] * 12, velocity=vel, time=count))
        track.append(Message('note_off', note=accord[0]  # our note within octave
                                              + all_chords[accord[1]][1]  # add value to get accord
                                              + accord[2] * 12, velocity=vel, time=0))
        track.append(Message('note_off', note=accord[0]  # our note within octave
                                              + all_chords[accord[1]][2]  # add value to get accord
                                              + accord[2] * 12, velocity=vel, time=0))
        flagged = False
    else:
        track.append(Message('note_on', note=accord[0]  # our note within octave
                                             + all_chords[accord[1]][0]  # add value to get accord
                                             + accord[2] * 12, velocity=vel, time=0))  # add octave
        track.append(Message('note_on', note=accord[0]  # our note within octave
                                             + all_chords[accord[1]][1]  # add value to get accord
                                             + accord[2] * 12, velocity=vel, time=0))
        track.append(Message('note_on', note=accord[0]  # our note within octave
                                             + all_chords[accord[1]][2]  # add value to get accord
                                             + accord[2] * 12, velocity=vel, time=0))
        track.append(Message('note_off', note=accord[0]  # our note within octave
                                              + all_chords[accord[1]][0]  # add value to get accord
                                              + accord[2] * 12, velocity=vel, time=count))
        track.append(Message('note_off', note=accord[0]  # our note within octave
                                              + all_chords[accord[1]][1]  # add value to get accord
                                              + accord[2] * 12, velocity=vel, time=0))
        track.append(Message('note_off', note=accord[0]  # our note within octave
                                              + all_chords[accord[1]][2]  # add value to get accord
                                              + accord[2] * 12, velocity=vel, time=0))

# Just save file
mid.save(pat)