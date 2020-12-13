from ka.models import *
import random
import string
from ka import bcrypt
from datetime import datetime, timedelta
from string import ascii_lowercase, ascii_uppercase, digits, capwords


#*************************************************
#  Random inputs
#*************************************************


non_english_unicode_chars = 'ēĒæåôἀὥ㐁ぅהࢢ😍'
chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + non_english_unicode_chars


def rname():
    length = random.choice(range(3, 200))
    return ''.join(random.choice(chars) for i in range(length))


def rtitle():
    return capwords(rname())


def rint(start, end):
    return random.choice(range(start, end))

def make_timestamp():
    base_date = datetime.utcnow()
    date = base_date + timedelta(days=random.choice(range(-400,0)))
    return date


#*************************************************
#  Users
#*************************************************


def make_user(username):
    chars = ascii_lowercase + ascii_uppercase + digits
    password = str([random.choice(chars) for i in range(10)])
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(name=username)
    user.email = username + '@example.com'
    user.password = hashed_password
    return user


def make_default_users():
    paul = make_user('Paul')
    irulan = make_user('Irulan')
    channi = make_user('Channi')
    players = [paul, irulan, channi]
    return players



#*************************************************
#  Score
#*************************************************


def make_score(composer) -> Score:
    title = rtitle()
    s = Score()
    s.name = title
    s.composer = composer
    s.text = random.choice(content_strings)
    s.count_plays = random.choice(range(0, 1000))
    s.count_favorites = random.choice(range(0, 1000))
    s.for_players = random.choice(for_players)
    s.created = make_timestamp()

    return s


#*************************************************
#  Post
#*************************************************


def make_post(composer) -> Post:
    title = rtitle()
    p = Post()
    p._name = title
    p.composer = composer
    p.text = random.choice(content_strings)
    p.count_plays = random.choice(range(0, 1000))
    p.count_favorites = random.choice(range(0, 1000))
    p.created = make_timestamp()

    return p


#*************************************************
#  Measure
#*************************************************


def make_measures(count, score):
    measures = []
    for i in range(0, count):
        title = make_ordinal(i) + " measure"
        tempo = random.choice(tempos)
        dynamic = random.choice(dynamics)

        text = random.choice(content_strings)
        seconds = random.choice(range(20, 300))
        m = Measure()
        m.name = title
        m.score = score
        m.ordinal = i
        m.tempo = tempo
        m.dynamic = dynamic
        m.text = text
        m.duration = seconds
        m.created = datetime.utcnow()
        measures.append(m)

    return measures


def make_ordinal(n):
    '''
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    '''
    # source: https://stackoverflow.com/a/50992575
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix



# Book quotes to use in creating test objects.

a = """They loved each other, not driven by necessity, by the "blaze of passion" often falsely ascribed to love. They loved each other because everything around them willed it, the trees and the clouds and the sky over their heads and the earth under their feet."""

b = """You and I, it's as though we have been taught to kiss in heaven and sent down to earth together, to see if we know what we were taught."""

c = """Perhaps, after all, romance did not come into one's life with pomp and blare, like a gay knight riding down; perhaps it crept to one's side like an old friend through quiet ways; perhaps it revealed itself in seeming prose, until some sudden shaft of illumination flung athwart its pages betrayed the rhythm and the music, perhaps. . . perhaps. . .love unfolded naturally out of a beautiful friendship, as a golden-hearted rose slipping from its green sheath."""

d = """Once, during a visit to her studio many years before, the bowler hat had caught Tomas's fancy. He had set it on his head and looked at himself in the large mirror which, as in the Geneva studio, leaned against the wall. He wanted to see what he would have looked like as a nineteenth-century mayor. When Sabina started undressing, he put the hat on her head. There they stood in front of the mirror (they always stood in front of the mirror while she undressed), watching themselves. She stripped to her underwear, but still had the hat on her head. And all at once she realized they were both excited by what they saw in the mirror.

What could have excited them so? A moment before, the hat on her head had seemed nothing but a joke. Was excitement really a mere step away from laughter?

Yes. When they looked at each other in the mirror that time, all she saw for the first few seconds was a comic situation. But suddenly the comic became veiled by excitement: the bowler hat no longer signified a joke; it signified violence; violence against Sabina, against her dignity as a woman. She saw her bare legs and thin panties with her pubic triangle showing through. The lingerie enhanced the charm of her femininity, while the hard masculine hat denied it, violated and ridiculed it. The fact that Tomas stood beside her fully dressed meant that the essence of what they both saw was far from good clean fun (if it had been fun he was after, he, too, would have had to strip and don a bowler hat); it was humiliation. But instead of spurning it, she proudly, provocatively played it for all it was worth, as if submitting of her own will to public rape; and suddenly, unable to wait any longer, she pulled Tomas down to the floor. The bowler hat rolled under the table, and they began thrashing about on the rug at the foot of the mirror."""

e = """I’m glad it found its way here,’ he said, and reached over and touched his finger very delicately to the edge of one of its straps, near my collarbone, but instead of pushing it down and off my shoulder as I thought he would, he ran his finger slowly along then upper edge of my bra in front and then traced it all the way down around the bottom. I watched his face while he did this. It seemed more intimate than kissing him had. By the time he’d finished outlining the whole thing, he’d barely touched me and yet I was so wet I could hardly stand up."""

f = """She drew him toward her with her eyes, he inclined his face toward hers and lay his mouth on her mouth, which was like a freshly split-open fig. For a long time he kissed Kamala, and Siddhartha was filled with deep astonishment as she taught him how wise she was, how she ruled him, put him off, lured him back... each one different from the other, still awaiting him. Breathing deeply, he remained standing and at this moment he was like a child astonished by the abundance of knowledge and things worth learning opening up before his eyes."""

g = """When she saw that he was dissolved with pleasure, she stopped, divining that perhaps if she deprived him now he might make a gesture towards fulfillment. At first he made no motion. His sex was quivering, and he was tormented with desire… Marianne grew desperate. She pushed his hand away, took his sex into her mouth again, and with her two hands she encircled his sexual parts, caressed him and absorbed him until he came. He leaned over with gratitude, tenderness, and murmured, ‘You are the first woman, the first woman, the first woman…'"""

# one more, with non-english chars
h = """😍 Lorem ipsum dolor sit amet, 㐁consectetur  ēἀぅ adipiscing elit, sed do eiusࢢmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliqôuip ex ea commodo consequat. Duis aute iruære dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. ExcepĒåteur sint occaecat cupidatat non proident, sunt in culpa qui officiaה deseruὥnt mollit anim id est laborum."""

content_strings = [a,b,c,d,e,f,g,h]


# Random word strings to use in generating titles

words_1 = """tank
sky
general
terrific
wait
clean
serve
natural
joyous
move
daffy
wakeful
plot
skin
few
van
ēcharœ
decorous
shelf
need
whimsical
tan
suit
handle""".split()

words_2 = """cough
clear
interfere
introduce
encourage
nail
repeat
remind
😍
mark
whirl
visit
follow
dare
plan
nest""".split()

words_3 = """thundering
numberless
bawdy
gleaming
big
awful
noiseless
dizzy
lush
natural
scandalous
laughable
versed
short
ultra
squalid
calculating
symptomatic
imaginary""".split()

title_strings = words_1 + words_2 + words_3




