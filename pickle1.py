import pickle
set1 = set()
d = dict()
range1 = []
pickle.dump(range1,open("range_list.p","wb"))
pickle.dump(set1,open("categories.p","wb"))
pickle.dump(d,open("acts_list_categories_dict.p","wb"))
pickle.dump(d,open("no_of_acts_categories_dict.p","wb"))
