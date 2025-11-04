import pygame
import sys
import random

# Initialization
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Mod - FNF Python")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 100)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
GRAY = (30, 30, 40)
PURPLE = (150, 50, 255)
ORANGE = (255, 150, 0)

# Fonts
title_font = pygame.font.SysFont("Arial", 72, bold=True)
font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)
timer_font = pygame.font.SysFont("Arial", 32, bold=True)
combo_font = pygame.font.SysFont("Arial", 48, bold=True)

# Load images
bg_image = pygame.image.load("Bg.png").convert()
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

char_size = (300, 400)
idle_img = pygame.image.load("Character1Anim1.png").convert_alpha()
idle_img = pygame.transform.scale(idle_img, char_size)

left_img = pygame.image.load("Character1Anim2.png").convert_alpha()
left_img = pygame.transform.scale(left_img, char_size)

up_img = pygame.image.load("Character1Anim3.png").convert_alpha()
up_img = pygame.transform.scale(up_img, char_size)

down_img = pygame.image.load("Character1Anim4.png").convert_alpha()
down_img = pygame.transform.scale(down_img, char_size)

right_img = pygame.image.load("Character1Anim5.png").convert_alpha()
right_img = pygame.transform.scale(right_img, char_size)

current_char_img = idle_img
char_x = (WIDTH - char_size[0]) // 2
char_y = (HEIGHT - char_size[1]) // 2

# Arrows
arrow_size = (80, 80)
arrow_left = pygame.image.load("ArrowLeft.png").convert_alpha()
arrow_left = pygame.transform.scale(arrow_left, arrow_size)

arrow_down = pygame.image.load("ArrowDown.png").convert_alpha()
arrow_down = pygame.transform.scale(arrow_down, arrow_size)

arrow_up = pygame.image.load("ArrowUp.png").convert_alpha()
arrow_up = pygame.transform.scale(arrow_up, arrow_size)

arrow_right = pygame.image.load("ArrowRight.png").convert_alpha()
arrow_right = pygame.transform.scale(arrow_right, arrow_size)

# Arrow positions (above player)
arrow_spacing = 100
arrow_start_x = (WIDTH - arrow_spacing * 3) // 2
hit_y = char_y - 50

hit_positions = {
    0: (arrow_start_x, hit_y),
    1: (arrow_start_x + arrow_spacing, hit_y),
    2: (arrow_start_x + arrow_spacing * 2, hit_y),
    3: (arrow_start_x + arrow_spacing * 3, hit_y)
}

arrow_images = [arrow_left, arrow_down, arrow_up, arrow_right]
arrow_keys = [pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT]
char_anims = [left_img, down_img, up_img, right_img]

# Health bar - at bottom
health = 100
max_health = 100
health_bar_width = 400
health_bar_height = 30
health_bar_x = (WIDTH - health_bar_width) // 2
health_bar_y = HEIGHT - 80

# Game states
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
RESULTS = "results"
current_state = MENU

# Score & Stats
score = 0
combo = 0
max_combo = 0
misses = 0
hits = 0
total_notes = 0
multiplier = 1.0

# Notes
notes = []
chart_index = 0

# === CHART SYSTEM - FULL SONGS ===
# Song duration: 2:36 → 156000ms
SONG_DURATION_MS = 156000

# Procedurally generate full charts
def generate_chart(num_notes):
    """Generates a chart with given number of notes spread over the song."""
    chart = []
    total_time = SONG_DURATION_MS - 2000  # Leave 2s at end
    interval = total_time // num_notes
    
    time_offset = 1000  # Start after 1s
    for i in range(num_notes):
        time = time_offset + (i * interval) + random.randint(-200, 200)  # Add jitter
        lane = random.randint(0, 3)
        chart.append({"time": time, "lane": lane})
    
    # Sort by time
    chart.sort(key=lambda x: x["time"])
    return chart

# Charts per difficulty
charts = {
    "easy":   generate_chart(100),
    "normal": generate_chart(150),
    "hard":   generate_chart(225)
}

# Current chart
chart = charts["normal"]

# Difficulty settings
difficulties = {
    "easy":   {"tolerance": 60, "speed": 3.8, "spacing": 100},
    "normal": {"tolerance": 45, "speed": 4.5, "spacing": 100},
    "hard":   {"tolerance": 30, "speed": 5.5, "spacing": 85}
}
current_difficulty = "normal"
HIT_TOLERANCE = difficulties[current_difficulty]["tolerance"]
NOTE_SPEED = difficulties[current_difficulty]["speed"]
arrow_spacing = difficulties[current_difficulty]["spacing"]

# Key states
key_pressed = {k: False for k in arrow_keys}

# === SOUND EFFECTS ===
miss_sound = None
hit_sound = None
try:
    miss_sound = pygame.mixer.Sound("MissSound.mp3")
    hit_sound = pygame.mixer.Sound("HitSound.mp3")
    print("Sound effects loaded!")
except Exception as e:
    print(f"Sound files not found or error: {e}")
    print("Place MissSound.mp3 and HitSound.mp3 in the same folder.")

# Music
try:
    pygame.mixer.music.load("IntroSound.mp3")
    game_music = pygame.mixer.Sound("GameSound.mp3")
    print("Music loaded!")
except Exception as e:
    print(f"Music files not found: {e}")
    game_music = None

# Song duration
SONG_DURATION = 156
song_start_time = 0
song_playing = False

# Effects
hit_flash = 0
shake_offset = [0, 0]
combo_pop = []

# Menu animation
menu_alpha = 0
menu_fade_in = True

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks()
    elapsed = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    if event.key == pygame.K_1:
                        current_difficulty = "easy"
                    elif event.key == pygame.K_2:
                        current_difficulty = "normal"
                    elif event.key == pygame.K_3:
                        current_difficulty = "hard"
                    
                    # Update difficulty
                    HIT_TOLERANCE = difficulties[current_difficulty]["tolerance"]
                    NOTE_SPEED = difficulties[current_difficulty]["speed"]
                    arrow_spacing = difficulties[current_difficulty]["spacing"]
                    
                    # Update arrow positions
                    arrow_start_x = (WIDTH - arrow_spacing * 3) // 2
                    hit_positions = {
                        0: (arrow_start_x, hit_y),
                        1: (arrow_start_x + arrow_spacing, hit_y),
                        2: (arrow_start_x + arrow_spacing * 2, hit_y),
                        3: (arrow_start_x + arrow_spacing * 3, hit_y)
                    }
                    
                    # Update chart
                    chart = charts[current_difficulty]

                if event.key == pygame.K_RETURN:
                    current_state = PLAYING
                    # Reset
                    health = 100
                    score = 0
                    combo = 0
                    max_combo = 0
                    misses = 0
                    hits = 0
                    total_notes = len(chart)
                    notes = []
                    chart_index = 0
                    song_start_time = current_time + 1000
                    song_playing = True
                    if game_music:
                        game_music.play()
                    pygame.mixer.music.stop()

        elif current_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                for i, key in enumerate(arrow_keys):
                    if event.key == key:
                        key_pressed[key] = True
                        hit = False
                        for note in notes[:]:
                            if note['lane'] == i:
                                dist = abs(note['y'] - hit_y)
                                if dist <= HIT_TOLERANCE:
                                    notes.remove(note)
                                    if hit_sound:
                                        hit_sound.play()
                                    hit_flash = 15
                                    combo_pop.append({
                                        "text": "NICE!",
                                        "x": hit_positions[i][0] + 40,
                                        "y": hit_y - 50,
                                        "life": 30,
                                        "vy": -3
                                    })
                                    base_score = 100 + (combo * 10)
                                    final_score = int(base_score * multiplier)
                                    score += final_score
                                    combo += 1
                                    max_combo = max(max_combo, combo)
                                    hits += 1
                                    health = min(health + 5, max_health)
                                    hit = True
                                    break
                        if not hit:
                            combo = 0
                            multiplier = 1.0
                            health -= 15

            if event.type == pygame.KEYUP:
                if event.key in arrow_keys:
                    key_pressed[event.key] = False

        elif current_state == RESULTS:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                current_state = MENU
                menu_alpha = 0
                menu_fade_in = True
                pygame.mixer.music.load("IntroSound.mp3")
                pygame.mixer.music.play(-1)

        elif current_state == GAME_OVER:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                current_state = MENU
                menu_alpha = 0
                menu_fade_in = True
                pygame.mixer.music.load("IntroSound.mp3")
                pygame.mixer.music.play(-1)

    # === TIMER & SONG END ===
    if current_state == PLAYING:
        elapsed = (current_time - song_start_time) // 1000
        remaining = max(SONG_DURATION - elapsed, 0)
        mins = remaining // 60
        secs = remaining % 60

        # === CHART SPAWN ===
        if chart_index < len(chart) and current_time >= song_start_time + chart[chart_index]["time"]:
            lane = chart[chart_index]["lane"]
            notes.append({
                'lane': lane,
                'y': HEIGHT + 100,
                'speed': NOTE_SPEED,
                'spawn_time': current_time
            })
            chart_index += 1

        # === MISS DETECTION ===
        for note in notes[:]:
            note['y'] -= note['speed']
            if note['y'] + 80 < hit_y - HIT_TOLERANCE:
                notes.remove(note)
                combo = 0
                multiplier = 1.0
                misses += 1
                health -= 20
                if miss_sound:
                    miss_sound.play()
                shake_offset = [random.randint(-10, 10), random.randint(-10, 10)]

        # === COMBO MULTIPLIER ===
        if combo >= 20:
            multiplier = 2.0
        elif combo >= 10:
            multiplier = 1.5
        else:
            multiplier = 1.0

        # === SHAKE DECAY ===
        shake_offset = [s * 0.8 for s in shake_offset]

        if health <= 0:
            current_state = GAME_OVER
            if game_music:
                game_music.stop()
            pygame.mixer.music.load("IntroSound.mp3")
            pygame.mixer.music.play(-1)

        if elapsed >= SONG_DURATION and song_playing:
            current_state = RESULTS
            song_playing = False
            if game_music:
                game_music.stop()
            pygame.mixer.music.load("IntroSound.mp3")
            pygame.mixer.music.play(-1)

    # === MENU ===
    if current_state == MENU:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("IntroSound.mp3")
            pygame.mixer.music.play(-1)

        if menu_fade_in:
            menu_alpha = min(menu_alpha + 5, 255)
            if menu_alpha == 255:
                menu_fade_in = False
        else:
            menu_alpha = max(menu_alpha - 3, 180)
            if menu_alpha == 180:
                menu_fade_in = True

        screen.blit(bg_image, (0, 0))

        title = title_font.render("Cyber Mod", True, CYAN)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 120))
        title.set_alpha(menu_alpha)
        screen.blit(title, title_rect)

        subtitle = small_font.render("FNF Python Edition", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
        subtitle.set_alpha(menu_alpha)
        screen.blit(subtitle, subtitle_rect)

        diff_text = small_font.render("Choose Difficulty:", True, WHITE)
        diff_rect = diff_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        diff_text.set_alpha(menu_alpha)
        screen.blit(diff_text, diff_rect)

        easy_text = font.render("1 - EASY (100 notes)", True, GREEN if current_difficulty == "easy" else WHITE)
        easy_rect = easy_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        easy_text.set_alpha(menu_alpha)
        screen.blit(easy_text, easy_rect)

        norm_text = font.render("2 - NORMAL (150 notes)", True, YELLOW if current_difficulty == "normal" else WHITE)
        norm_rect = norm_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 90))
        norm_text.set_alpha(menu_alpha)
        screen.blit(norm_text, norm_rect)

        hard_text = font.render("3 - HARD (225 notes)", True, RED if current_difficulty == "hard" else WHITE)
        hard_rect = hard_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 130))
        hard_text.set_alpha(menu_alpha)
        screen.blit(hard_text, hard_rect)

        start_text = small_font.render("Press ENTER to start", True, CYAN)
        start_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT - 80))
        start_text.set_alpha(menu_alpha)
        screen.blit(start_text, start_rect)

    # === PLAYING ===
    elif current_state == PLAYING:
        pressed_any = False
        for i, key in enumerate(arrow_keys):
            if key_pressed[key]:
                current_char_img = char_anims[i]
                pressed_any = True
                break
        if not pressed_any:
            current_char_img = idle_img

        if hit_flash > 0:
            hit_flash -= 1

        for pop in combo_pop[:]:
            pop["y"] += pop["vy"]
            pop["vy"] += 0.2
            pop["life"] -= 1
            if pop["life"] <= 0:
                combo_pop.remove(pop)

        screen.blit(bg_image, (0, 0))
        offset_x, offset_y = int(shake_offset[0]), int(shake_offset[1])

        # Health bar
        hb_x = health_bar_x + offset_x
        hb_y = health_bar_y + offset_y
        pygame.draw.rect(screen, GRAY, (hb_x - 5, hb_y - 5, health_bar_width + 10, health_bar_height + 10), border_radius=15)
        pygame.draw.rect(screen, RED, (hb_x, hb_y, health_bar_width, health_bar_height), border_radius=12)
        pygame.draw.rect(screen, GREEN, (hb_x, hb_y, health_bar_width * (health / max_health), health_bar_height), border_radius=12)

        # Timer
        timer_text = timer_font.render(f"{mins:02d}:{secs:02d}", True, CYAN)
        timer_rect = timer_text.get_rect(center=(WIDTH//2 + offset_x, 30 + offset_y))
        screen.blit(timer_text, timer_rect)

        # Fixed arrows
        for i in range(4):
            ax, ay = hit_positions[i]
            screen.blit(arrow_images[i], (ax + offset_x, ay + offset_y))

        # Falling arrows
        for note in notes:
            x = hit_positions[note['lane']][0] + offset_x
            y = note['y'] + offset_y
            screen.blit(arrow_images[note['lane']], (x, y))
            if abs(y - hit_y - offset_y) <= HIT_TOLERANCE:
                glow = pygame.Surface(arrow_size, pygame.SRCALPHA)
                glow.fill((0, 255, 100, 100))
                screen.blit(glow, (x, y))

        if hit_flash > 0:
            flash = pygame.Surface((WIDTH, HEIGHT))
            flash.set_alpha(50)
            flash.fill(WHITE)
            screen.blit(flash, (0, 0))

        for pop in combo_pop:
            alpha = int((pop["life"] / 30) * 255)
            text = small_font.render(pop["text"], True, YELLOW)
            text.set_alpha(alpha)
            rect = text.get_rect(center=(pop["x"] + offset_x, pop["y"] + offset_y))
            screen.blit(text, rect)

        screen.blit(current_char_img, (char_x + offset_x, char_y + offset_y))

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20 + offset_x, 20 + offset_y))

        if combo > 0:
            combo_color = ORANGE if combo >= 20 else YELLOW if combo >= 10 else WHITE
            combo_text = combo_font.render(f"{combo}x", True, combo_color)
            combo_rect = combo_text.get_rect(center=(WIDTH//2 + offset_x, hit_y - 100 + offset_y))
            screen.blit(combo_text, combo_rect)

            if multiplier > 1.0:
                mult_text = small_font.render(f"x{multiplier}", True, CYAN)
                mult_rect = mult_text.get_rect(center=(WIDTH//2 + offset_x, hit_y - 60 + offset_y))
                screen.blit(mult_text, mult_rect)

        if max_combo > 0:
            max_text = small_font.render(f"Best: {max_combo}", True, GREEN)
            screen.blit(max_text, (20 + offset_x, 100 + offset_y))

        miss_text = small_font.render(f"Miss: {misses}", True, RED)
        screen.blit(miss_text, (20 + offset_x, 130 + offset_y))

    # === RESULTS ===
    elif current_state == RESULTS:
        screen.blit(bg_image, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(PURPLE)
        screen.blit(overlay, (0, 0))

        results_title = title_font.render("SONG COMPLETE!", True, CYAN)
        results_title_rect = results_title.get_rect(center=(WIDTH//2, 100))
        screen.blit(results_title, results_title_rect)

        accuracy = (hits / total_notes * 100) if total_notes > 0 else 0
        grade = "S" if accuracy >= 95 else "A" if accuracy >= 85 else "B" if accuracy >= 70 else "C" if accuracy >= 50 else "D"

        stats = [
            f"Final Score: {score}",
            f"Max Combo: {max_combo}",
            f"Notes Hit: {hits}/{total_notes}",
            f"Accuracy: {accuracy:.1f}%",
            f"Grade: {grade}",
            f"Misses: {misses}"
        ]

        y_offset = 200
        for stat in stats:
            text = font.render(stat, True, WHITE)
            rect = text.get_rect(center=(WIDTH//2, y_offset))
            screen.blit(text, rect)
            y_offset += 50

        prompt = small_font.render("Press ENTER to return to main menu", True, YELLOW)
        prompt_rect = prompt.get_rect(center=(WIDTH//2, HEIGHT - 100))
        screen.blit(prompt, prompt_rect)

    # === GAME OVER ===
    elif current_state == GAME_OVER:
        overlay = pygame.Surface((WIDTH, HEIGHT))  # Fixed: pygame.Surface, not pygame.FileNotFoundError
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        go_text = title_font.render("GAME OVER", True, RED)
        go_rect = go_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
        screen.blit(go_text, go_rect)

        final_score = font.render(f"Final Score: {score}", True, WHITE)
        final_rect = final_score.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(final_score, final_rect)

        restart_text = small_font.render("Press anything to return to menu", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()