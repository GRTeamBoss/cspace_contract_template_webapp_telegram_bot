from faker import Faker
from app import create_app, db
from app.models import Person, Company, Client, Seller, Company, Owner, Subject

app = create_app()
fake = Faker()

def generate_fake_info():
  for i in range(10):
    if i % 2 == 0:
      subject = Subject(name="Person")
    elif i % 2 != 0:
      subject = Subject(name="Company")
    db.session.add(subject)
  db.session.commit()

  for i in range(1, 11):
    if i % 2 == 0:
      company = Company(legacy_name=fake.company(), subject_id=i, stir=fake.random_number(digits=9), bank_account=fake.bban(), bank_name=fake.company(), bank_mfo=fake.random_number(digits=5), bank_oked=fake.random_number(digits=6), address=fake.address(), director=fake.name(), phone=fake.phone_number(), email=fake.email())
      db.session.add(company)
    elif i % 2 != 0:
      person = Person(name=fake.name(), passport_id=fake.ssn(), subject_id=i)
      db.session.add(person)
  db.session.commit()
    
  for i in range(1, 3):
    owner = Owner(subject_id=i)
    db.session.add(owner)
  for i in range(3, 7):
    seller = Seller(subject_id=i)
    db.session.add(seller)
  for i in range(7, 11):
    client = Client(subject_id=i)
    db.session.add(client)
  db.session.commit()

with app.app_context():
  db.drop_all()
  db.create_all()
  generate_fake_info()