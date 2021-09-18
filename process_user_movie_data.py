import re 
import sys 


# filename = './ml-100k/u.item'  './ml-100k/u.data' './ml-100k/u.user'
# example: python process_user_movie_data.py ./ml-100k/u.data ./ml-100k/u.user ./ml-100k/u.item 20 11

def process_file(filename,user_filename , movie_filename, age, genres):
    file1 = open(movie_filename,'r',encoding = "ISO-8859-1")
    lines = file1.readlines() 
    new_fn_name = "user_movie_" +  str(age) + "_" +  '_'.join(genres) + '.data'

    genre = [
        'unknown', 
        'Action',
        'Adventure',
        'Animation',
        '''Children's''',
        'Comedy',
        'Crime' ,
        'Documentary',
        'Drama',
        'Fantasy', 
        'Film-Noir',
        'Horror',
        'Musical',
        'Mystery',
        'Romance',
        'Sci-Fi',
        'Thriller',
        'War',
        'Western'
    ]

    # genre =  [11]
    genres = [int(i) for i in genres]

    movies = []
    for l in lines:
        l = l.replace("\n","")
        item = re.split('[\t \n|,]+',l)

        item_genre = item[-19:]
        for g in genres:
            if int(item_genre[g]) == 1:
                movies.append(int(item[0]))
                break


    # age = 30
    age = int(age)
    users = []
    file1 = open(user_filename,'r')
    lines = file1.readlines() 

    for l in lines:
        l = l.replace("\n","")
        u = re.split('[\t \n|,]+',l)
        
        user_age = int(u[1])
        if user_age < age:
            continue
        users.append(int(u[0]))
        



    file2 = open(filename,'r')
    lines = file2.readlines() 
    new_string  = ""
    for l in lines:
    
        l = l.replace("\n","")
        e = re.split('[\t \n|,]+',l)
        left = int(e[0])
        right = int(e[1])

        if right not in movies:
            continue 
        if left not in users:
            continue
        new_string += l + "\n"


    
    f = open(new_fn_name, "w")
    f.write(new_string)
    f.close()
    return new_fn_name

if len(sys.argv) <= 2:
    print("Input arguments format: <path of data file> <path of user file> <path of movie file> <age> <genre 1> <genre 2> ...")
else:
    data_path = sys.argv[1]
    user_path = sys.argv[2]
    movie_path = sys.argv[3]
    age = sys.argv[4]
    genres = sys.argv[5:]
    newfn = process_file(data_path, user_path, movie_path, age, genres)
    print("Your new generated file is", newfn)
