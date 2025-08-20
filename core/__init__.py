from docx import Document as DocxDocument
from docx2pdf import convert
from io import BytesIO

from .api import postgreAPIexecutor


async def generate_contract(*args, **kwargs) -> BytesIO:
  """
  Generate a contract document based on the provided template and data.

  :param kwargs: The keyword arguments containing the contract data.
  :type kwargs: dict

  - *contract*: A dictionary containing the contract data.
  - *ordering*: A list of keys specifying the order of content in the document.
  
  """
  result = {}
  doc_io = BytesIO()
  doc = DocxDocument(None)
  kwargs["method"] = "GET"
  for key, value in kwargs.get("contract", {}).items():
    if isinstance(value, str):
      kwargs["query"] = f"SELECT content FROM {key} WHERE id = {value}"
      kwargs["params"] = ""
    elif isinstance(value, list):
      kwargs["query"] = f"SELECT content FROM {key} WHERE id = ANY(%s)"
      kwargs["params"] = (value,)
    result[key] = []
    sqlselect = await postgreAPIexecutor(args, kwargs)
    for row in sqlselect:
      result[key].append(row[0])
  kwargs["result"] = []
  for paragraph in kwargs.get("ordering", []):
    doc.add_paragraph("\n".join(result.get(paragraph, [])))
  doc.save(doc_io)
  doc_io.seek(0)
  convert(doc_io, docx=True)
  return doc_io.read()