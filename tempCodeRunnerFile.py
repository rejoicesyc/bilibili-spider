rel_titles=soup.find_all('a',class_="title")
rel_titles=[rel_title.text for rel_title in rel_titles]