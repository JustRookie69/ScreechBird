import pygame
import pyaudio
import numpy as np
import threading

#initializing
pygame.init()

#fetching screen size
info = pygame.display.Info()
screenWidth, screenHeight = info.current_w, info.current_h
#setting up screen with full screen mode
screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN)
pygame.display.set_caption("aaaaaaaaa")

#load image for background
image = pygame.image.load("Background.png")
imageWidth, imageHeight = image.get_size()

#player setup
player_image = pygame.image.load("player.png")
player_x, player_y, = screenWidth // 2, screenHeight // 2
player_jump = False
jumpHeight = 250
jumpSpeed = 14

#setup Audio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()
stream = p.open(format = FORMAT, channels = CHANNELS, rate = RATE, input = True, frames_per_buffer = CHUNK)

#stroring sound
soundStrength = 0

def getVoiceStrength():
    global soundStrength
    while True:
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        volume = np.linalg.norm(data) / CHUNK
        soundStrength = volume

voice_thread = threading.Thread(target = getVoiceStrength)
voice_thread.daemon = True
voice_thread.start()

def BackgroundDraw():
    y_position = screenHeight - imageHeight
    for x in range(0, screenWidth, imageWidth):
        screen.blit(image, (x,y_position))

def PlayerDraw():
    screen.blit(player_image,(player_x, player_y))

def drawVoiceStrength():
    font = pygame.font.SysFont(None, 36)
    text = font.render(f'Voice Strength: {int(soundStrength)}', True, (255,0,0))
    screen.blit(text, (screenWidth - 250, 20))

def playerJump():
    global player_y, player_jump
    if player_jump:
        if player_y > screenHeight//2 - jumpHeight:
            player_y -= jumpSpeed # go up less y
        
        else:
            player_jump = False
    
    elif player_y < screenHeight // 2:
        player_y += jumpSpeed #moving down increase y

runnng  = True
while runnng:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runnng = False
        if event.type == pygame.KEYDOWN:
            if event.key ==pygame.K_Space and player_y == screenHeight //2:
                player_jump = True
        screen.fill((0, 0, 0))  # Clear screen
    
    # Draw elements
    BackgroundDraw()
    PlayerDraw()
    drawVoiceStrength()
    
    # Update player movement
    playerJump()
    
    # Update display
    pygame.display.update()

# Clean up
pygame.quit()
stream.stop_stream()
stream.close()
p.terminate()

