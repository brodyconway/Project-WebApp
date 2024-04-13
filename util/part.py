class Part:
    def __init__(self, headers, name, content):
        self.headers = headers
        self.name = name
        self.content = content

    def getHeaders(self):
        return self.headers
    
    def getName(self):
        return self.name
    
    def getContent(self):
        return self.content
    
    def setHeaders(self, headers):
        self.headers = headers
    
    def setName(self, name: str):
        self.name = name

    def setContent(self, content: bytes):
        self.content = content