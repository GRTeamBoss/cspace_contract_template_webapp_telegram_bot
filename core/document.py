from ..schemas import Document, Client

class Document:
  def __init__(self, seller: Document, client: Client):
    self.seller = seller
    self.client = client

  
  @property
  def template_document_guarantee(self):
    return "Template for Guarantee Document"

class Document_Classic(Document):
  def __init__(self, seller: Document, client: Client):
    super().__init__(seller, client)


class Document_EI(Document):
  def __init__(self, seller: Document, client: Client):
    super().__init__(seller, client)


class Document_Guarantee(Document):
  def __init__(self, seller: Document, client: Client):
    super().__init__(seller, client)