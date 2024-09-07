import pygame
import pyaudio
import numpy as np
import threading

# initializing
pygame.init()

# fetching screen size
info = pygame.display.Info()
screenWidth, screenHeight = info.current_w, info.current_h
# setting up screen with full screen mode
screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN)
pygame.display.set_caption("Voice Input and Player Jump")

# load image for background
image = pygame.image.load("Background.png")
imageWidth, imageHeight = image.get_size()

# player setup
player_image = pygame.image.load("player.png")
player_x, player_y = screenWidth // 2, screenHeight // 2
player_jump = False
jumpHeight = 250
jumpSpeed = 14
jumpStrenght = 0  # Initialize jumpStrenght

# setup Audio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# storing sound
soundStrength = 0
displayedVolume = 0  # Volume displayed on the screen, smooth transition variable

def getVoiceStrength():
    global soundStrength
    while True:
        try:
            data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            volume = np.mean(np.abs(data))  # Alternative volume calculation
            soundStrength = volume
        except IOError:
            # Handle audio input errors
            soundStrength = 0

# Start the voice capture thread
voice_thread = threading.Thread(target=getVoiceStrength)
voice_thread.daemon = True
voice_thread.start()

def BackgroundDraw():
    y_position = screenHeight - imageHeight
    for x in range(0, screenWidth, imageWidth):
        screen.blit(image, (x, y_position))

def PlayerDraw():
    screen.blit(player_image, (player_x, player_y))

def drawVoiceStrength():
    """Displays the voice strength, smoothly decreasing when no input."""
    global displayedVolume
    
    # Smoothly adjust the displayed volume based on current sound strength
    if soundStrength > displayedVolume:
        displayedVolume += min(2, soundStrength - displayedVolume)  # Smooth increment
    else:
        displayedVolume -= min(2, displayedVolume)  # Smooth decrement when no sound detected
    
    # Draw the updated voice strength value
    font = pygame.font.SysFont('Arial', 36)  # Changed to Arial for better readability
    text = font.render(f'Voice Strength: {int(displayedVolume)}', True, (0, 0, 255))  # Blue color
    screen.blit(text, (screenWidth - 300, 20))  # Adjust position

def jumpValue():
    global jumpStrenght
    if displayedVolume > 25:
        # Find the closest multiples of 5 (lower and upper)
        lower_multiple = (displayedVolume // 5) * 5
        upper_multiple = lower_multiple + 5
    
        if (displayedVolume - lower_multiple) < (upper_multiple - displayedVolume):
            jumpStrenght = lower_multiple
        else:
            jumpStrenght = upper_multiple

        jumpStrenght = round(jumpStrenght / 5)
    else:
        jumpStrenght = 0

def playerJump():
    """Handles player jumping based on the y-axis."""
    global player_y, player_jump
    if player_jump:
        if player_y > screenHeight // 2 - jumpHeight:
            player_y -= jumpStrenght * 100  # go up, decrease y
        else:
            player_jump = False  # stop jumping when max height is reached
    elif player_y < screenHeight // 2:
        player_y += jumpStrenght * 100  # move down, increase y

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and player_y == screenHeight // 2:
                player_jump = True  # Jump only when on the ground
    
    # Clear the screen
    screen.fill((255, 255, 255))
    
    # Draw elements
    BackgroundDraw()
    PlayerDraw()
    drawVoiceStrength()
    
    # Update jump value
    jumpValue()
    
    # Update player movement
    playerJump()
    
    # Update display
    pygame.display.update()

# Clean up
pygame.quit()
stream.stop_stream()
stream.close()
p.terminate()
