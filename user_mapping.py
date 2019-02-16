"""A single user has many email ids. Mapping user to id and id to user."""

import pickle

def map_user(address_file):
    f = open(address_file, "r")
    ## Each user will have multiple addresses. Therefore values will be list
    user_to_address_dict = {}
    ## Each address corresponds to a user. Therefore values will be userLastName_userFirstName
    address_to_user_dict = {}
    ## To skip reading the firstline
    f.readline()
    for line in f.readlines():
        line = line.lower()
        line_split = line.split()
        last_name = line_split[0]
        address = line_split[-1]
        first_name = line_split[-2]
        name = last_name + "_"+ first_name
        address_to_user_dict[address] = name
        address_list = user_to_address_dict.get(name,[])
        address_list.append(address)
        user_to_address_dict[name] = address_list

    # print(user_to_address_dict)
    print(len(address_to_user_dict),address_to_user_dict)

    with open(
            "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/performance_data/user_to_address_mapping.pkl",
            "wb") as handle:
        pickle.dump(user_to_address_dict, handle)

    with open(
            "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/performance_data/address_to_user_mapping.pkl",
            "wb") as handle:
        pickle.dump(address_to_user_dict, handle)



        # print(last_name,first_name,address)




if __name__ == "__main__":
    map_user("./data/performance_data/Address_linkfile.txt")
    with open(
            "/Users/sainikhilmaram/Desktop/OneDrive/UCSB_courses/project/hedgefund_analysis/data/performance_data/address_to_user_mapping.pkl",
            "rb") as handle:
        out_dict = pickle.load(handle)
        print(out_dict)