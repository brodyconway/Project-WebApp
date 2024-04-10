class Part:
    def __init__(self, header: dict, name: str, content: bytes):
        self.header = header
        self.name = name
        self.content = content

    def getHeader(self):
        return self.header
    
    def getName(self):
        return self.name
    
    def getContent(self):
        return self.content
    
    def setHeader(self, header: dict):
        self.header = header
    
    def setName(self, name: str):
        self.name = name

    def setContent(self, content: bytes):
        self.content = content