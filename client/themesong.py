import pyglet
import threading


class ThemeSong(threading.Thread):

    def __init__(self):
        super().__init__()
        music = pyglet.resource.media('music/90s.mp3', streaming=False)
        music.play()

    def run(self):
        pyglet.app.run()

    def stop(self):
        pyglet.app.exit()






