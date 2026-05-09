import struct
import math

class JazzNote:
    """Represents a musical note with struct-based storage"""
    
    # Struct format: pitch (int), duration (float), velocity (int), is_rest (bool)
    FORMAT = 'iBfB?'
    SIZE = struct.calcsize(FORMAT)
    
    def __init__(self, pitch, duration, velocity=100, is_rest=False):
        """
        Initialize a jazz note
        pitch: MIDI note number (0-127)
        duration: note duration in beats
        velocity: MIDI velocity (0-127)
        is_rest: True if this is a rest
        """
        self.pitch = pitch
        self.duration = duration
        self.velocity = velocity
        self.is_rest = is_rest
    
    def to_bytes(self):
        """Pack note data into binary format"""
        return struct.pack(self.FORMAT, self.pitch, self.duration, 
                          self.velocity, self.is_rest)
    
    @classmethod
    def from_bytes(cls, data):
        """Unpack binary data into a JazzNote"""
        pitch, duration, velocity, is_rest = struct.unpack(cls.FORMAT, data)
        return cls(pitch, duration, velocity, is_rest)
    
    def __repr__(self):
        rest_str = "(rest)" if self.is_rest else ""
        return f"Note(pitch={self.pitch}, duration={self.duration}, velocity={self.velocity}) {rest_str}"


class JazzChord:
    """Represents a jazz chord with multiple notes"""
    
    # C Major scale: C, D, E, F, G, A, B (relative to C)
    C_MAJOR_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
    
    # Common jazz chord patterns (semitone intervals from root)
    CHORD_PATTERNS = {
        'major': [0, 4, 7],           # Major triad
        'minor': [0, 3, 7],           # Minor triad
        'dominant7': [0, 4, 7, 10],   # Dominant 7th
        'maj7': [0, 4, 7, 11],        # Major 7th
        'min7': [0, 3, 7, 10],        # Minor 7th
        'min7b5': [0, 3, 6, 10],      # Half-diminished
        'maj9': [0, 4, 7, 11, 2],     # Major 9th
    }
    
    def __init__(self, root_pitch, chord_type='major', octave=4, duration=1.0):
        """
        Initialize a jazz chord
        root_pitch: MIDI note number for the root
        chord_type: type of chord (see CHORD_PATTERNS)
        octave: octave offset multiplier (12 semitones)
        duration: chord duration in beats
        """
        self.root_pitch = root_pitch
        self.chord_type = chord_type
        self.duration = duration
        self.notes = self._build_chord(octave)
    
    def _build_chord(self, octave):
        """Build chord notes based on pattern"""
        pattern = self.CHORD_PATTERNS.get(self.chord_type, [0, 4, 7])
        notes = []
        for interval in pattern:
            pitch = self.root_pitch + interval + (octave * 12)
            notes.append(JazzNote(pitch, self.duration, velocity=90))
        return notes
    
    def __repr__(self):
        return f"Chord({self.chord_type.upper()}, root={self.root_pitch}, duration={self.duration})"


class JazzPiece:
    """A complete jazz composition in C Major"""
    
    # MIDI note numbers for C Major scale
    MIDI_C = 60  # Middle C
    
    def __init__(self, tempo=120, time_signature=(4, 4)):
        """
        Initialize a jazz piece
        tempo: BPM
        time_signature: (beats, note_value)
        """
        self.tempo = tempo
        self.time_signature = time_signature
        self.beats_per_measure = time_signature[0]
        self.sequence = []
        self._build_melody()
        self._add_harmony()
    
    def _build_melody(self):
        """Build a jazz melody in C Major"""
        print("Building jazz melody in C Major...")
        
        # Melody sequence: notes in C Major scale
        # C Major scale: C, D, E, F, G, A, B (repeating)
        c_major_melody = [
            (self.MIDI_C, 0.5),      # C - eighth note
            (self.MIDI_C + 2, 0.5),  # D
            (self.MIDI_C + 4, 1.0),  # E - quarter note
            (self.MIDI_C + 5, 0.5),  # F
            (self.MIDI_C + 7, 0.5),  # G
            (self.MIDI_C + 9, 1.5),  # A - dotted quarter
            (self.MIDI_C + 11, 0.5), # B
            (self.MIDI_C + 12, 2.0), # C (octave) - half note
            (self.MIDI_C + 7, 0.5),  # G - back down
            (self.MIDI_C + 5, 0.5),  # F
            (self.MIDI_C + 4, 1.0),  # E
            (self.MIDI_C + 2, 2.0),  # D
        ]
        
        for pitch, duration in c_major_melody:
            note = JazzNote(pitch, duration, velocity=100)
            self.sequence.append(note)
    
    def _add_harmony(self):
        """Add harmonic structure with jazz chords"""
        print("Adding jazz chord harmony...")
        
        # Chord progression: Cmaj7 - Am7 - Dm7 - G7
        # Common jazz ii-V-I progression in C Major
        chords = [
            JazzChord(self.MIDI_C, 'maj7', octave=3, duration=4.0),      # Cmaj7
            JazzChord(self.MIDI_C + 9, 'min7', octave=3, duration=4.0),  # Am7
            JazzChord(self.MIDI_C + 2, 'min7', octave=3, duration=4.0),  # Dm7
            JazzChord(self.MIDI_C + 7, 'dominant7', octave=3, duration=4.0),  # G7
        ]
        
        self.harmony = chords
    
    def serialize(self):
        """Serialize the piece to binary format"""
        print("Serializing jazz piece to binary...")
        
        # Pack header: tempo (int), beats_per_measure (int), sequence_length (int)
        header = struct.pack('III', self.tempo, self.beats_per_measure, len(self.sequence))
        
        # Pack all notes
        notes_data = b''.join(note.to_bytes() for note in self.sequence)
        
        return header + notes_data
    
    def display_composition(self):
        """Display the jazz piece information"""
        print("\n" + "="*60)
        print("JAZZ PIECE IN C MAJOR".center(60))
        print("="*60)
        print(f"Tempo: {self.tempo} BPM")
        print(f"Time Signature: {self.time_signature[0]}/{self.time_signature[1]}")
        print(f"Total Notes: {len(self.sequence)}")
        
        print("\n--- MELODY ---")
        for i, note in enumerate(self.sequence, 1):
            print(f"{i:2d}. {note}")
        
        print("\n--- HARMONIC STRUCTURE (Jazz Chord Progression) ---")
        for chord in self.harmony:
            print(f"  {chord}")
            for note in chord.notes:
                print(f"     └─ {note}")
        
        print("\n--- BINARY SERIALIZATION ---")
        binary_data = self.serialize()
        print(f"Total Binary Size: {len(binary_data)} bytes")
        print(f"Header Size: {struct.calcsize('III')} bytes (Tempo, Beats, Sequence Length)")
        print(f"Note Data Size: {JazzNote.SIZE} bytes per note")
        print(f"Total Note Data: {len(self.sequence) * JazzNote.SIZE} bytes")
        
        # Show first few bytes as hex
        hex_preview = ' '.join(f'{b:02x}' for b in binary_data[:32])
        print(f"Binary Preview (first 32 bytes): {hex_preview}...")
        print("="*60 + "\n")


def main():
    """Generate and display a jazz piece in C Major"""
    
    # Create a jazz piece
    jazz = JazzPiece(tempo=120, time_signature=(4, 4))
    
    # Display the composition
    jazz.display_composition()
    
    # Demonstrate deserialization
    print("\n--- DESERIALIZATION DEMO ---")
    binary = jazz.serialize()
    
    # Unpack header
    header_size = struct.calcsize('III')
    tempo, beats, seq_len = struct.unpack('III', binary[:header_size])
    print(f"Unpacked Header: Tempo={tempo} BPM, Beats={beats}/4, Sequence Length={seq_len}")
    
    # Unpack first 3 notes to demonstrate
    print(f"\nFirst 3 Notes (reconstructed from binary):")
    for i in range(3):
        offset = header_size + (i * JazzNote.SIZE)
        note_data = binary[offset:offset + JazzNote.SIZE]
        note = JazzNote.from_bytes(note_data)
        print(f"  {i+1}. {note}")


if __name__ == "__main__":
    main()
