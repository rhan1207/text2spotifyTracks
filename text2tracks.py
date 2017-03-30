from itertools import combinations, chain
import fileinput
import requests

def find_track(aStr):
    # it seems spotify api doesn't support exact track name match
    # so the solution is to obtain all partial matches through endpoints
    # then find exact match afterwards (not case sensitive)
    aStr = aStr.lower()
    exist = 0
    limit = 50
    offset = 0

    query = 'https://api.spotify.com/v1/search?q="' + aStr + '"&type=track&limit=' + str(limit)
    request = requests.get(query)
    results = request.json()
    all_list = results['tracks']['items']
    total_hits = results['tracks']['total']

    name_list = list(map(lambda x: x['name'].lower(), all_list))

    # find exact match using 50 step-size
    try:
        idx = name_list.index(aStr)
        return results['tracks']['items'][idx]['external_urls']['spotify']
        exist = 1
    except:
        exist = 0
    count = total_hits - limit
    while ((exist == 0) & (count > 0)):
        offset += limit
        query='https://api.spotify.com/v1/search?q="'+aStr+'"&type=track&limit='+str(limit)+'&offset='+str(offset)
        request = requests.get(query)
        results = request.json()
        all_list = results['tracks']['items']
        name_list = list(map(lambda x: x['name'].lower(), all_list))
        try:
            idx = name_list.index(aStr)
            return results['tracks']['items'][idx]['external_urls']['spotify']
            exist = 1
        except:
            exist = 0
        count = count - limit
    return None

# sum_to_n(n) is adapted from the following source
# http://wordaligned.org/articles/partitioning-with-python
# note that this solution is very expensive when n is large
# function is great since it return solution in the order
# ascending length of list so short list will be checked first
def sum_to_n(n):
    'Generate the series of +ve integer lists which sum to a +ve integer, n.'
    from operator import sub
    b, mid, e = [0], list(range(1, n)), [n]
    splits = (d for i in range(n) for d in combinations(mid, i)) 
    return (list(map(sub, chain(s, e), chain(b, s))) for s in splits)

# convert a list of numbers from sum_to_n to a list of words/phrases       
def num2words(aList, inputs):
    output = []
    start = 0
    for i in aList:
        end = start + i
        if end - start > 1:
            output.append(' '.join(inputs[start:end]))
        else:
            output.append(inputs[start])
        start += i
    return output

def main():
    
    for line in fileinput.input():
        inputs = line.strip().split(' ')
    print(inputs)
    # we need two hash tables to store 
    # 1. words/phrases that have been checked and exist
    # 2. words/phrases do not exist in Spotify's database. 
    # This will drastically reduce the computing time
    word_dict = {}
    none_dict = {}
    f = open('output.txt', 'w')
    for i in sum_to_n(len(inputs)):
        split_words = num2words(i, inputs)
        none_keys = list(none_dict.keys())
        keys = list(word_dict.keys())

        # if any phrase in the none_dict, split_words is not
        # a valid combination. No need to check further.
        terminate = 1
        if not any(list(map(lambda x: x in none_keys, split_words))):
            output = []
            for sp in split_words:
                # if the the phrase has been checked, look up value
                # else find its track
                res = word_dict[sp] if sp in keys else find_track(sp)
                if res == None:
                    none_dict[sp] = None
                    terminate = 0
                    break
                else:
                    output.append(res)
                    word_dict[sp] = res
            # if all phrases exist in spotify, return tracks
            if terminate == 1:
                for tr in output:
                    f.write(tr + "\n")
                f.close()
                return
                
    # otherwise, we don't have a possible combo
    f.write("No possible combination of tracks found.\n")
    f.close()
    return

if __name__ == "__main__":
    main()