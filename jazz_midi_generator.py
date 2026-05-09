import struct

class MidiEvent:
    """Represents a MIDI event with binary struct serialization"""
    
    def __init__(self, delta_time, event_type, data):
        """
        delta_time: time since last event (in ticks)
        event_type: MIDI event type byte
        data: event data bytes
        """
        self.delta_time = delta_time
        self.event_type = event_type
        self.data = data
    
    def encode_variable_length(self, value):
        """Encode variable-length quantity for MIDI timing"""
        result = []
        result.append(value & 0x7f)
        value >>= 7
        while value:
            result.append((value & 0x7f) | 0x80)
            value >>= 7
        return bytes(reversed(result))
    
    def to_bytes(self):
        """Convert event to binary MIDI format"""
        delta_bytes = self.encode_variable_length(self.delta_time)
        return delta_bytes + bytes([self.event_type]) + self.data


class MidiTrack:
    """Represents a MIDI track with multiple events"""
    
    def __init__(self, track_name="Track 1"):
        """Initialize a MIDI track"""
        self.track_name = track_name
        self.events = []
        self.add_track_name(track_name)
        self.current_time = 0
    
    def add_track_name(self, name):
        """Add track name as a meta event"""
        name_bytes = name.encode('ascii')
        meta_event = bytes([0xff, 0x03, len(name_bytes)]) + name_bytes
        self.events.append(meta_event)
    
    def add_note_on(self, channel, pitch, velocity, delta_time):
        """Add Note On event (channel 0-15, pitch 0-127, velocity 0-127)"""
        self.current_time += delta_time
        status = 0x90 | (channel & 0x0f)
        event_data = struct.pack('BBB', status, pitch, velocity)
        
        delta_bytes = MidiEvent(delta_time, 0, b'').encode_variable_length(delta_time)
        self.events.append(delta_bytes + event_data)
    
    def add_note_off(self, channel, pitch, velocity, delta_time):
        """Add Note Off event"""
        self.current_time += delta_time
        status = 0x80 | (channel & 0x0f)
        event_data = struct.pack('BBB', status, pitch, velocity)
        
        delta_bytes = MidiEvent(delta_time, 0, b'').encode_variable_length(delta_time)
        self.events.append(delta_bytes + event_data)
    
    def add_program_change(self, channel, program, delta_time=0):
        """Add Program Change event (instrument selection)"""
        status = 0xc0 | (channel & 0x0f)
        event_data = struct.pack('BB', status, program)
        
        delta_bytes = MidiEvent(delta_time, 0, b'').encode_variable_length(delta_time)
        self.events.append(delta_bytes + event_data)
    
    def add_control_change(self, channel, controller, value, delta_time=0):
        """Add Control Change event"""
        status = 0xb0 | (channel & 0x0f)
        event_data = struct.pack('BBB', status, controller, value)
        
        delta_bytes = MidiEvent(delta_time, 0, b'').encode_variable_length(delta_time)
        self.events.append(delta_bytes + event_data)
    
    def add_end_of_track(self):
        """Add End of Track meta event"""
        end_event = bytes([0x00, 0xff, 0x2f, 0x00])
        self.events.append(end_event)
    
    def get_track_data(self):
        """Serialize track to binary MIDI format"""
        # Add end of track event
        self.add_end_of_track()
        
        # Combine all events
        track_data = b''.join(self.events)
        
        # Create track header using struct
        track_header = struct.pack('>4sI', b'MTrk', len(track_data))
        
        return track_header + track_data


class JazzMidiGenerator:
    """Generates a complete MIDI file for a jazz piece in C Major"""
    
    # MIDI parameters
    MIDI_C = 60  # Middle C
    TICKS_PER_QUARTER = 480  # Standard MIDI resolution
    
    def __init__(self, tempo=120):
        """Initialize MIDI generator"""
        self.tempo = tempo
        self.tracks = []
    
    def add_melody_track(self):
        """Add a melody track with jazz composition in C Major"""
        track = MidiTrack("Melody")
        
        # Set instrument to Grand Piano (0)
        track.add_program_change(0, 0, 0)
        
        # Set volume to 100
        track.add_control_change(0, 7, 100, 0)
        
        # Melody in C Major scale with varying note durations
        # Format: (pitch, duration_in_ticks, velocity)
        melody = [
            (self.MIDI_C, self.TICKS_PER_QUARTER // 2, 100),      # C - eighth note
            (self.MIDI_C + 2, self.TICKS_PER_QUARTER // 2, 100),  # D
            (self.MIDI_C + 4, self.TICKS_PER_QUARTER, 100),       # E - quarter note
            (self.MIDI_C + 5, self.TICKS_PER_QUARTER // 2, 100),  # F
            (self.MIDI_C + 7, self.TICKS_PER_QUARTER // 2, 100),  # G
            (self.MIDI_C + 9, self.TICKS_PER_QUARTER + self.TICKS_PER_QUARTER // 2, 100),  # A - dotted quarter
            (self.MIDI_C + 11, self.TICKS_PER_QUARTER // 2, 100), # B
            (self.MIDI_C + 12, self.TICKS_PER_QUARTER * 2, 100),  # C (octave) - half note
            (self.MIDI_C + 7, self.TICKS_PER_QUARTER // 2, 100),  # G - descending
            (self.MIDI_C + 5, self.TICKS_PER_QUARTER // 2, 100),  # F
            (self.MIDI_C + 4, self.TICKS_PER_QUARTER, 100),       # E
            (self.MIDI_C + 2, self.TICKS_PER_QUARTER * 2, 100),   # D
        ]
        
        # Add notes to track
        for pitch, duration, velocity in melody:
            track.add_note_on(0, pitch, velocity, 0)
            track.add_note_off(0, pitch, 0, duration)
        
        self.tracks.append(track)
    
    def add_harmony_track(self):
        """Add a harmony track with jazz chords"""
        track = MidiTrack("Harmony")
        
        # Set instrument to String Ensemble (48)
        track.add_program_change(0, 48, 0)
        
        # Set volume to 85
        track.add_control_change(0, 7, 85, 0)
        
        # Jazz chord progression: Cmaj7 - Am7 - Dm7 - G7
        # Format: (chord_pitches, duration_in_ticks)
        chords = [
            ([self.MIDI_C, self.MIDI_C + 4, self.MIDI_C + 7, self.MIDI_C + 11], self.TICKS_PER_QUARTER * 4),  # Cmaj7
            ([self.MIDI_C + 9, self.MIDI_C + 12, self.MIDI_C + 16, self.MIDI_C + 19], self.TICKS_PER_QUARTER * 4),  # Am7
            ([self.MIDI_C + 2, self.MIDI_C + 5, self.MIDI_C + 9, self.MIDI_C + 12], self.TICKS_PER_QUARTER * 4),  # Dm7
            ([self.MIDI_C + 7, self.MIDI_C + 11, self.MIDI_C + 14, self.MIDI_C + 17], self.TICKS_PER_QUARTER * 4),  # G7
        ]
        
        # Add chords to track
        for chord_pitches, duration in chords:
            # Note on for all pitches
            for pitch in chord_pitches:
                track.add_note_on(0, pitch, 80, 0)
            # Note off for all pitches
            for pitch in chord_pitches:
                if pitch == chord_pitches[0]:
                    track.add_note_off(0, pitch, 0, duration)
                else:
                    track.add_note_off(0, pitch, 0, 0)
        
        self.tracks.append(track)
    
    def generate_midi(self, filename="jazz_piece.mid"):
        """Generate and save the complete MIDI file"""
        # Create header track for tempo and time signature
        header_track = MidiTrack("Header")
        
        # Set tempo using struct for meta event
        tempo_data = struct.pack('>I', int(60000000 / self.tempo))[1:]  # Convert BPM to microseconds per beat
        meta_tempo = bytes([0x00, 0xff, 0x51, 0x03]) + tempo_data
        header_track.events.append(meta_tempo)
        
        # Set time signature to 4/4
        meta_time_sig = bytes([0x00, 0xff, 0x58, 0x04, 0x04, 0x02, 0x18, 0x08])
        header_track.events.append(meta_time_sig)
        
        header_track.add_end_of_track()
        
        # Build MIDI file
        midi_data = b''
        
        # MIDI file header using struct
        # Format: 'MThd' (4 bytes), header length (4 bytes), format (2 bytes), num tracks (2 bytes), division (2 bytes)
        num_tracks = len(self.tracks) + 1
        midi_header = struct.pack('>4sIHHH', 
                                 b'MThd',
                                 6,  # Header length
                                 0,  # Format 0
                                 num_tracks,  # Number of tracks
                                 self.TICKS_PER_QUARTER)  # Ticks per quarter note
        
        midi_data += midi_header
        
        # Add header track
        midi_data += header_track.get_track_data()
        
        # Add all tracks
        for track in self.tracks:
            midi_data += track.get_track_data()
        
        # Write to file
        with open(filename, 'wb') as f:
            f.write(midi_data)
        
        print(f"✓ MIDI file generated: {filename}")
        print(f"  File size: {len(midi_data)} bytes")
        print(f"  Tempo: {self.tempo} BPM")
        print(f"  Tracks: {num_tracks}")
        print(f"  Format: Standard MIDI file (uses struct for binary packing)")


def main():
    """Generate a jazz MIDI composition"""
    print("="*60)
    print("JAZZ MIDI GENERATOR - C Major".center(60))
    print("="*60)
    
    # Create MIDI generator
    generator = JazzMidiGenerator(tempo=120)
    
    print("\nBuilding melody track...")
    generator.add_melody_track()
    
    print("Building harmony track...")
    generator.add_harmony_track()
    
    print("\nGenerating MIDI file with struct-based binary format...")
    generator.generate_midi("jazz_piece_c_major.mid")
    
    print("\n" + "="*60)
    print("MIDI Composition Details:".center(60))
    print("="*60)
    print("• Time Signature: 4/4")
    print("• Key: C Major")
    print("• Melody: Grand Piano")
    print("• Harmony: String Ensemble")
    print("• Chord Progression: Cmaj7 → Am7 → Dm7 → G7")
    print("• MIDI Resolution: 480 ticks per quarter note")
    print("\nBinary Format:")
    print("  - File header: packed with struct (MThd format)")
    print("  - Track headers: packed with struct (MTrk format)")
    print("  - Events: variable-length quantities using struct")
    print("="*60)


if __name__ == "__main__":
    main()
