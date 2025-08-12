class ClientSchema:

  def __init__(self, legacy_name, stir, director, bank_account_number=None, mfo=None, bank_name=None, bank_stir=None, phone_number=None, address=None):
    self.legacy_name = legacy_name
    self.stir = stir
    self.director = director
    self.bank_account_number = bank_account_number
    self.mfo = mfo
    self.bank_name = bank_name
    self.bank_stir = bank_stir
    self.phone_number = phone_number
    self.address = address


class DocumentSchema:

  def __init__(self, location, date, department=None, director=None, document_number=None, floor=None, office=None, square=None, price=None, date_from=None, date_to=None, usage_limit=None, additional_text=None):
    self.location = location
    self.date = date
    self.department = department
    self.director = director
    self.document_number = document_number
    self.floor = floor
    self.office = office
    self.square = square
    self.price = price
    self.date_from = date_from
    self.date_to = date_to
    self.usage_limit = usage_limit
    self.additional_text = additional_text