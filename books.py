import sellerservice
from pprint import pprint
from collections import OrderedDict

keepalive = True
yes = ('yes', 'y')

def interaction_loop():
    k = s = b = True
    while k:
        keywords = raw_input('Input keywords to search by or q to quit:\n')
        keywords = keywords.split()

        books = sellerservice.search_keywords(keywords)
        if not books:
            print "There were no matches for the keywords " + ", ".join(keywords)
        else:
            k = False
    while s:
        print "ID\tRating\t\t\tPrice\tTitle and Author(s)"
        ids = OrderedDict()
        i = 1
        for index, key in enumerate(books):
            ids[str(index)] = key
        for index, isbn in ids.iteritems():
            book = books[isbn]
            # pprint(book)
            if 'rating' not in book:
                rating = "No ratings found"
            else:
                rating = unicode(book['rating']) + u' over ' + unicode(book['ratings_count']) + u' reviews'
            print u"{}\t{}\t{}\t{} by {}".format(
                index, 
                rating, 
                book['price'].FormattedPrice if book['price'] else 'NA', 
                book['title'],  
                u"; ".join(book['authors'])
            )

        selection = raw_input('Please write the IDs of the books to buy or q to quit:\n')
        if selection is 'q':
            return
        selection = selection.split()
        total = 0
        tobuy = list()
        for ident in selection:
            if ident not in ids:
                print "ID {} not valid, skipping"
                continue
            book = books[ids[ident]]
            if not book['price']:
                print "{} has no list price, skipping".format(book['title'])
                continue
            tobuy.append(book)
            total += book['price'].Amount
        if not len(tobuy): 
            s = raw_input("No books selected. Press q to quit or Enter to see the list of matches again:\n") is not 'q'
            if not s: return
        else:
            s = False

    while b:
        print total
        service = raw_input("""
            About to buy {} books for ${}. Please select payment method:
            1: Visa (WS-I)
            2: Online payment (REST)
            q: Quit
            """.format(len(tobuy), float(total) / 100))
        if service is 'q':
            return
        elif service is '1':
            buy_visa(total)
        elif service is '2':
            buy_rest(total)
        else:
            print "Selection not recognized"
            continue
        b = False
    print "Thank you for your purchase"

def buy_visa(total):
    print "Please input card information (DO NOT input real data, this is NOT SECURE)"
    number = ""
    while not number.startswith('4620'):
        number = raw_input("Card number (16 digits, starts with 4620):\n")
    card = {
        'number': number,
        'owner': raw_input("Owner name:\n"),
        'validYear': raw_input("Valid (Year):\n"),
        'validMonth': raw_input('Valid (Month):\n'),
        'csv': raw_input('Security code:\n')
    }
    sellerservice.make_wsi_bank_transfer(total, card, "FakeAccount")

def buy_rest(total):
    print "Please input fake account information"
    sellerservice.make_rest_bank_transfer(
        username=raw_input("Username:\n"),
        fromaccount=raw_input("Account:\n"),
        toaccount="FakeAccount",
        amount=total
    )
    

if __name__ == '__main__':
    while(keepalive):
        interaction_loop()
        keepalive = raw_input('Search again?\n').lower() in yes
    print "Bye"