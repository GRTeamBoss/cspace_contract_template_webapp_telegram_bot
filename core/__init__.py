from ..schemas import DocumentSchema, ClientSchema
from .document import Document_Classic, Document_EI, Document_Guarantee

def create_document(seller: DocumentSchema, client: ClientSchema):
  return Document_Classic(seller, client)

def create_document_ei(seller: DocumentSchema, client: ClientSchema):
  return Document_EI(seller, client)

def create_guarantee_document(seller: DocumentSchema, client: ClientSchema):
  return Document_Guarantee(seller, client)