from util.part import Part

class Obj:
    def __init__(self, boundary: str, parts):
        self.boundary = boundary
        self.parts = parts

    def getBoundary(self):
        return self.boundary
    
    def getPart(self):
        return self.parts
    
    def setBoundary(self, boundary: str):
        self.boundary = boundary

    def setPart(self, parts):
        self.parts = parts