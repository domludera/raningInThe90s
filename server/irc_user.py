
class IRCUser:

    def __init__(self):
        self.username = ''
        self.nickname = ''
        self.channel = ''

    def setUsername(self, username):
        self.username = username

    def setNickname(self, nickname):
        self.nickname = nickname

    def joinChannel(self, channel):
        self.channel = channel

    def isAuthenticated(self):
        if self.username and self.nickname:
            return True
        else:
            return False

    def joinedChannel(self):
        if self.channel:
            return True
        else:
            return False

    def getUsername(self):
        return self.username

    def getNickname(self):
        return self.nickname

    def getChannel(self):
        return self.channel

    def __str__(self):
        return self.username + ' ' + self.nickname


