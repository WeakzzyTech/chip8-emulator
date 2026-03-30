import pygame
import sys
from emulator import Chip8

# Constants
SCALE = 10
COLOR_ON = (255, 255, 255)  # White
COLOR_OFF = (0, 0, 0)       # Black

def main():
    key_map = {
        pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
        pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
        pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
        pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
    }
    pygame.init()
    pygame.mixer.init()
    beep = pygame.mixer.Sound("beep.wav")
    beep_playing = False
    screen = pygame.display.set_mode((64 * SCALE, 32 * SCALE))
    pygame.display.set_caption("CHIP-8 Emulator")
    clock = pygame.time.Clock()

    # Initialize CPU
    cpu = Chip8()
    cpu.load_rom("Roms/Pong.ch8")

    running = True
    while running:
        # Handle Window Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        pygame_keys = pygame.key.get_pressed()
        for py_key, hex_val in key_map.items():
            if pygame_keys[py_key]:
                cpu.keypad[hex_val] = 1
            else:
                cpu.keypad[hex_val] = 0

        # Cycle the CPU
        # 10 instructions per frame
        for _ in range(10):
            opcode = cpu.fetch()
            cpu.execute(opcode)
        
        # Update Timers (should happen 60 times per second)
        cpu.update_timers()
        # CHIP-8 sound logic
        if cpu.sound_timer > 0:
            if not beep_playing:
                beep.play(-1)  # loop forever
                beep_playing = True
        else:
            if beep_playing:
                beep.stop()
                beep_playing = False

        # Draw the display
        screen.fill(COLOR_OFF)
        for i in range(len(cpu.display)):
            if cpu.display[i] == 1:
                x = (i % 64) * SCALE
                y = (i // 64) * SCALE
                pygame.draw.rect(screen, COLOR_ON, (x, y, SCALE, SCALE))
        
        pygame.display.flip()

        # Keep the loop running at 60 FPS
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()