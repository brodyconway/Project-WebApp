class Frame:
  def __init__(self, fin_bit: int, opcode: int, payload_length: int, payload: bytes):
      self.fin_bit = fin_bit
      self.opcode = opcode
      self.payload_length = payload_length
      self.payload = payload