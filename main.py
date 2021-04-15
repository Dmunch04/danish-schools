import math
import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://www.skoleliste.eu/type/?t={school_type}&start={page_start}'

class SchoolType:
  AFDELING = 'afdeling'
  HOVEDSKOLE = 'hovedskole'
  INSTITUTION = 'institution-unden-enheder'

class Address(object):
  def __init__(self, address, city):
    self.address = address
    self.city = city

  def __str__(self):
    return f'{self.address} {self.city}'

  def __repr__(self):
    return self.__str__()

class School(object):
  def __init__(self, name, school_type, dean, address, website):
    self.name = name
    self.school_type = school_type
    self.dean = dean
    self.address = address
    self.website = website

  def to_string(self):
    return self.__str__()

  def __str__(self):
    return f'{self.name}, {self.school_type.split("-")[0]}, {self.dean}, {self.address}, {self.website}'

  def __repr__(self):
    return self.__str__()

def make_url(school_type, page_start=0):
  return BASE_URL.format(school_type=school_type, page_start=page_start)

def get_schools(school_type):
  schools = []

  page = requests.get(make_url(school_type))
  soup = BeautifulSoup(page.content, 'html.parser')
  
  school_amount = int(soup.find('div', class_='page_body').find('div', class_='document').find('div', class_='searched').find('b').text)
  pages = math.ceil(school_amount/20)

  for page_index in range(pages):
    schools.extend(find_school_infos(make_url(school_type, page_index*20)))

  return schools

def find_school_infos(url):
  schools = []

  page = requests.get(url)
  soup = BeautifulSoup(page.content, 'html.parser')

  school_elements = soup.find('div', class_='page_body').find('div', class_='document').find_all('div', class_='doc_entry')
  
  for school_element in school_elements:
    schools.append(parse_school_info(school_element))

  return schools

def parse_school_type(school_type):
  if school_type == 'Afdeling (underordnet enhed)': return SchoolType.AFDELING
  elif school_type == 'Hovedskole (institution med enheder)': return SchoolType.HOVEDSKOLE
  elif school_type == 'Institution uden enheder': return SchoolType.INSTITUTION

def parse_school_info(element):
  school_info_element = element.find('div', class_='school_info')
  for ad in school_info_element.find_all('div', class_='advertise'):
    ad.decompose()

  school_info = school_info_element.text.split(',')
  school_type = parse_school_type(school_info[0].replace('Type af skole:', '').strip())
  city = school_info_element.find('span', class_='city').text.strip()
  location = Address(school_info[1].strip(), city)
  dean = school_info[2].replace(city, '').replace('Skoleleder:', '').replace('Direktør:', '').strip()
  website = school_info[3].strip() if len(school_info) == 4 else 'a'

  return School(
    name=element.find('div', class_='doc_entry_desc').find('div', class_='school_name').find('a', class_='red').text.strip(),
    school_type=school_type,
    dean=dean,
    address=location,
    website=website
  )

if __name__ == '__main__':
  print('Writing "afdelinger"...')
  with open('afdelinger.txt', 'w+') as file:
    for school in get_schools(SchoolType.AFDELING):
      file.write(school.to_string())
      file.write('\n\n')
  print('Finished writing "afdelinger".')

  print('Writing "hovedskoler"...')
  with open('hovedskoler.txt', 'w+') as file:
    for school in get_schools(SchoolType.HOVEDSKOLE):
      file.write(school.to_string())
      file.write('\n\n')
  print('Finished writing "hovedskoler".')

  print('Writing "institutioner"...')
  with open('institutioner.txt', 'w+') as file:
    for school in get_schools(SchoolType.INSTITUTION):
      file.write(school.to_string())
      file.write('\n\n')
  print('Finished writing "institutioner".')
