# 00E0 / 00EE – Clear screen, return from subroutine
# 1NNN / 2NNN / 3XNN … – Jump, call, skip instructions
# 4XNN / 5XY0 – Skip if registers equal/not equal
# 6XNN / 7XNN – Load/add to registers
# 8XY0–8XYE – Register math & bitwise ops
# 9XY0 – Skip if registers not equal
# ANNN / BNNN – Set I register / jump with offset
# CXNN – Random & mask
# DXYN – Draw sprite
# EX9E / EXA1 – Skip if key pressed/not pressed
# FX07 / FX0A / FX15 / FX18 / FX1E / FX29 / FX33 / FX55 / FX65 – Timers, I operations, memory transfer


import opcode
import random

class Chip8:
    def __init__(self):
        self.memory = [0] * 4096        # 4kb of RAM
        self.v = [0] * 16               # 16 General purpose registers (V0-VF0)
        self.i = 0                      #Index register (points to memory)
        self.pc = 0x200                 #Program counter (starts at 0x200)
        self.stack = []                 # Remembers where we were before a jump
        self.display = [0] * (64 * 32)  # 64x32 pixel monochrome display (1 or 2)
        self.delay_timer = 0
        self.sound_timer = 0
        self.keypad = [0] * 16          # Hex-based keypad (0x0-0xF)
        FONT_SET = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        for i in range(len(FONT_SET)):
            self.memory[i] = FONT_SET[i]

    def fetch(self):
        # Grab byte at PC and the next byte
        byte1 = self.memory[self.pc]
        byte2 = self.memory[self.pc + 1]

        # Shift B1 left by 8b and 'OR' it with B2
        # Result: 0xA2 and 0xF1 -> 0xA2F1
        opcode = (byte1 << 8) | byte2
    
        # Move 'finger' forward 2 slots for the next instruction
        self.pc += 2
        return opcode
    
    def execute(self, opcode):
        # 'Mask' the first 4 bits to see the main command
        first_nibble = (opcode & 0xF000) >> 12

        if first_nibble == 0x0:
            if opcode == 0x00EE:
                # 00EE: Return from subroutine
                self.pc = self.stack.pop()
            elif opcode == 0x00E0:
                # 00E0: Clear screen
                self.display = [0] * (64 * 32)

        elif first_nibble == 0x1:
            # Instruction 1NNN: Jump to adress NNN
            address = opcode & 0x0FFF
            self.pc = address            # Set our finger to the new page
    
        elif first_nibble == 0x2:
            # 2NNN: Call subroutine at NNN
            self.stack.append(self.pc)
            self.pc = opcode & 0x0FFF
        
        elif first_nibble == 0x3:
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            if self.v[x] == nn:
                self.pc += 2  # Skip next instruction

        elif first_nibble == 0x4:
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            if self.v[x] != nn:
                self.pc += 2

        elif first_nibble == 0x5:
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            if self.v[x] == self.v[y]:
                self.pc += 2

        elif first_nibble == 0x6:
            # Instruction 6XNN: Set VX to NN
            x = (opcode & 0x0F00) >> 8  # Isolate 'X'
            nn = (opcode & 0x00FF)      # Isolate 'NN'
            self.v[x] = nn              # Put the value in the register
        
        elif first_nibble == 0x7:
            # 7XNN: Add NN to VX
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            self.v[x] = (self.v[x] + nn) & 0xFF

        # Copy register
        elif first_nibble == 0x8:
            last = opcode & 0x000F
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4

            if last == 0x0:
                self.v[x] = self.v[y]
            
            elif last == 0x1:
                self.v[x] |= self.v[y]

            elif last == 0x2:
                self.v[x] &= self.v[y]

            elif last == 0x3:
                self.v[x] ^= self.v[y]

            elif last == 0x4:
                total = self.v[x] + self.v[y]
                self.v[0xF] = 1 if total > 255 else 0
                self.v[x] = total & 0xFF

            elif last == 0x5:
                self.v[0xF] = 1 if self.v[x] > self.v[y] else 0
                self.v[x] = (self.v[x] - self.v[y]) & 0xFF

            elif last == 0x6:  # SHR
                self.v[0xF] = self.v[x] & 1
                self.v[x] >>= 1
            elif last == 0x7:
                self.v[0xF] = 1 if self.v[y] > self.v[x] else 0
                self.v[x] = (self.v[y] - self.v[x]) & 0xFF

            elif last == 0xE:  # SHL
                self.v[0xF] = (self.v[x] >> 7) & 1
                self.v[x] = (self.v[x] << 1) & 0xFF

        elif first_nibble == 0x9:
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            if self.v[x] != self.v[y]:
                self.pc += 2

        elif first_nibble == 0xA:
            # ANNN: Set index register I to NNN
            self.i =opcode & 0x0FFF
        
        elif first_nibble == 0xB:
            # BNNN: Jump to address NNN + V0
            nn = opcode & 0x0FFF
            self.pc = self.v[0] + nn

        elif first_nibble == 0xC:
            # CXNN: Set VX to a random number AND NN
            x = (opcode & 0x0F00) >> 8
            nn = opcode & 0x00FF
            self.v[x] = random.randint(0, 255) & nn

        elif first_nibble == 0xD:
            # DXYN: Draw sprite at (VX, VY) with height N
            x_pos = self.v[(opcode & 0x0F00) >> 8] % 64
            y_pos = self.v[(opcode & 0x00F0) >> 4] % 32
            height = opcode & 0x000F

            self.v[0xF] = 0 # Reset collision flag

            for row in range(height):
                sprite_byte = self.memory[self.i + row]
                for col in range(8):
                    # Check each bit in the sprite byte (from left to right)
                    if (sprite_byte & (0x80 >> col)) != 0:
                        # Calculate screen index
                        screen_idx = ((x_pos + col) % 64) + (((y_pos + row) % 32) * 64)
                        if self.display[screen_idx] == 1:
                            self.v[0xF] = 1                 # Collision detected
                        self.display[screen_idx] ^= 1       #XOR the pixel

        elif first_nibble == 0xE:
            x = (opcode & 0x0F00) >> 8
            key = self.v[x]

            if opcode & 0x00FF == 0x9E:
                if self.keypad[key]:
                    self.pc += 2
            
            elif opcode & 0x00FF == 0xA1:
                if not self.keypad[key]:
                    self.pc += 2

        elif first_nibble == 0xF:
            x = (opcode & 0x0F00) >> 8
            last_byte = opcode & 0x00FF

            if last_byte == 0x07:
                self.v[x] = self.delay_timer

            elif last_byte == 0x15:
                self.delay_timer = self.v[x]

            elif last_byte == 0x18:
                self.sound_timer = self.v[x]

            # Can be used for sprite positioning
            elif last_byte == 0x1E:
                self.i = (self.i + self.v[x]) & 0xFFF

            elif last_byte == 0x29:
                # FX29: Set I to the location of the sprite for the character in VX
                self.i = self.v[x] * 5  # Each sprite is 5 bytes long

            elif last_byte == 0x0A:
                # FX0A: wait for key press, store in VX
                key_pressed = False
                for i, k in enumerate(self.keypad):
                    if k != 0:
                        self.v[x] = i
                        key_pressed = True
                        break
                if not key_pressed:
                    self.pc -= 2  # Stay on this instruction until a key is pressed

            #BCD conversion
            elif last_byte == 0x33:
                value = self.v[x]
                self.memory[self.i] = value // 100
                self.memory[self.i + 1] = (value // 10) % 10
                self.memory[self.i + 2] = value % 10

            # Memory ops
            elif last_byte == 0x55:
                for i in range(x + 1):
                    self.memory[self.i + i] = self.v[i]

            elif last_byte == 0x65:
                for i in range(x + 1):
                    self.v[i] = self.memory[self.i + i]

    def load_rom(self, path):
        with open(path, "rb") as f:
            rom_data = f.read()
            for i in range(len(rom_data)):
                # We start at 0x200 (512) to avoid overwriting the font!
                self.memory[0x200 + i] = rom_data[i]
    
    def update_timers(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1