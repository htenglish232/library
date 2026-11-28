from dataclasses import dataclass, field

@dataclass
class Lesson:
    title: str
    questions: list = field(default_factory=list)
    targets: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)
    review_slots: list = field(default_factory=list)

    def add(self, ident, page, kind, answer, explanation, **geometry):
        solutions = ' / '.join(answer) if isinstance(answer, list) else answer
        self.questions.append(dict(id=ident, page=page-1, kind=kind, ans=answer,
                                   explanation=f"Đáp án: {solutions}.\n{explanation}", **geometry))

    def mark(self, ident, page, answer, explanation, kind, options):
        self.add(ident, page, kind, answer, explanation, opts=options)

    def fill(self, ident, page, answer, explanation, rect, choices=None, group=None):
        self.add(ident,page,'word' if choices else 'entry',answer,explanation,rect=rect,choices=choices,group=group)

    def links(self, name, page, points):
        self.targets[name] = dict(page=page-1,points=points)

    def match(self, ident, page, answer, explanation, point, link):
        self.add(ident,page,'match',answer,explanation,**{'from':point,'link':link})

lessons={}
a_an=['a','an']
articles=['a','an','the']
meanings={
    'ant':'con kiến','watch':'đồng hồ đeo tay','umbrella':'chiếc ô','desk':'bàn học',
    'orange':'quả cam','piano':'đàn dương cầm','elephant':'con voi','cap':'mũ lưỡi trai',
    'owl':'con cú','bear':'con gấu','iguana':'cự đà','alligator':'cá sấu mõm ngắn',
    'zebra':'ngựa vằn','book':'quyển sách','house':'ngôi nhà','ostrich':'đà điểu',
    'igloo':'nhà tuyết','robot':'người máy','egg':'quả trứng','apple':'quả táo','flower':'bông hoa',
    'mirror':'cái gương','teacher':'cô giáo','girl':'bé gái','moon':'Mặt Trăng','sun':'Mặt Trời',
    'sky':'bầu trời','Earth':'Trái Đất','cloud':'đám mây','bird':'con chim','bike':'xe đạp',
    'butterfly':'con bướm','snail':'con ốc sên'
}

def article(noun, key, why=None, example=None, opts=articles):
    word=key.lower()
    if why is None:
        sound = 'nguyên âm' if word=='an' else 'phụ âm'
        why = f'{noun} bắt đầu bằng âm {sound}, nên dùng {word} khi giới thiệu một {meanings[noun]}.'
    wrong=[]
    for other in opts:
        if other==word:
            continue
        if other=='the':
            wrong.append('the dùng khi người nghe đã biết chính xác em nói về ai hoặc vật nào')
        else:
            typ='phụ âm' if other=='a' else 'nguyên âm'
            wrong.append(f'{other} giới thiệu một người hoặc vật chưa xác định, trước âm {typ}')
    return (f'{noun} nghĩa là {meanings[noun]}. {why}'
            + (' ' + '. '.join(part[0].upper()+part[1:] for part in wrong) + '.' if wrong else '')
            + (f'\nVí dụ: {example[0]}\n{example[1]}' if example else ''))

def article_fill(lesson,ident,page,noun,key,rect,why=None,example=None,opts=articles):
    display=[x.capitalize() for x in opts] if key[0].isupper() else opts
    lesson.fill(ident,page,key,article(noun,key,why,example,opts),rect,display)

u=lessons['Unit 02']=Lesson('A / An + Noun')
for num,noun,key,x,y in [
    (2,'elephant','an',404,960),(3,'cap','a',739,960),(4,'owl','an',140,1213),
    (5,'bear','a',432,1213),(6,'iguana','an',720,1213)
]:
    u.mark(f'A{num}',1,key,article(noun,key,opts=a_an),'circle',
           [('a',[x,y,37,42],[x+4,y+5,29,32]),('an',[x+38,y,54,42],[x+41,y+5,44,32])])
rows=[('ant',168),('watch',285),('umbrella',403),('desk',521),('orange',640),('piano',758)]
u.links('B',2,{n:[568,y] for n,y in rows if n!='umbrella'})
for num,noun,key,y0,y in [(2,'desk','a',286,521),(3,'orange','an',404,640),(4,'piano','a',523,758),(5,'ant','an',641,168),(6,'watch','a',760,285)]:
    u.match(f'B{num} nối',2,noun,f'{noun} là {meanings[noun]}. Hình bên trái cho thấy một phần của đúng vật hoặc con vật đó. Cụm đầy đủ là {key} {noun}.',[257,y0],'B')
    article_fill(u,f'B{num} mạo từ',2,noun,key,[735,y-19,75,37],opts=a_an)
bank=['alligator','book','house','igloo','elephant','ostrich','robot']
for key,x,yy,right in [('a',120,[1104,1170,1235],['book','house','robot']),('an',707,[1036,1102,1167,1232],['alligator','elephant','ostrich','igloo'])]:
    examples=', '.join(f'{word} ({meanings[word]})' for word in right)
    counterpart='an' if key=='a' else 'a'
    for i,y in enumerate(yy,1):
        u.fill(f'C {key} {i}',2,right,
               f'{key} đứng trước âm '+('phụ âm' if key=='a' else 'nguyên âm')+f'. Các từ hợp với cột này là {examples}. Để các từ còn lại vào cột {counterpart}. Mỗi từ điền một lần.',
               [x,y-35,194,36],bank,'C')
for num,noun,key,y in [(2,'egg','an',960),(3,'orange','an',1030),(4,'flower','a',1101),(5,'watch','a',1171),(6,'mirror','a',1241)]:
    example=(f'I have {key} {noun}.',f'Em có một {meanings[noun]}.')
    article_fill(u,f'D{num} mạo từ',3,noun,key,[207,y-35,122,35],example=example,opts=a_an)
    u.fill(f'D{num} danh từ',3,noun,f'{noun} là {meanings[noun]}. Nhìn đồ vật bạn số {num} đang cầm hoặc đeo để chọn từ. Các từ còn lại gọi tên vật khác.\n{example[0]}\n{example[1]}',[336,y-35,219,35],['egg','mirror','watch','orange','flower'])

for question in u.questions:
    if question['kind']=='word' and question['id'][0] in ('B','D'):
        question['kind']='direct'
        question.pop('choices',None)

u=lessons['Unit 03']=Lesson('The + Noun')
def unique(n):
    return f'Trong bài, ta nói về {meanings[n]} duy nhất mà ai cũng biết, nên dùng the.'
def again(n):
    return f'Câu trước đã giới thiệu {meanings[n]}. Khi nhắc lại đúng đối tượng đó, em dùng the. Ở đầu câu viết The.'
for num,noun,key,x,y,first in [(2,'girl','a',394,903,'a'),(3,'moon','the',686,902,'a'),(4,'ant','an',100,1179,'an'),(5,'sun','the',394,1177,'a'),(6,'orange','an',685,1176,'an')]:
    u.mark(f'A{num}',1,key,article(noun,key,unique(noun) if key=='the' else None,opts=[first,'the']),'tick',
           [(first,[x,y,127,37],[x+7,y+4,33,29]),('the',[x,y+37,127,37],[x+7,y+41,33,29])])
for ident,noun,key,x,y,why,example in [
    ('B2','owl','an',465,320,None,('It is an owl.','Đó là một con cú.')),
    ('B3','sky','the',736,321,unique('sky'),('It is the sky.','Đó là bầu trời.')),
    ('B4.1','teacher','a',159,566,None,('She is a teacher.','Cô ấy là giáo viên.')),
    ('B4.2','teacher','the',168,616,'Câu trước đã giới thiệu cô giáo. Bây giờ em đang nói về chính cô giáo đó.',('Look at the teacher.','Hãy nhìn cô giáo.')),
    ('B5.1','Earth','the',436,566,unique('Earth'),('It is the Earth.','Đó là Trái Đất.')),
    ('B5.2','Earth','The',382,616,again('Earth'),('The Earth is round.','Trái Đất hình tròn.')),
    ('B6.1','apple','an',718,567,None,('It is an apple.','Đó là một quả táo.')),
    ('B6.2','apple','The',665,616,again('apple'),('The apple is red.','Quả táo màu đỏ.'))
]:
    article_fill(u,ident,2,noun,key,[x,y-31,73,32],why,example)
u.links('C',2,{'moon':[572,948],'bear':[572,1075],'sun':[572,1203]})
for num,noun,key,ly,y1,x1,y2,examples in [
    (2,'sun','the',947,1189,659,1239,('It is the sun. The sun is bright.','Đó là Mặt Trời. Mặt Trời rất sáng.')),
    (3,'bear','a',1075,1062,713,1111,('There is a bear. The bear is brown.','Có một con gấu. Con gấu có màu nâu.')),
    (4,'moon','the',1202,934,660,985,('It is the moon. The moon is yellow.','Đó là Mặt Trăng. Mặt Trăng có màu vàng.'))
]:
    u.match(f'C{num} nối',2,noun,f'Hình số {num} là {meanings[noun]}. Đọc danh từ trong ô bên phải để tìm đúng hình.\n{examples[0]}\n{examples[1]}',[278,ly],'C')
    article_fill(u,f'C{num}.1',2,noun,key,[x1,y1-31,73,32],unique(noun) if key=='the' else None,examples)
    article_fill(u,f'C{num}.2',2,noun,'The',[607,y2-31,73,32],again(noun),examples)
for num,noun,y,x,description,translated in [
    (2,'cloud',988,430,'white','màu trắng'),(3,'bird',1059,410,'blue','màu xanh dương'),
    (4,'bike',1129,414,'new','mới'),(5,'butterfly',1200,467,'yellow','màu vàng'),
    (6,'snail',1270,419,'slow','di chuyển chậm')
]:
    example=(f'There is a {noun}. The {noun} is {description}.',f'Có một {meanings[noun]}. {meanings[noun][0].upper()+meanings[noun][1:]} {translated}.')
    article_fill(u,f'D{num}.1',3,noun,'a',[240,y-33,98,34],example=example)
    article_fill(u,f'D{num}.2',3,noun,'The',[x,y-33,98,34],again(noun),example)

meanings.update(boy='bé trai',box='cái hộp',peach='quả đào',shoe='chiếc giày',dress='chiếc váy',
                dog='con chó',cup='cái cốc',dish='cái đĩa',hat='cái mũ',sock='chiếc tất',
                bench='ghế băng',fox='con cáo',banana='quả chuối',cookie='bánh quy',
                sandwich='bánh mì kẹp',bus='xe buýt',doctor='bác sĩ',monkey='con khỉ',
                chair='cái ghế',pencil='bút chì',zoo='sở thú',computer='máy tính',octopus='bạch tuộc')

def plural(word,key=None):
    suffix='es' if word.endswith(('s','ch','sh','x')) else 's'
    answer=word+suffix
    correct_ending=next((e for e in ('ch','sh','x','s') if word.endswith(e)),'')
    if correct_ending:
        rule=f'{word} kết thúc bằng -{correct_ending}, nên thêm -es để được {answer}. Chỉ thêm -s sẽ sai chính tả.'
    else:
        rule=f'{word} không kết thúc bằng -s, -ch, -sh hay -x. Trong câu này, em chỉ cần thêm -s để được {answer}.'
    return f'{word} nghĩa là {meanings[word]}. Hình có nhiều hơn một, nên cần dùng số nhiều. {rule}'

u=lessons['Unit 04']=Lesson('Noun + -s / -es')
u.links('A',1,{'peaches':[630,820],'oranges':[630,947],'boxes':[630,1075]})
for num,noun,key,y0,y1,variants in [
    (2,'box','boxes',947,1075,[('boxs',697,81),('boxes',782,83)]),
    (3,'orange','oranges',1075,947,[('oranges',660,117),('orangees',782,122)]),
    (4,'peach','peaches',1202,820,[('peachs',669,107),('peaches',782,116)])
]:
    u.match(f'A{num} nối',1,key,plural(noun),[281,y0],'A')
    u.mark(f'A{num} khoanh',1,key,plural(noun),'circle',[(v,[x,y1-22,w,44]) for v,x,w in variants])
for i,noun,key,x,y in [(2,'shoe','s',510,324),(3,'dress','es',794,323),(4,'dog','s',221,573),
                       (5,'cup','s',506,573),(6,'dish','es',785,571)]:
    u.fill(f'B{i}',2,key,plural(noun),[x,y-29,40,30],['s','es'])
for ident,noun,key,cells in [
    ('C2','hat','hats',[(270,1071),(328,1071),(386,1071),(443,1070)]),
    ('C3','sock','socks',[(270,1170),(328,1170),(386,1170),(444,1170),(502,1170)]),
    ('C4','umbrella','umbrellas',[(95,y) for y in (823,873,922,972,1022,1071,1121,1171,1221)]),
    ('C5','bench','benches',[(269,y) for y in (872,922,972,1022,1071,1121,1170)]),
    ('C6','fox','foxes',[(443,y) for y in (872,922,972,1022,1071)])
]:
    answer_cells=[None if y==922 else [x+1,y+1,56,48] for x,y in cells]
    u.add(ident,2,'entry',key,plural(noun),rect=answer_cells[0],cells=answer_cells)
for num,noun,key,x,y,quantity in [
    (2,'banana','bananas',265,962,'three'),(3,'orange','oranges',249,1032,'four'),
    (4,'cookie','cookies',244,1102,'five'),(5,'peach','peaches',265,1172,'three'),
    (6,'sandwich','sandwiches',249,1242,'four')
]:
    u.fill(f'D{num}',3,key,plural(noun)+f'\nI eat {quantity} {key}.\nEm ăn '+{'three':'ba','four':'bốn','five':'năm'}[quantity]+f' {meanings[noun]}.',[x,y-34,218,35])

u=lessons['Review 01']=Lesson('Units 01–04')
bank=['doctor','monkey','chair','bear','pencil','teacher','zoo']
for category,nouns,x,ys,meaning in [
    ('Person',['doctor','teacher'],112,[499,557],'người'),
    ('Place',['zoo'],325,[556],'địa điểm'),
    ('Thing',['chair','pencil'],536,[497,555],'đồ vật'),
    ('Animal',['monkey','bear'],749,[496,554],'động vật')
]:
    translated=', '.join(f'{v} ({meanings[v]})' for v in nouns)
    for i,y in enumerate(ys,1):
        u.fill(f'A {category} {i}',1,nouns,
               f'{category} là nhóm danh từ chỉ {meaning}. Em có thể chọn {translated} cho cột này. Các từ khác thuộc nhóm khác.',
               [x,y-34,156,35],bank,'A')
for i,noun,key,x,y,blank_y in [(2,'desk','a',746,775,880),(3,'computer','a',297,952,1059),
                               (4,'egg','an',747,951,1057),(5,'octopus','an',297,1130,1237),(6,'watch','a',747,1129,1235)]:
    u.mark(f'B{i} khoanh',1,key,article(noun,key,opts=a_an),'circle',
           [('a',[x,y,37,42],[x+4,y+5,29,32]),('an',[x+37,y,54,42],[x+41,y+5,44,32])])
    article_fill(u,f'B{i} điền',1,noun,key,[x-4,blank_y-32,98,33],opts=a_an)
for i,noun,keys,candidates,x1,x2,y,oy,correct_opt,example,reason in [
    (2,'girl',('a','the'),['a, the','an, the','the, a'],235,494,242,267,0,
     ('There is a girl. Look at the girl.','Có một bé gái. Hãy nhìn bé gái đó.'),None),
    (3,'apple',('an','The'),['a, The','an, The','the, An'],179,368,344,377,1,
     ('It is an apple. The apple is green.','Đó là một quả táo. Quả táo có màu xanh lá.'),None),
    (4,'sky',('the','The'),['a, The','the, A','the, The'],227,386,447,474,2,
     ('Look at the sky. The sky is blue.','Hãy nhìn bầu trời. Bầu trời có màu xanh dương.'),unique('sky'))
]:
    first=article(noun,keys[0],reason,example)
    second=article(noun,keys[1],again(noun),example)
    ox=[137,399,646]
    u.mark(f'C{i} khoanh',2,candidates[correct_opt],first+'\n'+again(noun),'circle',
           [(value,[x-12,oy-22,131,44],[x-13,oy-15,28,28]) for value,x in zip(candidates,ox)])
    article_fill(u,f'C{i}.1',2,noun,keys[0],[x1,y-33,97,34],reason,example)
    article_fill(u,f'C{i}.2',2,noun,keys[1],[x2,y-33,97,34],again(noun),example)
u.links('D',2,{'bench':[589,661],'cup':[589,770],'apple':[588,879],'bus':[588,1097],'fox':[587,1206]})
for i,noun,key,ly,ry,x in [(2,'cup','s',769,784,665),(3,'bus','es',879,1110,663),
                           (4,'bench','es',987,675,697),(5,'fox','es',1096,1220,653),(6,'apple','s',1205,893,688)]:
    u.match(f'D{i} nối',2,noun,plural(noun),[248,ly],'D')
    u.fill(f'D{i} điền',2,key,plural(noun),[x,ry-30,64,31],['s','es'])


pronoun_explanations={
    'I':'I nghĩa là “em” hoặc “tôi”. Dùng I khi người nói kể về chính mình. Động từ be đi với I là am.',
    'You':'You nghĩa là “bạn” hoặc “các bạn”. Người nói dùng You khi nói trực tiếp với người nghe. Động từ be đi với You là are.',
    'He':'He nghĩa là “cậu ấy” hoặc “anh ấy”. Dùng He khi nói về một người nam. Động từ be đi với He là is.',
    'She':'She nghĩa là “cô ấy” hoặc “bạn nữ ấy”. Dùng She khi nói về một người nữ. Động từ be đi với She là is.',
    'It':'It nghĩa là “nó” hoặc “đó”. Dùng It khi nói về một đồ vật, địa điểm hoặc con vật trong bài. Động từ be đi với It là is.',
    'We':'We nghĩa là “chúng em” hoặc “chúng tôi”. Người nói là một thành viên trong nhóm. Động từ be đi với We là are.',
    'They':'They nghĩa là “họ” hoặc “chúng”. Dùng They để nói về nhiều người, đồ vật hoặc con vật ở bên ngoài nhóm người nói và người nghe. Động từ be đi với They là are.'
}

def pronoun(key,context,example=None,alts=()):
    return (context+' '+pronoun_explanations[key]
            + (f'\nVí dụ: {example[0]}\n{example[1]}' if example else '')
            + ('\nPhân biệt: '+' '.join(pronoun_explanations[x] for x in alts if x!=key) if any(x!=key for x in alts) else ''))

def two_mark(u,ident,page,answer,exp,kind,left,right,y,w,h,a,b):
    u.mark(ident,page,answer,exp,kind,[(a,[left,y,w,h]),(b,[right,y,w,h])])

u=lessons['Unit 05']=Lesson('I / You / He / She / It')
singular=['I','You','He','She','It']
for i,key,a,b,x1,x2,y,w1,w2,context in [
    (2,'You','You','He',394,533,983,104,98,'Bạn gái đang nói trực tiếp với bạn trai.'),
    (3,'She','He','She',693,827,979,92,104,'Bạn nhỏ đang nói về cô bác sĩ.'),
    (4,'I','I','She',91,223,1226,64,107,'Bạn gái nói về chính mình.'),
    (5,'He','She','He',395,538,1221,105,94,'Bạn gái đang nói về người lính cứu hỏa nam.'),
    (6,'It','It','You',693,827,1218,74,106,'Bạn nhỏ đang nói về chiếc ô tô.')
]:
    u.mark(f'A{i}',1,key,pronoun(key,context,alts=[a,b]),'tick',[
        (a,[x1,y,w1,48],[x1+w1-42,y+4,39,40]),(b,[x2,y,w2,48],[x2+w2-42,y+4,39,40])])
u.links('B',2,{'bench':[575,161],'teacher':[575,379],'nurse':[575,488],'police officer':[575,597]})
for i,noun,key,ly,ry,verb,context,vi in [
    (2,'teacher','You',270,174+218,'are','Bạn trai đang nói với thầy giáo.','Thầy là giáo viên.'),
    (3,'police officer','He',379,611,'is','Bạn trai đang nói về chú cảnh sát.','Chú ấy là cảnh sát.'),
    (4,'nurse','She',489,501,'is','Bạn trai đang nói về cô y tá.','Cô ấy là y tá.'),
    (5,'bench','It',598,174,'is','Bạn trai chỉ vào chiếc ghế băng.','Đó là một chiếc ghế băng.')
]:
    exp=pronoun(key,context,(f'{key} {verb} a {noun}.',vi))
    u.match(f'B{i} nối',2,noun,exp,[325,ly],'B')
    u.fill(f'B{i} điền',2,key,exp,[610,ry-32,73,33],singular)
for i,key,verb,noun,y,context,vi,wrong in [
    (2,'I','am','girl',955,'Bạn gái nói về bản thân.','Em là một bé gái.','You'),
    (3,'It','is','book',1082,'Bạn nhỏ đang nói về quyển sách.','Đó là một quyển sách.','I'),
    (4,'He','is','singer',1210,'Bạn nhỏ đang nói về chú ca sĩ.','Chú ấy là ca sĩ.','It')
]:
    value=f'{key} {verb} a {noun}.'
    u.fill(f'C{i}',2,value,pronoun(key,context,(value,vi),[wrong]),[589,y-37,292,38])
for i,key,verb,noun,y,context,vi in [
    (2,'I','am','girl',1017,'Bạn gái tự giới thiệu mình.','Em là một bé gái.'),
    (3,'She','is','student',1096,'Bạn nhỏ chỉ vào bạn nữ bên ngoài cửa sổ.','Bạn ấy là học sinh.'),
    (4,'He','is','teacher',1174,'Bạn nhỏ chỉ vào người nam bên ngoài cửa sổ.','Thầy ấy là giáo viên.'),
    (5,'It','is','fish',1253,'Bạn nhỏ chỉ vào con cá trong bình.','Đó là một con cá.')
]:
    u.fill(f'D{i}',3,key,pronoun(key,context,(f'{key} {verb} a {noun}.',vi)),[245,y-33,99,34],singular)

u=lessons['Unit 06']=Lesson('We / You / They')
plural_pronouns=['We','You','They']
for i,key,a,b,l,r,y,w1,w2,context in [
    (2,'It','It','They',438,486,950,44,72,'Bạn gái chỉ vào một con mèo.'),
    (3,'You','He','You',726,790,950,58,69,'Bạn trai nói trực tiếp với hai bạn.'),
    (4,'He','He','They',140,201,1210,55,75,'Bạn trai nói về một nam ca sĩ.'),
    (5,'They','It','They',438,486,1211,44,72,'Bạn gái chỉ vào hai lính cứu hỏa.'),
    (6,'You','I','You',741,777,1211,26,65,'Bạn trai đang nói trực tiếp với cô giáo.')
]:
    u.mark(f'A{i}',1,key,pronoun(key,context,alts=[a,b]),'circle',[(a,[l,y,w1,43]),(b,[r,y,w2,43])])
for i,key,noun,x,y,context,vi in [
    (2,'We','girls',396,317,'Hai bạn nữ đang nói về chính nhóm của mình.','Chúng em là các bạn nữ.'),
    (3,'You','doctors',651,315,'Bạn trai đang nói trực tiếp với hai bác sĩ.','Các cô chú là bác sĩ.'),
    (4,'You','boys',109,566,'Bạn gái đang nói trực tiếp với hai bạn nam.','Các bạn là con trai.'),
    (5,'We','singers',378,565,'Hai ca sĩ đang nói về chính họ.','Chúng tôi là ca sĩ.'),
    (6,'They','lions',670,563,'Bạn trai chỉ những con sư tử phía sau.','Đó là những con sư tử.')
]:
    u.fill(f'B{i}',2,key,pronoun(key,context,(f'{key} are {noun}.',vi)),[x,y-33,92,34],plural_pronouns)
nouns=['shoes','boys','students','firefighters']
for i,key,noun,x1,x2,y,w,context,vi in [
    (2,'We','boys',540,694,1014,153,'Hai bạn nam nói về nhóm của mình.','Chúng em là các bạn nam.'),
    (3,'They','firefighters',97,250,1262,177,'Bạn trai chỉ vào hai lính cứu hỏa.','Họ là lính cứu hỏa.'),
    (4,'They','shoes',541,695,1259,152,'Bạn trai chỉ vào một đôi giày.','Đó là đôi giày.')
]:
    example=(f'{key} are {noun}.',vi)
    u.fill(f'C{i}.1',2,key,pronoun(key,context,example),[x1,y-32,98,33],plural_pronouns)
    u.fill(f'C{i}.2',2,noun,context+f' {noun} là danh từ số nhiều phù hợp với hình.\n{example[0]}\n{vi}',[x2,y-32,w,33],nouns)
for ident,key,noun,x,y,context,vi in [
    ('D1.2','We','girls',547,239,'Hai bạn nữ nói về chính mình.','Chúng cháu là con gái.'),
    ('D2.1','They','cats',172,592,'Bà đang nói về hai con vật bà tưởng là mèo.','Chúng là mèo.'),
    ('D2.2','They','dogs',609,579,'Hai bạn giải thích rằng hai con vật là chó.','Chúng là chó.'),
    ('D3.1','You','soccer players',148,919,'Bà đang nói trực tiếp với hai bạn nữ.','Các cháu là cầu thủ bóng đá.'),
    ('D3.2','They','soccer players',425,923,'Hai bạn nữ chỉ hai cầu thủ phía bên phải.','Họ là cầu thủ bóng đá.')
]:
    u.fill(ident,3,key,pronoun(key,context,(f'{key} are {noun}.',vi)),[x,y-30,73,31],plural_pronouns)


meanings.update(car='chiếc ô tô',tree='cái cây',kite='con diều',rabbit='con thỏ',
                sofa='ghế sofa',vase='lọ hoa',table='cái bàn',picture='bức tranh',window='cửa sổ',
                television='chiếc ti vi',cars='những chiếc ô tô',benches='những ghế băng',birds='những con chim',
                dolls='những con búp bê',alligators='những con cá sấu mõm ngắn',houses='những ngôi nhà',
                books='những quyển sách',caps='những chiếc mũ lưỡi trai',pencils='những chiếc bút chì',
                shoes='những chiếc giày',blocks='những khối đồ chơi',robots='những người máy',
                balls='những quả bóng',gloves='những chiếc găng tay',ants='những con kiến',
                **{'teddy bears':'những chú gấu bông','toy cars':'những chiếc xe đồ chơi'})
dem_s=['This','That']
dem_p=['These','Those']
dem_all=dem_s+dem_p
def demonstrative(key,noun,example=True):
    near=key in ('This','These')
    multiple=key in dem_p
    adverb='gần' if near else 'xa'
    en_verb='are' if multiple else 'is'
    en_noun=noun if multiple else ('an ' if noun[0] in 'aeiou' else 'a ')+noun
    vi='Đây' if near else 'Kia'
    other=next(d for d in (dem_p if multiple else dem_s) if d!=key)
    return (f'{noun} nghĩa là {meanings[noun]}. Hình chỉ '+('nhiều' if multiple else 'một')+
            f' đối tượng ở {adverb}, nên dùng {key} với {en_verb}. {other} dùng khi đối tượng ở '+
            ('xa.' if near else 'gần.')+(f'\n{key} {en_verb} {en_noun}.\n{vi} là {meanings[noun]}.' if example else ''))

def dem_pair(u,id,page,key,noun,r1,r2,noun_bank):
    exp=demonstrative(key,noun)
    u.fill(id+'.1',page,key,exp,r1,dem_p if key in dem_p else dem_s)
    u.fill(id+'.2',page,noun,exp,r2,noun_bank)

u=lessons['Unit 07']=Lesson('This / That')
for i,key,noun,x,y in [(2,'This','car',583,917),(3,'That','watch',94,1133),(4,'This','monkey',584,1132)]:
    correct_picture='Hình trái' if key=='This' else 'Hình phải'
    u.mark(f'A{i}',1,correct_picture,demonstrative(key,noun),'tick',
           [(v,[x+170*j,y,169,126],[x+170*j+133,y+96,36,29]) for j,v in enumerate(['Hình trái','Hình phải'])])
for i,key,noun,x,y in [
    (2,'That','bench',374,304),(3,'This','umbrella',646,305),
    (4,'That','kite',104,583),(5,'This','hat',372,583),(6,'That','elephant',646,584)
]:
    exp=demonstrative(key,noun)
    u.mark(f'B{i} khoanh',2,key,exp,'circle',[('This',[x+2,y+10,44,26]),('That',[x+50,y+10,48,26])])
    u.fill(f'B{i} điền',2,key,exp,[x,y-31,97,32],dem_s)
for i,key,noun,y,x in [(2,'This','rabbit',1035,294),(3,'This','ant',1138,308),(4,'That','iguana',1241,308)]:
    dem_pair(u,f'C{i}',2,key,noun,[118,y-35,121,36],[x,y-35,121,36],['rabbit','ant','iguana','tree'])
for i,key,noun,y,w in [(2,'This','vase',871,132),(3,'This','table',962,133),(4,'That','picture',1053,134),
                       (5,'That','window',1145,133),(6,'That','television',1236,200)]:
    dem_pair(u,f'D{i}',3,key,noun,[129,y-34,132,35],[316,y-34,w,35],['vase','sofa','table','window','picture','television'])

u=lessons['Unit 08']=Lesson('These / Those')
u.notes=['Trang in 27, phần Grammar Point. Hai dòng dịch của “Those are trees” và “Those are benches” in “Đây là…”. Theo quy tắc về khoảng cách trên cùng trang, lời giải dùng “Kia là…”. Ảnh đề giữ nguyên.']
u.links('A',1,{'These':[626,1007],'Those':[626,1140]})
for i,key,noun,y in [(2,'These','cars',1023),(3,'These','benches',1121),(4,'Those','benches',1218)]:
    u.match(f'A{i}',1,key,demonstrative(key,noun),[316,y],'A')
for i,key,noun,x,y in [(2,'Those','birds',393,328),(3,'These','dolls',671,327),
                       (4,'Those','alligators',122,609),(5,'Those','houses',378,608),(6,'These','books',666,607)]:
    u.fill(f'B{i}',2,key,demonstrative(key,noun),[x,y-32,97,33],dem_p)
for i,key,noun,y in [(2,'These','caps',1062),(3,'These','pencils',1153),(4,'Those','books',1245)]:
    dem_pair(u,f'C{i}',2,key,noun,[125,y-34,138,35],[313,y-34,157,35],['caps','pencils','shoes','books'])
for i,key,noun,y in [(2,'Those','teddy bears',943),(3,'Those','robots',1031),(4,'These','dolls',1101),
                     (5,'Those','balls',1178),(6,'These','toy cars',1255)]:
    dem_pair(u,f'D{i}',3,key,noun,[209,y-33,124,34],[386,y-33,196,34],['balls','dolls','robots','blocks','toy cars','teddy bears'])

u=lessons['Review 02']=Lesson('Units 05–08')
u.notes=['Answer Key trang in 91 liệt kê thêm Review II phần C (This, That, These, Those) và D (That, This, This, These, Those, Those) ở trang in 32. PDF Review 02 trong ZIP chỉ có trang in 30–31, còn trang in 32 thuộc Unit 09. Cần giáo viên xác nhận nguồn cho C và D.']
people=['dog','teacher','student','foxes','nurse','doctors','singers','police officer']
for i,key,noun,x1,x2,y,w,verb,context,vi in [
    (2,'He','police officer',604,761,618,172,'is a','Bạn trai đang chỉ chú cảnh sát.','Chú ấy là cảnh sát.'),
    (3,'It','dog',129,285,837,144,'is a','Bạn trai đang chỉ một con chó.','Đó là một con chó.'),
    (4,'I','student',604,780,836,143,'am a','Bạn trai đang tự giới thiệu.','Em là học sinh.'),
    (5,'She','nurse',130,286,1054,144,'is a','Bạn trai đang chỉ cô y tá.','Cô ấy là y tá.'),
    (6,'We','doctors',605,759,1053,145,'are','Hai bác sĩ đang nói về chính họ.','Chúng tôi là bác sĩ.'),
    (7,'You','singers',130,284,1272,145,'are','Bạn nhỏ nói trực tiếp với hai ca sĩ.','Các bạn là ca sĩ.'),
    (8,'They','foxes',605,759,1271,145,'are','Bạn gái nói về những con cáo.','Đó là những con cáo.')
]:
    example=(f'{key} {verb} {noun}.',vi)
    u.fill(f'A{i}.1',1,key,pronoun(key,context,example),[x1,y-33,97,34],singular+['We','They'])
    u.fill(f'A{i}.2',1,noun,context+f' Danh từ phù hợp với hình là {noun}.\n{example[0]}\n{vi}',[x2,y-33,w,34],people)
for i,key,noun,keys,variants,x2,y,oy in [
    (2,'This','igloo','This',['This','That','Those'],None,409,439),
    (3,'These','gloves','These',['These','Those','This'],None,606,636),
    (4,'Those','shoes','Those',['These','Those','That'],None,802,831),
    (5,'These','ants','These, ants',['This, an ant','Those, ants','These, ants'],539,997,1029),
    (6,'That','bus','That, a bus',['This, buses','That, a bus','Those, a bus'],527,1193,1223)
]:
    exp=demonstrative(key,noun)
    u.mark(f'B{i} khoanh',2,keys,exp,'circle',
           [(v,[x-13,oy-21,179,43],[x-13,oy-13,27,27]) for x,v in zip([356,554,756],variants)])
    u.fill(f'B{i}.1',2,key,exp,[344,y-33,145,34],dem_all)
    if x2:
        u.fill(f'B{i}.2',2,'ants' if i==5 else 'a bus',exp,[x2,y-33,194,34],['an ant','ants','a bus','buses'])


be_forms={'I':'am','You':'are','He':'is','She':'is','It':'is','We':'are','They':'are'}
be_short={'I':"I'm",'You':"You're",'He':"He's",'She':"She's",'It':"It's",'We':"We're",'They':"They're"}
neg_short={'am':'not','is':"isn't",'are':"aren't"}
def be_result(p,noun,negative=False):
    return f'{p} {be_forms[p]} '+('not ' if negative else '')+noun+'.'
def negative_variant(p,noun):
    return (be_short[p]+' not' if p=='I' else p+' '+neg_short[be_forms[p]])+' '+noun+'.'
def be_explain(p,noun,vi,negative=False,short=False,wrong=None,reorder=False):
    b=be_forms[p]
    pair=f'{p} {b}'
    t=f'Chủ ngữ là {p}, nên động từ be là {b}. I đi với am, he/she/it đi với is, còn you/we/they đi với are.'
    if negative:
        t+=' Đặt not ngay sau '+b+' để nói “không phải là”.'
        if short:
            contraction=(be_short[p]+' not' if p=='I' else p+' '+neg_short[b])
            t+=f' Dạng rút gọn của {pair} not là {contraction}.'
    elif short:
        t+=f' Dùng dấu nháy để rút gọn {pair} thành {be_short[p]}.'
    if wrong:
        t+=f' Cách viết {wrong} sai vì dùng nhầm dạng be hoặc sai vị trí của not.'
    if reorder:
        t+=' Bắt đầu bằng chủ ngữ, sau đó đặt động từ be'+(' và not' if negative else '')+', rồi đến phần còn lại.'
    return t+'\n'+be_result(p,noun,negative)+'\n'+vi

def be_line(u,ident,page,p,noun,vi,rect,negative=False,wrong=None):
    full=be_result(p,noun,negative)
    alt=negative_variant(p,noun) if negative else be_short[p]+' '+noun+'.'
    u.fill(ident,page,[full,alt],be_explain(p,noun,vi,negative,False,wrong),rect)

def be_order(u,ident,p,noun,vi,rect,tokens,negative=False):
    u.add(ident,3,'order',be_result(p,noun,negative),be_explain(p,noun,vi,negative,reorder=True),rect=rect,choices=tokens)

u=lessons['Unit 09']=Lesson('Pronoun + Be')
for i,p,noun,vi,a,b,x1,x2,y in [
    (2,'I','a girl','Em là một bé gái.','am','are',420,477,1007),
    (3,'You','a teacher','Thầy là giáo viên.','am','are',714,770,1005),
    (4,'He','a doctor','Chú ấy là bác sĩ.','am','is',131,191,1221),
    (5,'They','nurses','Họ là y tá.','are','am',439,498,1219),
    (6,'We','police officers','Chúng tôi là cảnh sát.','is','are',703,745,1218)
]:
    u.mark(f'A{i}',1,be_forms[p],be_explain(p,noun,vi),'circle',[(a,[x1,y,x2-x1-4,39]),(b,[x2,y,51,39])])
for i,p,noun,vi,y in [
    (2,'I','a student','Em là học sinh.',305),(3,'She','a singer','Cô ấy là ca sĩ.',429),
    (4,'You','police officers','Các chú là cảnh sát.',553),(5,'They','gloves','Đó là những chiếc găng tay.',677)
]:
    be_line(u,f'B{i}',2,p,noun,vi,[602,y-34,320,35])
for i,p,noun,vi,y in [
    (2,'You','a police officer','Chú là cảnh sát.',940),(3,'He','a firefighter','Chú ấy là lính cứu hỏa.',1003),
    (4,'She','a doctor','Cô ấy là bác sĩ.',1067),(5,'It','a computer','Đó là máy tính.',1130),
    (6,'We','girls','Chúng em là các bạn nữ.',1193),(7,'They','teachers','Họ là giáo viên.',1256)
]:
    u.fill(f'C{i}',2,be_short[p],be_explain(p,noun,vi,short=True),[527,y-35,146,36],list(be_short.values()))
for i,p,noun,vi,y,tokens in [
    (2,'It','a book','Đó là một quyển sách.',378,['a','is','It','book.']),
    (3,'They','foxes','Đó là những con cáo.',514,['are','They','foxes.']),
    (4,'I','a teacher','Tôi là giáo viên.',649,['I','teacher.','am','a']),
    (5,'She','a doctor','Cô ấy là bác sĩ.',784,['doctor.','a','She','is'])
]:
    be_order(u,f'D{i}',p,noun,vi,[343,y-38,583,39],tokens)
for i,p,noun,vi,y,wrong in [
    (2,'He','a soccer player','Cậu ấy là cầu thủ bóng đá.',1000,'He are'),
    (3,'They','igloos','Đó là những ngôi nhà tuyết.',1067,'They is'),
    (4,'It','a banana','Đó là một quả chuối.',1134,'It am'),
    (5,'We','dancers','Chúng tôi là vũ công.',1201,'We is'),
    (6,'I','a singer','Tôi là ca sĩ.',1269,'I are')
]:
    be_line(u,f'E{i}',3,p,noun,vi,[486,y-36,456,37],wrong=wrong)

u=lessons['Unit 10']=Lesson('Pronoun + Be + Not')
for i,p,noun,vi,a,b,x1,x2,y in [
    (2,'You','dancers','Các bạn không phải là vũ công.','is not','are not',585,673,1005),
    (3,'She','a teacher','Bạn ấy không phải là giáo viên.','is not','am not',138,227,1209),
    (4,'They','cats','Chúng không phải là mèo.','is not','are not',594,687,1210)
]:
    u.mark(f'A{i}',1,be_forms[p]+' not',be_explain(p,noun,vi,True),'circle',[(a,[x1,y,x2-x1-5,42]),(b,[x2,y,99,42])])
for i,p,noun,vi,y in [
    (2,'I','a student','Tôi không phải là học sinh.',299),(3,'You','teachers','Các em không phải là giáo viên.',423),
    (4,'We','boys','Chúng em không phải là các bạn nam.',549),(5,'He','a dancer','Chú ấy không phải là vũ công.',674)
]:
    be_line(u,f'B{i}',2,p,noun,vi,[577,y-34,318,35],True)
for i,p,noun,vi,y in [
    (2,'I','a painter','Tôi không phải là họa sĩ.',941),(3,'She','a doctor','Cô ấy không phải là bác sĩ.',1004),
    (4,'It','a frog','Đó không phải là một con ếch.',1067),(5,'We','pilots','Chúng tôi không phải là phi công.',1131),
    (6,'They','umbrellas','Đó không phải là những chiếc ô.',1195),(7,'He','a singer','Chú ấy không phải là ca sĩ.',1258)
]:
    first=be_short[p] if p=='I' else p
    second=neg_short[be_forms[p]]
    exp=be_explain(p,noun,vi,True,True)
    u.fill(f'C{i}.1',2,first,exp,[524,y-34,107,35],['I',"I'm",'She','He','It','We','They','You'])
    u.fill(f'C{i}.2',2,second,exp,[638,y-34,128,35],["not","isn't","aren't"])
for i,p,noun,vi,y,tokens in [
    (2,'They','socks','Đó không phải là những chiếc tất.',357,['are','They','socks.','not']),
    (3,'It','a school','Đó không phải là một ngôi trường.',487,['not','is','It','a school.']),
    (4,'I','a boy','Em không phải là bé trai.',618,['I','not','am','a boy.']),
    (5,'You','a teacher','Bạn không phải là giáo viên.',749,['You','a teacher.','not','are'])
]:
    be_order(u,f'D{i}',p,noun,vi,[339,y-37,581,38],tokens,True)
for i,p,noun,vi,y,wrong in [
    (2,'He','a taxi driver','Chú ấy không phải là tài xế taxi.',982,"He'm not"),
    (3,'They','airplanes','Đó không phải là những chiếc máy bay.',1048,"They isn't"),
    (4,'It','a lion','Đó không phải là sư tử.',1115,'It not is'),
    (5,'You','teachers','Các bạn không phải là giáo viên.',1182,'You not am'),
    (6,'I','a doctor','Tôi không phải là bác sĩ.',1249,'I are not')
]:
    if i in (2,3):
        u.fill(f'E{i}',3,[negative_variant(p,noun),be_result(p,noun,True)],be_explain(p,noun,vi,True,True,wrong),[475,y-35,455,36])
    else:
        be_line(u,f'E{i}',3,p,noun,vi,[475,y-35,455,36],True,wrong)


be_choices=['am','is','are']
subjects=['I','you','he','she','it','we','they']
cap_subjects=[p.capitalize() for p in subjects]
def be_question(p,noun,vi):
    subject=p if p=='I' else p.lower()
    verb=be_forms[p]
    sentence=f'{verb.capitalize()} {subject} {noun}?'
    return sentence,(f'Đặt {verb} trước {subject} để hỏi “có phải là … không?”. I đi với am, he/she/it đi với is, còn you/we/they đi với are.\n{sentence}\n{vi}')
def parts(u,id,page,values,rects,banks,exp):
    for i,(value,rect,bank) in enumerate(zip(values,rects,banks,strict=True),1):
        u.fill(f'{id}.{i}',page,value,exp,rect,bank)
def row(x,y,width=98,height=32):
    return [x,y-height,width,height+1]
def columns(xs,y,width=98,height=32):
    return [row(x,y,width,height) for x in xs]
def order(u,id,page,ans,ex,rect,tokens):
    u.add(id,page,'order',ans,ex,rect=rect,choices=tokens)

u=lessons['Unit 11']=Lesson('Am / Are / Is …?')
u.links('A',1,{'we / you / they':[589,1095],'he / she / it':[589,1168]})
u.match('A2',1,'we / you / they','Trong câu hỏi, Are đứng trước we, you hoặc they. Ví dụ: Are they students? → Họ có phải là học sinh không?',[347,1169],'A')
u.match('A3',1,'he / she / it','Trong câu hỏi, Is đứng trước he, she hoặc it. Ví dụ: Is she a doctor? → Cô ấy có phải là bác sĩ không?',[347,1243],'A')
short_answers=['am','are','is','not',"isn't","aren't"]
for i,p,noun,vi,yes,answer_subject,ending,x,y,xs,y2,context in [
    (2,'You','a police officer','Cô có phải là cảnh sát không?','No',"I'm",'not',570,296,[570,680,783],345,'Cô ấy là lính cứu hỏa. “No, I’m not” nghĩa là “Không, tôi không phải”.'),
    (3,'She','a doctor','Cô ấy có phải là bác sĩ không?','No','she',"isn't",91,554,[91,200,305],603,'Cô ấy là y tá. “No, she isn’t” nghĩa là “Không, cô ấy không phải”.'),
    (4,'They','pilots','Họ có phải là phi công không?','No','they',"aren't",568,555,[568,678,781],604,'Họ là cảnh sát. “No, they aren’t” nghĩa là “Không, họ không phải”.'),
    (5,'You','singers','Các bạn có phải là ca sĩ không?','Yes','we','are',90,813,[90,198,303],861,'Hai bạn đang hát. “Yes, we are” nghĩa là “Vâng, chúng tôi là ca sĩ”.'),
    (6,'He','a teacher','Chú ấy có phải là giáo viên không?','Yes','he','is',567,815,[567,676,780],864,'Chú ấy đang dạy học. “Yes, he is” nghĩa là “Vâng, chú ấy là giáo viên”.')
]:
    question,exp=be_question(p,noun,vi)
    exp+=f'\n{yes}, {answer_subject} {ending}. {context} Câu trả lời ngắn bắt đầu bằng Yes hoặc No.'
    parts(u,f'B{i}',2,[be_forms[p].capitalize(),yes,answer_subject,ending],
          [row(x,y),*columns(xs,y2)],[['Am','Is','Are'],['Yes','No'],subjects+["I'm",'I'],short_answers],exp)
for i,p,noun,vi,reply,y,xs in [
    (2,'He','a cook','Cậu ấy có phải là đầu bếp không?','he',1059,[117,527,768]),
    (3,'It','a schoolbag','Đó có phải là cặp sách không?','it',1126,[117,511,751]),
    (4,'You','dancers','Các bạn có phải là vũ công không?','we',1193,[117,531,773]),
    (5,'They','peaches','Đó có phải là những quả đào không?','they',1260,[116,549,787])
]:
    _,exp=be_question(p,noun,vi)
    b=be_forms[p]
    exp+=f'\nCâu trả lời có là “Yes, {reply} {b}.” và không rút gọn. Câu trả lời không là “No, {reply} {neg_short[b]}.”'
    rects=[row(xs[0],y,77),row(xs[1],y+1,78),row(xs[2],y+1,122)]
    parts(u,f'C{i}',2,[b.capitalize(),b,neg_short[b]],rects,[['Am','Is','Are'],be_choices,["isn't","aren't","am not"]],exp)
for i,p,noun,vi,y,tokens in [
    (2,'They','cats','Chúng có phải là mèo không?',373,['cats?','they','Are']),
    (3,'It','a school','Đó có phải là trường học không?',508,['a school?','Is','it']),
    (4,'You','a firefighter','Chú có phải là lính cứu hỏa không?',644,['a firefighter?','Are','you']),
    (5,'He','a police officer','Chú ấy có phải là cảnh sát không?',779,['he','Is','a police officer?'])
]:
    value,exp=be_question(p,noun,vi)
    order(u,f'D{i}',3,value,exp,row(340,y,586,36),tokens)
for i,p,noun,vi,y,wrong in [
    (2,'She','a dancer','Cô ấy có phải là vũ công không?',996,'Are she'),
    (3,'They','teachers','Họ có phải là giáo viên không?',1064,'They are'),
    (4,'It','an umbrella','Đó có phải là chiếc ô không?',1131,'Are it'),
    (5,'You','a pilot','Chú có phải là phi công không?',1198,'Am you'),
    (6,'I','a student','Em có phải là học sinh không?',1265,'Are I')
]:
    value,exp=be_question(p,noun,vi)
    u.fill(f'E{i}',3,value,exp+f'\nSửa {wrong} sang {value.split(" ",2)[0]} {value.split(" ",2)[1]} để có câu hỏi đúng.',row(480,y,459,36))

def wh_explain(wh,eng,vi):
    return ('Who dùng để hỏi “ai” khi nói về người. ' if wh=='Who' else 'What dùng để hỏi “cái gì” khi nói về đồ vật, nơi chốn hoặc con vật. ')+(
        'What dành cho vật, nơi chốn hoặc con vật.' if wh=='Who' else 'Who dành cho người.')+(
        f' Trong câu hỏi, đặt {wh} trước động từ be, rồi đến chủ ngữ.\n{eng}\n{vi}')
u=lessons['Unit 12']=Lesson('Who / What + Be …?')
u.links('A',1,{'He is David.':[614,1154],'They are hats.':[616,826]})
for i,wh,ans,y,oy,eng,vi in [
    (2,'Who','He is David.',988,1050,'Who is he? He is David.','Cậu ấy là ai? Cậu ấy là David.'),
    (3,'What','They are hats.',1153,1215,'What are they? They are hats.','Đó là gì? Đó là những chiếc mũ.')
]:
    exp=wh_explain(wh,eng,vi)
    u.mark(f'A{i} khoanh',1,wh,exp,'circle',[('What',[116,oy,75,40]),('Who',[199,oy,62,40])])
    u.match(f'A{i} nối',1,ans,exp,[347,y],'A')
for i,wh,p,noun,eng,vi,y in [
    (2,'What','They','gloves','What are they? They are gloves.','Đó là gì? Đó là những chiếc găng tay.',325),
    (3,'Who','She','Sally','Who is she? She is Sally.','Cô bé là ai? Cô bé là Sally.',475),
    (4,'Who','I','Jeff','Who are you? I am Jeff.','Bạn là ai? Tôi là Jeff.',625)
]:
    exp=wh_explain(wh,eng,vi)+' '+pronoun_explanations[p]
    parts(u,f'B{i}',2,[wh,p,be_forms[p]],[row(501,y),row(501,y+44),row(606,y+43)],[['Who','What'],cap_subjects,be_choices],exp)
for i,wh,b,p,x,y,company,vi in [
    (2,'Who','are','you',602,984,'We are Susan and Karen.','Các bạn là ai? Chúng tôi là Susan và Karen.'),
    (3,'Who','is','he',97,1229,'He is Jack.','Cậu ấy là ai? Cậu ấy là Jack.'),
    (4,'What','is','it',603,1225,'It is an octopus.','Đó là gì? Đó là một con bạch tuộc.')
]:
    parts(u,f'C{i}',2,[wh,b,p],columns([x,x+105,x+210],y),[['Who','What'],be_choices,subjects],
          wh_explain(wh,f'{wh} {b} {p}? {company}',vi))
for i,wh,p,name,y,tokens,question,vi in [
    (2,'Who','He','David',360,['David.','He','is'],'Who is he?','Cậu ấy là ai? Cậu ấy là David.'),
    (3,'What','They','shoes',520,['are','shoes.','They'],'What are they?','Đó là gì? Đó là những chiếc giày.'),
    (4,'Who','They','Charles and George',679,['They','Charles and George.','are'],'Who are they?','Họ là ai? Họ là Charles và George.')
]:
    value=be_result(p,name)
    order(u,f'D{i}',3,value,wh_explain(wh,question+' '+value,vi)+' Câu trả lời bắt đầu bằng chủ ngữ, rồi dùng động từ be.',row(402,y,500,36),tokens)
for i,wh,y,eng,vi in [
    (2,'Who',1029,'Who is she? She is Sue.','Cô bé là ai? Cô bé là Sue.'),
    (3,'What',1141,'What is it? It is a rabbit.','Đó là gì? Đó là một con thỏ.'),
    (4,'Who',1253,'Who are they? They are my parents.','Họ là ai? Họ là bố mẹ em.')
]:
    u.fill(f'E{i}',3,eng,wh_explain(wh,eng,vi),row(156,y,730,39))

u=lessons['Review 03']=Lesson('Units 09–12')
for i,p,noun,vi,x,y in [
    (2,'We','cooks','Chúng tôi là đầu bếp.',383,472),(3,'He','a singer','Chú ấy là ca sĩ.',677,470),
    (4,'She','a doctor','Cô ấy là bác sĩ.',91,709),(5,'You','boys','Các bạn là con trai.',386,713),
    (6,'I','a student','Em là học sinh.',679,708)
]:
    parts(u,f'A{i}',1,[p,be_forms[p]],columns([x,x+75],y,69),[cap_subjects,be_choices],be_explain(p,noun,vi))
u.links('B',1,{'ca sĩ':[695,887],'y tá':[695,994],'ô tô':[696,1214]})
for i,p,noun,vi,key,alt,x,y,start,end,ty,point,clue in [
    (2,'It','a bus','Đó không phải là xe buýt.', "isn't","aren't",163,997,198,260,1014,'ô tô','Trong hình là ô tô.'),
    (3,'We','dancers','Chúng tôi không phải là vũ công.',"aren't","isn't",187,1106,255,200,1123,'ca sĩ','Trong hình là hai ca sĩ.'),
    (4,'She','a doctor','Cô ấy không phải là bác sĩ.',"isn't","aren't",195,1215,207,255,1232,'y tá','Trong hình là cô y tá.')
]:
    exp=be_explain(p,noun,vi,True,True)+' '+clue
    u.mark(f'B{i} khoanh',1,key,exp,'circle',[(key,[end,ty-13,53,26]),(alt,[start,ty-13,55,26])])
    u.fill(f'B{i} điền',1,key,exp,row(x,y,170 if i==2 else 123),[key,alt])
    u.match(f'B{i} nối',1,point,exp,[459,y],'B')
for i,p,noun,vi,ansp,ansb,xs,y,xe,ye in [
    (2,'It','a school','Đó có phải là trường học không?','it','is',[539,645],313,[598,704],363),
    (3,'He','a student','Chú ấy có phải là học sinh không?','he',"isn't",[94,199],600,[143,248],650),
    (4,'They','doctors','Họ có phải là bác sĩ không?','they',"aren't",[538,642],596,[578,682],621)
]:
    _,exp=be_question(p,noun,vi)
    exp+=f' Trả lời ngắn bằng “{"Yes" if i==2 else "No"}, {ansp} {ansb}.” Hình cho biết đáp án.'
    parts(u,f'C{i}',2,[be_forms[p].capitalize(),p.lower(),ansp,ansb],
          columns(xs,y)+columns(xe,ye,height=22 if i==4 else 31),[['Am','Is','Are'],subjects,subjects,short_answers],exp)
for i,wh,value,alts,y,oy,x,eng,vi in [
    (2,'Who','Who are they?',['What are they?','Who is he?','Who are they?'],981,1017,128,'Who are they? They are my friends.','Họ là ai? Họ là các bạn của em.'),
    (3,'What','What is it?',['What is it?','Who is it?','What are they?'],1094,1129,128,'What is it? It is a school.','Đó là gì? Đó là một ngôi trường.'),
    (4,'What','They are frogs.',['It is a banana.','They are frogs.','They are my parents.'],1208,1239,325,'What are they? They are frogs.','Đó là gì? Đó là những con ếch.')
]:
    exp=wh_explain(wh,eng,vi)
    u.mark(f'D{i} khoanh',2,value,exp,'circle',[(v,[dx-13,oy-21,230,42],[dx-13,oy-14,27,27]) for v,dx in zip(alts,[141,390,659])])
    u.fill(f'D{i} điền',2,value,exp,row(x,y,371),alts)


adj_vi=dict(blue='màu xanh dương',yellow='màu vàng',round='tròn',square='hình vuông',
            big='to',small='nhỏ',red='màu đỏ',green='màu xanh lá',long='dài',short='ngắn hoặc thấp',
            brown='màu nâu',rectangular='hình chữ nhật',pink='màu hồng',happy='vui',
            sad='buồn',cold='lạnh',hot='nóng',tall='cao',pretty='xinh',ugly='xấu',hungry='đói',
            full='no',new='mới',old='cũ hoặc lớn tuổi',fat='mập',thin='gầy',handsome='đẹp trai',
            young='trẻ',thirsty='khát',cute='dễ thương',angry='tức giận',clean='sạch',fast='nhanh',
            black='màu đen',dirty='bẩn',white='màu trắng',slow='chậm',triangular='hình tam giác')
def adj_explain(adj,noun,eng,vi,other=None):
    rule=(f'Đặt {adj} trước danh từ {noun} để miêu tả danh từ. '
          if noun else f'Đặt {adj} sau am, is hoặc are để miêu tả chủ ngữ. Không dùng a/an trước tính từ đứng riêng. ')
    return f'{adj} nghĩa là {adj_vi[adj]}. '+rule+(f'{other} nghĩa là {adj_vi[other]}, khác với đặc điểm trong hình. ' if other else '')+f'\n{eng}\n{vi}'
def adjective_sentence(u,id,page,p,adj,noun,vi,rect,tokens=None):
    value=be_result(p,(adj+' '+noun if noun else adj))
    if noun and p=='It':
        value=f'It is {"an" if adj[0] in "aeiou" else "a"} {adj} {noun}.'
    exp=adj_explain(adj,noun,value,vi)
    if tokens:
        order(u,id,page,value,exp,rect,tokens)
    else:
        u.fill(id,page,value,exp,rect)

u=lessons['Unit 13']=Lesson('Adjective + Noun')
u.notes=['Trang in 46, Grammar Point. Dòng dịch in dưới “They are blue shoes” dùng “một chiếc giày”. Ảnh đề giữ nguyên. Trong lời giải A3, bản dịch dùng số nhiều.']
u.links('A',1,{'shoes':[429,951],'raincoat':[429,1134],'donuts':[430,1225]})
for i,adj,noun,value,vi,ly,x,y,w in [
    (2,'yellow','raincoat','a yellow raincoat','một chiếc áo mưa màu vàng',1042,470,1145,169),
    (3,'blue','shoes','blue shoes','những chiếc giày màu xanh dương',1134,446,963,169),
    (4,'round','donuts','round donuts','những chiếc bánh vòng tròn',1225,450,1237,167)
]:
    exp=adj_explain(adj,noun,value,vi)
    u.match(f'A{i} nối',1,noun,exp,[304,ly],'A')
    u.fill(f'A{i} điền',1,adj,exp,row(x,y,w),['blue','small','round','yellow'])
for i,p,adj,noun,vi,x,y in [
    (2,'It','square','clock','Đó là đồng hồ hình vuông.',204,286),(3,'It','big','egg','Đó là một quả trứng to.',206,366),
    (4,'It','small','egg','Đó là một quả trứng nhỏ.',206,420),(5,'They','red','apples','Đó là những quả táo màu đỏ.',246,500),
    (6,'They','green','apples','Đó là những quả táo màu xanh lá.',254,552)
]:
    eng=f'It is a {adj} {noun}.' if p=='It' else f'They are {adj} {noun}.'
    u.fill(f'B{i}',2,adj,adj_explain(adj,noun,eng,vi),row(x,y,167),['small','round','red','big','green','square'])
for i,p,adj,noun,vi,y in [
    (2,'It','long','snake','Đó là một con rắn dài.',892),(3,'It','square','window','Đó là một cửa sổ hình vuông.',1012),
    (4,'They','red','roses','Đó là những bông hồng màu đỏ.',1133),(5,'They','short','pencils','Đó là những chiếc bút chì ngắn.',1254)
]:
    adjective_sentence(u,f'C{i}',2,p,adj,noun,vi,row(442,y,485,35))
for i,p,adj,noun,vi,y,tokens in [
    (2,'It','long','tail','Đó là một cái đuôi dài.',369,['long','It is','tail.','a']),
    (3,'They','square','windows','Đó là những cửa sổ hình vuông.',504,['square','are','They','windows.']),
    (4,'They','brown','bears','Đó là những con gấu nâu.',639,['They','bears.','are','brown']),
    (5,'It','big','elephant','Đó là một con voi to.',775,['elephant.','a','It is','big'])
]:
    adjective_sentence(u,f'D{i}',3,p,adj,noun,vi,row(340,y,584,36),tokens)
for i,p,adj,noun,vi,y in [
    (2,'It','small','box','Đó là một cái hộp nhỏ.',993),(3,'It','long','ruler','Đó là một chiếc thước dài.',1060),
    (4,'They','rectangular','bags','Đó là những chiếc túi hình chữ nhật.',1127),(5,'It','pink','dress','Đó là một chiếc váy hồng.',1195),
    (6,'They','round','mirrors','Đó là những chiếc gương tròn.',1261)
]:
    adjective_sentence(u,f'E{i}',3,p,adj,noun,vi,row(534,y,406,36))

u=lessons['Unit 14']=Lesson('Be + Adjective')
u.notes=['Answer Key trang in 94, sau đáp án D1–D5 của trang 51, có thêm “4. hot, it is”, “5. full, she is”, “6. pretty, I am”. Đề Unit 14 trang 51 chỉ có D1–D5 dạng sắp xếp từ và phần E. Cần xác minh nguồn của ba dòng thừa.']
for i,p,adj,other,vi,x,y,a,b,lx,rx,lw,rw in [
    (2,'I','happy','sad','Em đang vui.',475,979,'happy','sad',487,548,51,34),
    (3,'It','cold','hot','Cốc nước lạnh.',771,979,'hot','cold',788,831,34,42),
    (4,'He','short','tall','Cậu ấy thấp.',180,1228,'tall','short',194,235,31,48),
    (5,'You','pretty','ugly','Bạn xinh.',495,1228,'pretty','ugly',499,560,52,44),
    (6,'She','hungry','full','Cô bé đang đói.',780,1229,'full','hungry',788,831,32,57)
]:
    exp=adj_explain(adj,None,be_result(p,adj),vi,other)
    u.mark(f'A{i} khoanh',1,adj,exp,'circle',[(a,[lx,y+10,lw,26]),(b,[rx,y+10,rw,26])])
    u.fill(f'A{i} điền',1,adj,exp,row(x,y,117),[a,b])
for i,p,adj,other,vi,x,y in [
    (2,'It','new','old','Nó còn mới.',345,323),(3,'She','full','hungry','Cô bé đã no.',615,451),
    (4,'He','tall','short','Cậu ấy cao.',365,581)
]:
    exp=adj_explain(adj,None,be_result(p,adj),vi)+f' {adj} trái nghĩa với {other} ({adj_vi[other]}).'
    u.fill(f'B{i}',2,adj,exp,row(x,y,116),[adj,other])
for i,p,adj,vi,x,y,pts in [
    (2,'She','hungry','Cô bé đói.',593,1193,[(96+58*z,929) for z in range(6)]),
    (3,'It','old','Quả bóng đã cũ.',816,1192,[(96+58*z,1025) for z in range(3)]),
    (4,'She','ugly','Cô ấy được mô tả là xấu.',342,1268,[(155,929+48*z) for z in range(4)]),
    (5,'I','happy','Em đang vui.',572,1267,[None]+[(385,735+48*z) for z in range(1,5)]),
    (6,'He','tall','Cậu ấy cao.',835,1265,[None]+[(500,734+48*z) for z in range(1,4)])
]:
    rect=row(x,y,116)
    cells=[None if point is None else [point[0]+1,point[1]+1,55,46] for point in pts]
    exp=adj_explain(adj,None,be_result(p,adj),vi)
    u.add(f'C{i}',2,'entry',adj,exp,rect=rect,cells=cells,extra_slot=next(rect for rect in cells if rect))
for i,p,adj,vi,y,tokens in [
    (2,'They','sad','Họ đang buồn.',362,['are','They','sad.']),(3,'He','fat','Cậu ấy mập.',498,['fat.','is','He']),
    (4,'It','cold','Cốc nước lạnh.',632,['cold.','It','is']),(5,'You','pretty','Bạn xinh.',766,['are','pretty.','You'])
]:
    adjective_sentence(u,f'D{i}',3,p,adj,None,vi,row(351,y,565,36),tokens)
for i,p,adj,vi,y in [(2,'We','fat','Chúng tôi mập.',983),(3,'I','handsome','Em đẹp trai.',1050),
                     (4,'It','new','Nó còn mới.',1117),(5,'You','full','Bạn đã no.',1183),(6,'He','young','Cậu ấy còn trẻ.',1250)]:
    adjective_sentence(u,f'E{i}',3,p,adj,None,vi,row(407,y,402,36))


def slots(*items):
    return [row(x,y,w) for x,y,w in items]
def rephrase(adj,noun,subject,verb,vi,first):
    second=f'The {noun} {verb} {adj}.'
    return adj_explain(adj,noun,first,vi)+f'\n{second} giữ nguyên nghĩa. Trong câu này, {adj} đứng sau {verb}.'
u=lessons['Unit 15']=Lesson('Adjective + Noun = Be + Adjective')
u.notes=['Trang in 54, E4 có đề “The pretty girl is.” nhưng Answer Key trang 94 bỏ câu này. Mục E.4 và E.5 trong key tương ứng với E5 và E6 trên đề. E4 giữ nguyên trên ảnh đề và tạm không chấm cho đến khi giáo viên xác nhận.']
u.links('A',1,{'baby':[557,801],'bananas':[557,936],'girl':[558,1204]})
for i,adj,n,sub,verb,vi,eng,from_y,vals,rects,banks in [
    (2,'cute','baby','He','is','Em bé dễ thương.','He is a cute baby.',937,['a','cute','baby'],slots((658,793,50),(715,793,73),(797,793,98)),[a_an,['cute','angry','round'],['baby','girl','table']]),
    (3,'angry','girl','She','is','Cô bé đang tức giận.','She is an angry girl.',1070,['is','angry'],slots((705,1246,73),(785,1246,99)),[be_choices,['cute','angry','round']]),
    (4,'yellow','bananas','They','are','Những quả chuối màu vàng.','They are yellow bananas.',1205,['are','yellow'],slots((771,973,74),(851,973,85)),[be_choices,['yellow','angry','round']])
]:
    exp=rephrase(adj,n,sub,verb,vi,eng)
    u.match(f'A{i} nối',1,n,exp,[329,from_y],'A')
    parts(u,f'A{i}',1,vals,rects,banks,exp)
for i,adj,n,sub,verb,vi,eng,vals,rects in [
    (2,'blue','crayons','They','are','Những chiếc bút sáp màu xanh dương.','They are blue crayons.',['blue','crayons','are','blue'],
      slots((683,386,73),(764,386,122),(740,435,72),(820,435,99))),
    (3,'fat','boy','He','is','Cậu bé mập.','He is a fat boy.',['a','fat','boy','is','fat'],
      slots((160,663,50),(217,663,74),(298,663,96),(210,713,73),(291,713,143))),
    (4,'sad','girl','She','is','Cô bé đang buồn.','She is a sad girl.',['a','sad','girl','is','sad'],
      slots((645,664,49),(702,664,74),(782,664,96),(675,713,72),(755,713,148)))
]:
    parts(u,f'B{i}',2,vals,rects,[None]*len(vals),rephrase(adj,n,sub,verb,vi,eng))
for i,adj,n,sub,verb,vi,eng,x1,x2,y,w1,w2 in [
    (2,'red','flower','It','is','Bông hoa màu đỏ.','It is a red flower.',596,651,920,48,123),
    (3,'old','man','He','is','Người đàn ông lớn tuổi.','He is an old man.',574,630,985,48,121),
    (4,'big','bag','It','is','Chiếc túi to.','It is a big bag.',568,624,1052,48,122),
    (5,'hungry','dogs','They','are','Những con chó đang đói.','They are hungry dogs.',582,661,1119,72,152),
    (6,'short','girl','She','is','Cô bé thấp.','She is a short girl.',558,613,1185,49,124),
    (7,'square','watch','It','is','Đồng hồ có hình vuông.','It is a square watch.',593,650,1252,48,151)
]:
    parts(u,f'C{i}',2,[verb,adj],slots((x1,y,w1),(x2,y,w2)),[None,None],rephrase(adj,n,sub,verb,vi,eng))
for i,adj,sub,verb,vi,y,tokens in [
    (2,'handsome','The boy','is','Cậu bé đẹp trai.',368,['handsome.','The boy','is']),
    (3,'fast','The horses','are','Những con ngựa chạy nhanh.',504,['The horses','fast.','are']),
    (4,'old','The woman','is','Người phụ nữ lớn tuổi.',639,['old.','is','The woman']),
    (5,'round','The table','is','Cái bàn hình tròn.',774,['is','The table','round.'])
]:
    eng=f'{sub} {verb} {adj}.'
    order(u,f'D{i}',3,eng,adj_explain(adj,None,eng,vi),row(353,y,565,36),tokens)
for i,adj,sub,verb,vi,y in [
    (2,'square','The windows','are','Những chiếc cửa sổ có hình vuông.',991),
    (3,'clean','The house','is','Ngôi nhà sạch.',1059),
    (5,'small','The shoes','are','Những chiếc giày nhỏ.',1193),
    (6,'black','The dogs','are','Những con chó màu đen.',1260)
]:
    eng=f'{sub} {verb} {adj}.'
    u.fill(f'E{i}',3,eng,adj_explain(adj,None,eng,vi),row(538,y,397,36))

number_words='one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty'.split()
number_vi='một,hai,ba,bốn,năm,sáu,bảy,tám,chín,mười,mười một,mười hai,mười ba,mười bốn,mười lăm,mười sáu,mười bảy,mười tám,mười chín,hai mươi'.split(',')
def count_exp(number,noun,vi):
    i=number_words.index(number)
    verb='is' if i==0 else 'are'
    rule='Dùng one với danh từ số ít và There is.' if i==0 else f'Dùng {number} với danh từ số nhiều và There are.'
    return f'{number} nghĩa là {number_vi[i]}. Viết số đếm trước danh từ. {rule}\nThere {verb} {number} {noun}.\nCó {number_vi[i]} {vi}.'
u=lessons['Unit 16']=Lesson('Numbers')
for i,number,noun,vi,key,y,w1,w2 in [
    (2,'five','boxes','cái hộp','Hình trái',966,194,194),
    (3,'ten','marbles','viên bi','Hình phải',1067,194,194),
    (4,'twelve','eggs','quả trứng','Hình trái',1167,194,194)
]:
    u.mark(f'A{i}',1,key,count_exp(number,noun,vi),'tick',
           [(choice,[x,y,w,89],[x+w-38,y+55,37,33]) for choice,x,w in [('Hình trái',480,w1),('Hình phải',699,w2)]])
for i,number,noun,vi,y in [(2,'eight','erasers','cục tẩy',364),(3,'sixteen','crayons','chiếc bút sáp',508),(4,'nineteen','books','quyển sách',653)]:
    u.fill(f'B{i}',2,number,count_exp(number,noun,vi),row(487,y,147),['eight','four','sixteen','nineteen'])
for i,number,noun,vi,x1,x2,y in [(2,'one','lion','con sư tử',705,833,1055),(3,'eleven','candles','cây nến',219,347,1269),
                                (4,'twenty','roses','bông hồng',726,854,1266)]:
    parts(u,f'C{i}',2,[number,noun],slots((x1,y,121),(x2,y,116)),[None,None],count_exp(number,noun,vi))
for i,number,noun,vi,y,tokens in [
    (2,'eighteen','cookies','chiếc bánh quy',374,['are','eighteen','There','cookies.']),
    (3,'thirteen','balls','quả bóng',509,['There','balls.','are','thirteen']),
    (4,'seven','marbles','viên bi',644,['marbles.','are','seven','There']),
    (5,'one','bird','con chim',778,['is','bird.','There','one'])
]:
    value=f'There {"is" if number=="one" else "are"} {number} {noun}.'
    order(u,f'D{i}',3,value,count_exp(number,noun,vi),row(349,y,573,36),tokens)
for i,number,noun,vi,y in [
    (2,'one','chair','chiếc ghế',995),(3,'ten','balls','quả bóng',1062),(4,'eleven','books','quyển sách',1128),
    (5,'one','door','cánh cửa',1195),(6,'fourteen','eggs','quả trứng',1262)
]:
    value=f'There {"is" if number=="one" else "are"} {number} {noun}.'
    u.fill(f'E{i}',3,value,count_exp(number,noun,vi),row(513,y,418,36))

u=lessons['Review 04']=Lesson('Units 13–16')
for i,p,adj,noun,eng,vi,x,y,w in [
    (2,'They','blue','shoes','They are blue shoes.','Đó là những chiếc giày xanh dương.',507,544,87),
    (3,'It','small','ball','It is a small ball.','Đó là một quả bóng nhỏ.',762,542,88),
    (4,'They','round','donuts','They are round donuts.','Đó là những chiếc bánh vòng tròn.',205,757,88),
    (5,'It','yellow','raincoat','It is a yellow raincoat.','Đó là một chiếc áo mưa màu vàng.',469,754,86),
    (6,'It','triangular','ruler','It is a triangular ruler.','Đó là chiếc thước hình tam giác.',763,752,113)
]:
    u.fill(f'A{i}',1,adj,adj_explain(adj,noun,eng,vi),row(x,y,w),['yellow','small','round','blue','long','triangular'])
u.links('B',1,{'short':[589,1010],'sad':[589,900],'full':[591,1229]})
for i,p,adj,vi,y,ry,tokens in [
    (2,'He','short','Cậu ấy thấp.',1010,1006,['He','short.','is']),
    (3,'I','sad','Em đang buồn.',1120,900,['am','I','sad.']),
    (4,'She','full','Cô ấy đã no.',1230,1219,['is','She','full.'])
]:
    value=be_result(p,adj)
    exp=adj_explain(adj,None,value,vi)
    u.match(f'B{i} nối',1,adj,exp,[380,y],'B')
    order(u,f'B{i} sắp xếp',1,value,exp,row(626,ry,291,35),tokens)
for i,adj,n,sub,verb,vi,eng,vals,rs in [
    (2,'dirty','car','It','is','Chiếc xe bị bẩn.','It is a dirty car.',['a','dirty','car','is','dirty'],
     slots((492,271,49),(548,271,112),(668,271,150),(553,321,73),(634,321,118))),
    (3,'fast','horses','They','are','Những con ngựa chạy nhanh.','They are fast horses.',['fast','horses','are','fast'],
     slots((554,396,97),(658,396,145),(596,446,74),(676,446,97))),
    (4,'handsome','boy','He','is','Cậu bé đẹp trai.','He is a handsome boy.',['a','handsome','boy','is','handsome'],
     slots((516,521,49),(572,521,169),(748,521,129),(565,570,74),(646,570,168))),
    (5,'angry','girl','She','is','Cô bé đang tức giận.','She is an angry girl.',['an','angry','girl','is','angry'],
     slots((521,646,49),(577,646,112),(697,646,148),(552,695,97),(656,695,120)))
]:
    parts(u,f'C{i}',2,vals,rs,[None]*len(vals),rephrase(adj,n,sub,verb,vi,eng))
for i,number,noun,vi,choices,y,oy,xs,correct_i,w in [
    (2,'eight','robots','người máy',['eight robot','robots eight','eight robots'],970,1010,[130,422,696],2,265),
    (3,'thirteen','pencils','chiếc bút chì',['pencils thirteen','thirteen pencils','thirteen pencil'],1083,1116,[135,426,696],1,289),
    (4,'twenty','balls','quả bóng',['twenty balls','balls twenty','twenty ball'],1196,1229,[135,423,693],0,265)
]:
    val=choices[correct_i];exp=count_exp(number,noun,vi)
    u.mark(f'D{i} khoanh',2,val,exp,'circle',[(v,[x-13,oy-22,203,42],[x-13,oy-13,27,27]) for v,x in zip(choices,xs)])
    u.fill(f'D{i} điền',2,val,exp,row(241,y,w),choices)


def third_person(p):
    return p in ('He','She','It')
def form(p,verb):
    return {'like':'likes','have':'has','do':'does'}[verb] if third_person(p) else verb
def verb_exp(p,verb,noun,vi,negative=False):
    v=form(p,verb)
    aux=form(p,'do')
    shown=(aux+"n't" if aux=='does' else "don't")+' '+verb if negative else v
    meaning='thích' if verb=='like' else 'có'
    opposite={'like':'likes','likes':'like','have':'has','has':'have'}[v]
    rule=(f'Dùng {shown} nghĩa là “không {meaning}”. He, she, it dùng doesn’t, còn I, you, we, they dùng don’t. Sau từ phủ định giữ nguyên {verb}.'
          if negative else f'{shown} nghĩa là “{meaning}”. Dùng {shown} sau {p}. Dùng {opposite} với nhóm chủ ngữ còn lại.')
    eng=f'{p} {shown} {noun}.'
    return shown,eng,rule+f'\n{eng}\n{vi}'
def verb_sentence(u,id,page,p,verb,noun,vi,rect,tokens=None,negative=False):
    _,eng,exp=verb_exp(p,verb,noun,vi,negative)
    if tokens:
        order(u,id,page,eng,exp,rect,tokens)
    else:
        u.fill(id,page,eng,exp,rect)
def word_pair(u,id,page,value,other,exp,blank,y,opts,mark_y,fill_width=None):
    u.mark(id+' khoanh',page,value,exp,'circle',[(v,[x,mark_y-12,w,24]) for v,x,w in opts])
    u.fill(id+' điền',page,value,exp,row(blank,y,fill_width or 103),[value,other])
u=lessons['Unit 17']=Lesson('Like / Likes')
u.links('A',1,{'sausages':[630,790],'carrots':[631,1060],'oranges':[632,1195]})
for i,p,noun,vi,ly,x,y,w in [
    (2,'He','sausages','Cậu ấy thích xúc xích.',926,689,803,122),(3,'We','oranges','Chúng em thích cam.',1061,696,1205,121),
    (4,'It','carrots','Nó thích cà rốt.',1196,673,1071,122)
]:
    value,_,exp=verb_exp(p,'like',noun,vi)
    u.match(f'A{i} nối',1,noun,exp,[331,ly],'A')
    u.fill(f'A{i} điền',1,value,exp,row(x,y,w))
for i,p,noun,vi,x,y,ox,oy in [
    (2,'They','bones','Chúng thích xương.',678,152,684,169),(3,'I','hot dogs','Em thích bánh mì xúc xích.',165,262,177,283),
    (4,'You','cucumbers','Bạn thích dưa chuột.',665,263,675,284),(5,'He','apples','Cậu ấy thích táo.',191,374,200,397),
    (6,'We','grapes','Chúng em thích nho.',658,375,668,399),(7,'They','grapes','Họ thích nho.',215,485,228,513),
    (8,'It','insects','Nó thích côn trùng.',635,486,645,516)
]:
    v,_,exp=verb_exp(p,'like',noun,vi)
    word_pair(u,f'B{i}',2,v,'likes' if v=='like' else 'like',exp,x,y,[('like',ox,35),('likes',ox+43,41)],oy)
for i,p,noun,vi,x,y in [
    (2,'He','peaches','Cậu ấy thích đào.',161,965),(3,'They','sandwiches','Họ thích bánh mì kẹp.',185,1038),
    (4,'They','cookies','Họ thích bánh quy.',185,1107),(5,'It','apples','Nó thích táo.',142,1177),(6,'It','bananas','Nó thích chuối.',141,1247)
]:
    v,_,exp=verb_exp(p,'like',noun,vi)
    u.fill(f'C{i}',2,f'{v} {noun}.',exp,row(x,y,602-x,35))
for i,p,noun,vi,y,tokens in [
    (2,'She','melons','Cô bé thích dưa lưới.',361,['likes','She','melons.']),
    (3,'I','hot dogs','Em thích bánh mì xúc xích.',497,['I','hot dogs.','like']),
    (4,'He','grapes','Cậu ấy thích nho.',632,['grapes.','likes','He']),
    (5,'We','hamburgers','Chúng em thích bánh hamburger.',767,['hamburgers.','We','like'])
]:
    verb_sentence(u,f'D{i}',3,p,'like',noun,vi,row(350,y,564,36),tokens)
for i,p,noun,vi,y in [
    (2,'He','peaches','Cậu ấy thích đào.',985),(3,'She','flowers','Cô ấy thích hoa.',1052),
    (4,'We','cats','Chúng em thích mèo.',1120),(5,'It','fish','Nó thích cá.',1187),(6,'I','oranges','Em thích cam.',1254)
]:
    verb_sentence(u,f'E{i}',3,p,'like',noun,vi,row(442,y,485,35))
u=lessons['Unit 18']=Lesson('Have / Has')
u.notes=['Trang in 65 ghi nhầm “Unit 17 Like / Likes” ở chân trang. Nội dung Have / Has và Answer Key trang 96 đều tương ứng Unit 18. Ảnh đề giữ nguyên.']
for i,p,noun,vi,x,y,ox,oy in [
    (2,'He','a robot','Cậu ấy có một người máy.',426,969,427,990),(3,'She','a doll','Cô bé có một con búp bê.',742,970,744,991),
    (4,'It','wings','Nó có cánh.',125,1237,126,1257),(5,'You','a book','Bạn có một quyển sách.',434,1238,435,1258),
    (6,'They','balls','Họ có bóng.',747,1239,747,1258)
]:
    v,_,exp=verb_exp(p,'have',noun,vi)
    word_pair(u,f'A{i}',1,v,'has' if v=='have' else 'have',exp,x,y,[('have',ox,48),('has',ox+65,36)],oy,97)
u.links('B',2,{'a robot':[628,183],'cats':[629,312],'flowers':[630,569]})
for i,p,noun,vi,ly,x,y in [
    (2,'He','a robot','Cậu ấy có một người máy.',313,686,204),
    (3,'She','flowers','Cô ấy có hoa.',442,701,590),
    (4,'We','cats','Chúng em có mèo.',570,691,333)
]:
    v,_,exp=verb_exp(p,'have',noun,vi)
    u.match(f'B{i} nối',2,noun,exp,[330,ly],'B')
    u.fill(f'B{i} điền',2,v,exp,row(x,y,122))
for i,p,noun,vi,x1,x2,y in [
    (2,'I','a watch','Em có một chiếc đồng hồ đeo tay.',142,271,1082),
    (3,'You','gloves','Bạn có găng tay.',182,311,1147),
    (4,'She','a piano','Cô ấy có một cây đàn dương cầm.',183,312,1210),
    (5,'They','hats','Họ có mũ.',197,326,1273)
]:
    v,_,exp=verb_exp(p,'have',noun,vi)
    parts(u,f'C{i}',2,[v,noun],slots((x1,y,121),(x2,y,166)),[None,None],exp)
for i,p,noun,vi,y,tokens in [
    (2,'She','a balloon','Cô bé có một quả bóng bay.',367,['has','a balloon.','She']),
    (3,'He','a skateboard','Cậu ấy có một chiếc ván trượt.',502,['a skateboard.','He','has']),
    (4,'It','legs','Nó có chân.',638,['It','legs.','has']),
    (5,'You','a book','Bạn có một quyển sách.',772,['a book.','have','You'])
]:
    verb_sentence(u,f'D{i}',3,p,'have',noun,vi,row(349,y,564,37),tokens)
for i,p,noun,vi,y in [
    (2,'He','a bike','Cậu ấy có một chiếc xe đạp.',988),(3,'She','a bag','Cô ấy có một chiếc túi.',1055),
    (4,'It','bananas','Nó có chuối.',1121),(5,'You','watches','Bạn có đồng hồ đeo tay.',1188),
    (6,'I','a teddy bear','Em có một chú gấu bông.',1255)
]:
    verb_sentence(u,f'E{i}',3,p,'have',noun,vi,row(444,y,475,36))


def neg_aux(p):
    return "doesn't" if third_person(p) else "don't"
u=lessons['Unit 19']=Lesson("Don’t / Doesn’t + Like")
u.notes=['Trang in 67, C2. Đề ghi “You like watermelons.” nhưng Answer Key trang 96 ghi “You don’t like cucumbers.”. Hai danh từ khác nhau. C2 giữ nguyên trên ảnh và tạm không chấm cho đến khi giáo viên xác nhận.']
for i,p,verb,noun,vi,x,y,positions in [
    (2,'She','like','peppers','Cô ấy không thích ớt.',400,1001,[420,523]),
    (3,'I','have','a watch','Em không có đồng hồ đeo tay.',362,1110,[368,479]),
    (4,'It','have','candles','Nó không có nến.',372,1220,[379,489])
]:
    key,_,exp=verb_exp(p,verb,noun,vi,True)
    vals=["don't "+verb,"doesn't "+verb]
    word_pair(u,f'A{i}',1,key,next(v for v in vals if v!=key),exp,x,y,
              [(v,ox,w) for v,ox,w in zip(vals,positions,[93,124])],y+20,242)
for i,p,noun,vi,x1,x2,y in [
    (2,'She','a book','Cô bé không có sách.',617,722,322),(3,'They','a ball','Họ không có bóng.',160,263,536),
    (4,'It','leaves','Cây không có lá.',585,688,539),(5,'You','a doll','Bạn không có búp bê.',145,248,754),
    (6,'He','a balloon','Cậu ấy không có bóng bay.',601,705,757)
]:
    _,_,exp=verb_exp(p,'have',noun,vi,True)
    parts(u,f'B{i}',2,[neg_aux(p),'have'],slots((x1,y,97),(x2,y,73)),[None,None],exp)
for i,p,noun,vi,y in [(3,'We','pineapples','Chúng em không thích dứa.',1150),(4,'It','carrots','Nó không thích cà rốt.',1254)]:
    verb_sentence(u,f'C{i}',2,p,'like',noun,vi,row(158,y,579,37),negative=True)
for i,p,noun,vi,y,tokens in [
    (2,'It','bones','Nó không thích xương.',375,['bones.',"doesn't",'It','like']),
    (3,'They','lemons','Họ không thích chanh.',510,['They','like',"don't",'lemons.']),
    (4,'He','peas','Cậu ấy không thích đậu Hà Lan.',646,["doesn't",'peas.','like','He']),
    (5,'We','cucumbers','Chúng em không thích dưa chuột.',781,['cucumbers.','like','We',"don't"])
]:
    verb_sentence(u,f'D{i}',3,p,'like',noun,vi,row(353,y,575,37),tokens,True)
for i,p,verb,noun,vi,y in [
    (2,'She','like','cats','Cô ấy không thích mèo.',997),(3,'They','have','a ball','Họ không có bóng.',1065),
    (4,'He','have','boots','Cậu ấy không có ủng.',1132),(5,'I','like','eggs','Em không thích trứng.',1199),
    (6,'It','have','a tail','Nó không có đuôi.',1266)
]:
    verb_sentence(u,f'E{i}',3,p,verb,noun,vi,row(515,y,428,36),negative=True)
def do_question(p,verb,noun,vi,wh=False):
    aux=form(p,'do')
    lead='What '+aux if wh else aux.capitalize()
    sentence=f'{lead} {p.lower() if p!="I" else p} {verb}'+(f' {noun}' if noun else '')+'?'
    rule=f'Dùng {aux} với {p.lower() if p!="I" else p}. He, she, it đi với does. I, you, we, they đi với do. Sau chủ ngữ, giữ nguyên {verb}.'
    if wh:rule='What nghĩa là “gì”. Đặt What ở đầu câu, rồi đến do hoặc does. '+rule
    return sentence,rule+f'\n{sentence}\n{vi}'
u=lessons['Unit 20']=Lesson('Do / Does + Like …?')
for i,p,verb,noun,vi,y,ans,yes,no,context in [
    (2,'You','have','flowers','Các bạn có hoa không?',1064,'Yes, we do.','Yes, we do.',"No, we don't.",'Hai bạn đang cầm hoa, nên dùng Yes.'),
    (3,'It','have','a baby','Nó có con không?',1191,"No, it doesn't.",'Yes, it does.',"No, it doesn't.",'Hình nét đứt cho biết con kangaroo không có con trong túi, nên dùng No.')
]:
    _,exp=do_question(p,verb,noun,vi)
    u.mark(f'A{i} khoanh',1,form(p,'do').capitalize(),exp,'circle',[('Do',[388,y-21,49,42]),('Does',[442,y-21,78,42])])
    u.mark(f'A{i} tích',1,ans,exp+' '+context+f' Đáp án ngắn là {ans}','tick',[
        (yes,[385,y+26,227,43],[385,y+26,40,43]),(no,[614,y+26,243,43],[614,y+26,40,43])])
for i,p,verb,noun,vi,answer_p,ending,y,yy,x in [
    (2,'He','have','a bat','Cậu ấy có gậy bóng chày không?','he',"doesn't",294,347,400),
    (3,'It','have','a nose','Nó có mũi không?','it',"doesn't",429,482,400),
    (4,'You','like','cookies','Bạn thích bánh quy không?','I','do',564,617,411),
    (5,'She','have','a hat','Cô bé có mũ không?','she',"doesn't",699,752,401)
]:
    _,exp=do_question(p,verb,noun,vi)
    reply='No' if ending=="doesn't" else 'Yes'
    parts(u,f'B{i}',2,[form(p,'do').capitalize(),answer_p,ending],slots((350,y,147),(x,yy,98),(x+106,yy,145)),
          [None]*3,exp+f'\n{reply}, {answer_p} {ending}. {('Hình cậu bé vui vẻ ăn bánh cho biết cậu thích bánh.' if reply=='Yes' else 'Hình nét đứt chỉ vật còn thiếu.')}')
for i,p,verb,noun,vi,reply,answer_p,ending,y in [
    (2,'You','like','oranges','Bạn thích cam không?','No',['I','we'],"don't",992),
    (3,'They','like','balloons','Họ thích bóng bay không?','Yes','they','do',1058),
    (4,'We','have','eggs','Chúng tôi có trứng không?','Yes','you','do',1125),
    (5,'It','have','a bone','Nó có khúc xương không?','No','it',"doesn't",1192),
    (6,'He','have','a skateboard','Cậu ấy có ván trượt không?','No','he',"doesn't",1259)
]:
    _,exp=do_question(p,verb,noun,vi)
    words=' hoặc '.join(answer_p) if isinstance(answer_p,list) else answer_p
    exp+=f'\nMặt cười báo câu trả lời Yes, mặt buồn báo câu trả lời No. Ở đây dùng {reply} với {words} {ending}.'
    parts(u,f'C{i}',2,[form(p,'do').capitalize(),reply,answer_p,ending],
          slots((126,y,99),(563,y,98),(675,y,98),(779,y,139)),[None]*4,exp)
for i,p,verb,noun,vi,y,tokens in [
    (2,'It','like','bananas','Nó có thích chuối không?',368,['like','Does','it','bananas?']),
    (3,'She','like','hot dogs','Cô bé có thích bánh mì xúc xích không?',502,['Does','like','she','hot dogs?']),
    (4,'They','have','lollipops','Họ có kẹo mút không?',637,['lollipops?','they','have','Do']),
    (5,'He','have','a cap','Cậu ấy có mũ lưỡi trai không?',772,['a cap?','have','Does','he'])
]:
    value,exp=do_question(p,verb,noun,vi)
    order(u,f'D{i}',3,value,exp,row(349,y,574,36),tokens)
for i,p,verb,noun,vi,y in [
    (2,'She','like','spiders','Cô ấy có thích nhện không?',988),
    (3,'You','like','blocks','Bạn có thích các khối đồ chơi không?',1055),
    (4,'It','have','a mouth','Nó có miệng không?',1122)
]:
    value,exp=do_question(p,verb,noun,vi)
    u.fill(f'E{i}',3,value,exp,row(493,y,440,36))
u.fill('E5',3,'Yes, he does.','He đi với does trong câu trả lời ngắn. Yes, he does nghĩa là “Vâng, cậu ấy có” hoặc “Vâng, cậu ấy thích”.',row(493,1189,440,36))
u.fill('E6',3,"No, I don't.",'I đi với do. Trong câu trả lời phủ định, dùng don’t. No, I don’t nghĩa là “Không, em không có” hoặc “Không, em không thích”.',row(493,1255,440,36))
u=lessons['Review 05']=Lesson('Units 17–21')
u.notes=['Trang in 75 ghi “Units 17–21” và phần D ôn mẫu What của Unit 21. Bài vẫn đứng sau Unit 20 theo thứ tự yêu cầu. Tiêu đề gốc được giữ trên ảnh, tiêu đề bài ghi theo PDF.']
for i,p,noun,vi,x,y,ox,oy in [
    (2,'She','grapes','Cô ấy thích nho.',630,297,659,312),(3,'You','donuts','Bạn thích bánh vòng.',181,405,211,421),
    (4,'He','hamburgers','Cậu ấy thích bánh hamburger.',617,405,648,423),
    (5,'It','fish','Nó thích cá.',151,514,181,529),(6,'They','cookies','Họ thích bánh quy.',641,516,670,533)
]:
    v,_,exp=verb_exp(p,'like',noun,vi)
    word_pair(u,f'A{i}',1,v,'likes' if v=='like' else 'like',exp,x,y,[('like',ox,35),('likes',ox+44,42)],oy,145)
for i,p,noun,vi,x,y in [
    (2,'He','a rabbit','Cậu ấy có một con thỏ.',161,1107),(3,'She','a cat','Cô ấy có một con mèo.',174,1177),
    (4,'They','frogs','Họ có những con ếch.',185,1247)
]:
    v,_,exp=verb_exp(p,'have',noun,vi)
    u.fill(f'B{i}',1,f'{v} {noun}',exp+' Ký hiệu O trong bảng cho biết người đó có con vật này.',row(x,y,719-x,36))
for i,p,verb,noun,vi,key,alts,x,y,oy in [
    (2,'You','like','cats','Bạn không thích mèo.',"don't",["isn't","don't","doesn't"],180,274,310),
    (3,'They','have','a car','Họ không có ô tô.',"don't have",["aren't have","don't have","don't has"],194,403,439),
    (4,'It','have','a ball','Nó không có bóng.',"doesn't have",["isn't have","don't have","doesn't have"],153,533,563)
]:
    _,_,exp=verb_exp(p,verb,noun,vi,True)
    u.mark(f'C{i} khoanh',2,key,exp,'circle',[(v,[dx-13,oy-21,216,42],[dx-13,oy-13,27,27]) for v,dx in zip(alts,[142,404,686])])
    u.fill(f'C{i} điền',2,key,exp,row(x,y,171 if i==2 else 191))
for i,p,verb,noun,vi,reply,x,y in [
    (2,'She','like','lollipops','Cô ấy thích gì? Cô ấy thích kẹo mút.','She',566,915),
    (3,'They','have','kites','Họ có gì? Họ có diều.','They',97,1206),
    (4,'He','like','bananas','Cậu ấy thích gì? Cậu ấy thích chuối.','He',568,1204)
]:
    q,exp=do_question(p,verb,'',vi,True)
    v,rep,_=verb_exp(reply,verb,noun,vi)
    parts(u,f'D{i}',2,['What',form(p,'do'),reply,v],
          columns([x,x+105],y)+columns([x,x+105],y+53),[None]*4,exp+'\n'+rep)


u=lessons['Unit 21']=Lesson('What + Do / Does + Like?')
u.links('A',1,{'They have pens.':[642,933],'It has a fish.':[642,1032],'He has a robot.':[642,1131]})
for i,p,noun,vi,y in [
    (2,'He','a robot','Cậu ấy có gì? Cậu ấy có một người máy.',1033),
    (3,'They','pens','Họ có gì? Họ có những chiếc bút mực.',1133),
    (4,'It','a fish','Nó có gì? Nó có một con cá.',1232)
]:
    _,exp=do_question(p,'have','',vi,True)
    _,reply,_=verb_exp(p,'have',noun,vi)
    u.match(f'A{i}',1,reply,exp+'\n'+reply+' Câu trả lời chỉ rõ món đồ và giữ đúng chủ ngữ.',[410,y],'A')
for i,p,noun,vi,y,x,w in [
    (2,'She','peaches','Cô ấy thích gì? Cô ấy thích đào.',493,590,331),
    (3,'It','bananas','Nó thích gì? Nó thích chuối.',560,495,355),
    (4,'They','oranges','Họ thích gì? Họ thích cam.',627,602,320)
]:
    _,exp=do_question(p,'like','',vi,True)
    v,reply,_=verb_exp(p,'like',noun,vi)
    parts(u,f'B{i}',2,['What',form(p,'do'),f'{v} {noun}'],
          slots((125,y,122),(255,y,121),(x,y+2,w)),[None]*3,exp+'\n'+reply+' Mặt cười trong bảng chỉ món được thích.')
for i,p,reply,noun,vi,y,yy,x,w in [
    (2,'It','It','a ball','Nó có gì? Nó có một quả bóng.',913,975,491,145),
    (3,'He','He','a bat','Cậu ấy có gì? Cậu ấy có một cây gậy bóng chày.',1046,1109,491,145),
    (4,'You','I','a bag','Bạn có gì? Em có một chiếc túi.',1181,1244,440,123)
]:
    _,exp=do_question(p,'have','',vi,True)
    v,reply_line,_=verb_exp(reply,'have',noun,vi)
    parts(u,f'C{i}',2,['What',form(p,'do'),reply,v],
          slots((338,y,145),(491,y,145),(338,yy,x-345),(x,yy,w)),[None]*4,exp+'\n'+reply_line)
for i,p,verb,vi,y,tokens in [
    (2,'She','have','Cô ấy có gì?',377,['What','have?','does','she']),
    (3,'It','like','Nó thích gì?',512,['like?','What','it','does']),
    (4,'They','have','Họ có gì?',647,['do','they','What','have?']),
    (5,'He','like','Cậu ấy thích gì?',782,['he','does','like?','What'])
]:
    value,exp=do_question(p,verb,'',vi,True)
    order(u,f'D{i}',3,value,exp,row(356,y,567,36),tokens)
for i,p,verb,vi,y in [
    (2,'We','have','Chúng ta có gì?',1000),(3,'You','like','Bạn thích gì?',1067),
    (4,'He','have','Cậu ấy có gì?',1134),(5,'It','have','Nó có gì?',1200),(6,'They','have','Họ có gì?',1267)
]:
    value,exp=do_question(p,verb,'',vi,True)
    u.fill(f'E{i}',3,value,exp,row(463,y,474,36))

can_choices=['can',"can't"]
def can_exp(p,key,verb,vi,context=''):
    opposite="can't" if key=='can' else 'can'
    meaning='có thể' if key=='can' else 'không thể'
    value=f'{p} {key} {verb}.'
    rule=f'{key} nghĩa là “{meaning}”. Đặt {key} trước động từ nguyên mẫu {verb}. Dùng {opposite} nếu khả năng ngược lại.'
    return value,context+(' ' if context else '')+rule+f'\n{value}\n{vi}'
def can_write(u,id,page,p,key,verb,vi,rect,tokens=None):
    value,exp=can_exp(p,key,verb,vi)
    if tokens:
        order(u,id,page,value,exp,rect,tokens)
    else:
        u.fill(id,page,value,exp,rect)
u=lessons['Unit 22']=Lesson('Can / Can’t')
u.notes=['Trang in 77, A3. Answer Key trang 98 ghi “It can run.”. Hình con rùa ở A3 cũng xuất hiện ở D4 (trang in 79), nơi bộ từ và key đều cho “It can’t run.”. Phần nối A3 vẫn chấm vì chỉ có một dòng “It … run”. Ô can/can’t ở A3 tạm không chấm.']
u.links('A',1,{'I … swim':[631,811],'You … swim':[629,1066],'It … run':[628,1193]})
for i,p,key,verb,target,vi,ly,x,y,context in [
    (2,'You',"can't",'swim','You … swim','Bạn không biết bơi.',936,699,1076,'Bạn nữ sợ xuống nước.'),
    (3,'It',None,'run','It … run','Con rùa trong hình.',1064,668,1204,'Hình bên trái là con rùa. Nối với câu về con vật bắt đầu bằng It.'),
    (4,'I','can','swim','I … swim','Em biết bơi.',1192,661,820,'Bạn trai đang bơi.')
]:
    exp=can_exp(p,key,verb,vi,context)[1] if key else context
    u.match(f'A{i} nối',1,target,exp,[328,ly],'A')
    if key:
        u.fill(f'A{i} điền',1,[key,'cannot'] if key=="can't" else key,exp,row(x,y,131))
for i,p,key,verb,vi,x,y,oy,context in [
    (2,'I',"can't",'write','Em không biết viết.',427,312,330,'Bạn nhỏ đang lúng túng trước trang giấy.'),
    (3,'It','can','climb','Con khỉ leo được.',728,311,329,'Con khỉ ở trên thân cây.'),
    (4,'They',"can't",'walk','Các em bé chưa biết đi.',162,567,585,'Hai em bé đang bò.'),
    (5,'You','can','jump','Bạn nhảy được.',445,566,584,'Bạn nhỏ nhảy qua rào.'),
    (6,'He',"can't",'skate','Cậu ấy không biết trượt băng.',737,564,582,'Cậu ấy bị ngã trên sân băng.')
]:
    _,exp=can_exp(p,key,verb,vi,context)
    u.mark(f'B{i} khoanh',2,key,exp,'circle',[('can',[x+3,oy-12,34,24]),("can't",[x+46,oy-12,53,24])])
    u.fill(f'B{i} điền',2,[key,'cannot'] if key=="can't" else key,exp,row(x,y,98))
for i,p,key,verb,vi,x1,x2,y,w in [
    (2,'It','can','swim','Con cá biết bơi.',584,689,1009,150),
    (3,'We','can','play basketball','Chúng em biết chơi bóng rổ.',140,245,1255,198),
    (4,'They',"can't",'ride a bike','Họ không biết đi xe đạp.',628,734,1252,200)
]:
    _,exp=can_exp(p,key,verb,vi)
    parts(u,f'C{i}',2,[[key,'cannot'] if key=="can't" else key,verb],slots((x1,y,98),(x2,y,w)),[None,None],exp)
for i,p,key,verb,vi,y,tokens in [
    (2,'I','can','ski','Em biết trượt tuyết.',372,['ski.','I','can']),
    (3,'She',"can't",'play the violin','Cô ấy không biết chơi đàn vĩ cầm.',507,['She','play the violin.',"can't"]),
    (4,'It',"can't",'run','Nó không chạy được.',642,['run.',"can't",'It']),
    (5,'We','can','ride a bike','Chúng em biết đi xe đạp.',776,['can','We','ride a bike.'])
]:
    can_write(u,f'D{i}',3,p,key,verb,vi,row(355,y,550,36),tokens)
for i,p,key,verb,vi,y in [
    (2,'She','can','play the piano','Cô ấy biết chơi đàn dương cầm.',992),
    (3,'I',"can't",'cook','Em không biết nấu ăn.',1059),(4,'He',"can't",'ride a bike','Cậu ấy không biết đi xe đạp.',1126),
    (5,'It',"can't",'jump','Nó không nhảy được.',1192),(6,'You',"can't",'play soccer','Bạn không biết chơi bóng đá.',1259)
]:
    can_write(u,f'E{i}',3,p,key,verb,vi,row(504,y,410,36))


def can_question(p,verb,vi):
    value=f'Can {p if p=="I" else p.lower()} {verb}?'
    exp=f'Đưa Can lên đầu câu để hỏi “có thể … không?”. Sau chủ ngữ, dùng động từ nguyên mẫu {verb}.\n{value}\n{vi}'
    return value,exp
u=lessons['Unit 23']=Lesson('Can …?')
u.links('A',1,{'Yes, they can.':[706,1020],"No, I can't.":[707,1126]})
for i,p,verb,vi,reply,y,ly,translation in [
    (2,'You','skate','Bạn biết trượt băng không?', "No, I can't.",1145,1128,'Không, mình không biết.'),
    (3,'They','play baseball','Họ biết chơi bóng chày không?','Yes, they can.',1252,1234,'Có, họ biết chơi.')
]:
    _,exp=can_question(p,verb,vi)
    u.fill(f'A{i} điền',1,'Can',exp,row(131,y,97))
    u.match(f'A{i} nối',1,reply,exp+f'\n{reply}\n{translation}',[496,ly],'A')
for i,p,verb,vi,ans,ending,y,yy,x2,x3,reply in [
    (2,'He','fly a kite','Cậu ấy biết thả diều không?','he',"can't",411,468,511,402,'No'),
    (3,'It','jump','Nó có nhảy được không?','it','can',561,618,494,412,'Yes'),
    (4,'They','play tennis','Họ biết chơi quần vợt không?','they',"can't",710,767,530,400,'No')
]:
    _,exp=can_question(p,verb,vi)
    exp+=f'\n{reply}, {ans} {ending}. Sau Yes, dùng can. Sau No, dùng can’t.'
    parts(u,f'B{i}',2,['Can',verb,ans,[ending,'cannot'] if ending=="can't" else ending],
          slots((353,y,112),(x2,y,193),(x3,yy,98),(x3+106,yy,145)),[None]*4,exp)
for i,p,verb,vi,y in [
    (2,'You','ride a horse','Bạn biết cưỡi ngựa không?',985),(3,'She','play the guitar','Cô ấy biết chơi đàn ghi-ta không?',1052),
    (4,'They','skate','Họ biết trượt băng không?',1118),(5,'It','fly','Nó có bay được không?',1185),(6,'We','paint','Chúng ta biết vẽ không?',1252)
]:
    value,exp=can_question(p,verb,vi)
    u.fill(f'C{i}',2,value,exp,row(475,y,435,36))
for i,p,verb,vi,y,tokens in [
    (2,'You','play baseball','Bạn biết chơi bóng chày không?',370,['play baseball?','you','Can']),
    (3,'She','skate','Cô ấy biết trượt băng không?',505,['Can','skate?','she']),
    (4,'They','walk','Các em bé biết đi chưa?',641,['they','walk?','Can']),
    (5,'It','run','Nó có chạy được không?',776,['run?','Can','it'])
]:
    value,exp=can_question(p,verb,vi)
    order(u,f'D{i}',3,value,exp,row(354,y,565,36),tokens)
for i,p,verb,vi,y in [
    (2,'It','climb','Nó có leo được không?',993),(3,'She','write','Cô bé biết viết không?',1060),
    (4,'We','ride a horse','Chúng ta có cưỡi ngựa được không?',1127)
]:
    value,exp=can_question(p,verb,vi)
    u.fill(f'E{i}',3,value,exp,row(466,y,469,36))
u.fill('E5',3,'Yes, they can.','Sau Yes, dùng can. “Yes, they can” nghĩa là “Vâng, họ làm được”.',row(468,1194,467,36))
u.fill('E6',3,"No, he can't.",'Sau No, dùng can’t. “No, he can’t” nghĩa là “Không, cậu ấy không làm được”.',row(468,1261,467,36))

def weather_exp(noun,vi,question=None):
    lead='Dùng It is khi nói về giờ, thời tiết hoặc mùa. It chỉ giúp câu có chủ ngữ.'
    if question:
        positive,context=question
        reply='Yes, it is.' if positive else "No, it isn't."
        return lead+f' Đưa is lên trước it để hỏi.\nIs it {noun}? {reply}\n{vi} {context}'
    return lead+f'\nIt is {noun}.\n{vi}'
u=lessons['Unit 24']=Lesson('It Is + Time / Weather / Season')
u.notes=['Trang in 83, A2. Dòng “__ __ is five o’clock” in sẵn “is” dư so với Answer Key trang 99 là “It is five o’clock.”. Phần nối hình đồng hồ vẫn chấm. Hai ô điền của dòng này tạm không chấm.']
u.links('A',1,{"five o'clock":[585,1187],'winter':[587,743],'rainy':[585,1039]})
for i,noun,vi,ly,x,y,context in [
    (2,"five o'clock",'Bây giờ là năm giờ.',891,606,1179,'Kim phút chỉ 12 và kim giờ chỉ 5.'),
    (3,'winter','Bây giờ là mùa đông.',1038,606,754,'Các bạn mặc áo ấm và chơi với tuyết.'),
    (4,'rainy','Trời mưa.',1187,604,1053,'Hình có các vệt mưa.')
]:
    exp=weather_exp(noun,vi)+' '+context
    u.match(f'A{i} nối',1,noun,exp,[334,ly],'A')
    if i!=2:
        parts(u,f'A{i}',1,['It','is'],slots((x,y,74),(x+81,y,49)),[None]*2,exp)
for i,noun,vi,x,y in [
    (2,"seven o'clock",'Bây giờ là bảy giờ.',370,338),(3,'fall','Bây giờ là mùa thu.',714,334),
    (4,'cloudy','Trời nhiều mây.',112,595),(5,"twelve o'clock",'Bây giờ là mười hai giờ.',359,593),
    (6,'spring','Bây giờ là mùa xuân.',694,591)
]:
    parts(u,f'B{i}',2,['It','is'],slots((x,y,49),(x+56,y,49)),[None]*2,weather_exp(noun,vi))
for i,noun,vi,x,y,xx,yy,positive,context in [
    (2,'summer','Có phải mùa hè không?',388,919,446,968,True,'Đúng, các bạn đang chơi trên bãi biển vào mùa hè.'),
    (3,"ten o'clock",'Có phải mười giờ không?',671,911,732,960,True,'Đúng, kim giờ chỉ 10.'),
    (4,'rainy','Trời có mưa không?',94,1218,143,1267,False,'Không, trời nắng.'),
    (5,'fall','Có phải mùa thu không?',388,1216,438,1266,False,'Không, hình có tuyết vào mùa đông.'),
    (6,"twelve o'clock",'Có phải mười hai giờ không?',672,1215,722,1264,False,'Không, kim giờ chỉ 1.')
]:
    exp=weather_exp(noun,vi,(positive,context))
    parts(u,f'C{i}',2,['Is','it','it','is' if positive else ["isn't","is not"]],
          slots((x,y,49),(x+56,y,49),(xx,yy,49),(xx+57,yy,74)),[None]*4,exp)
for i,noun,vi,y,tokens in [
    (2,'spring','Bây giờ là mùa xuân.',368,['spring.','It','is']),
    (3,"five o'clock",'Bây giờ là năm giờ.',503,['It',"five o'clock.",'is']),
    (4,'sunny','Trời nắng.',638,['is','It','sunny.']),
    (5,'fall','Bây giờ là mùa thu.',773,['fall.','is','It'])
]:
    order(u,f'D{i}',3,f'It is {noun}.',weather_exp(noun,vi),row(354,y,550,36),tokens)
for i,noun,vi,y in [
    (2,'snowy','Trời có tuyết.',990),(3,"six o'clock",'Bây giờ là sáu giờ.',1057),
    (4,'winter','Bây giờ là mùa đông.',1124),(5,"eleven o'clock",'Bây giờ là mười một giờ.',1191),
    (6,'spring','Bây giờ là mùa xuân.',1258)
]:
    value=f'It is {noun}.'
    exp=weather_exp(noun,vi)+' Trật tự câu kể là It + is, rồi đến từ chỉ giờ, thời tiết hoặc mùa.'
    u.fill(f'E{i}',3,value,exp,row(434,y,476,36))

u=lessons['Review 06']=Lesson('Units 22–24')
u.notes=['Trang in 86 ghi “Units 22–24”. Bài vẫn đứng sau Unit 24 theo thứ tự yêu cầu, trong nhóm Unit 21–24. Tiêu đề bài ghi theo PDF.']
for i,p,key,verb,vi,x,y,w in [
    (2,'It','can','swim','Con cá biết bơi.',584,512,170),(3,'You',"can't",'read','Các bạn chưa biết đọc.',143,704,170),
    (4,'She',"can't",'play the violin','Cô ấy chưa biết chơi đàn vĩ cầm.',618,700,186),
    (5,'I','can','ski','Em biết trượt tuyết.',105,895,170),(6,'They','can','fly','Những con bướm biết bay.',630,888,173)
]:
    _,exp=can_exp(p,key,verb,vi)
    parts(u,f'A{i}',1,[[key,'cannot'] if key=="can't" else key,verb],
          slots((x,y,97),(x+105,y,w)),[None,None],exp)
u.links('B',1,{'Yes, they can.':[688,1008],"No, I can't.":[690,1159],"No, it can't.":[691,1233]})
for i,p,verb,vi,reply,tr,y,ly in [
    (2,'You','play the flute','Bạn biết thổi sáo không?', "No, I can't.",'Không, mình không biết.',1101,1085),
    (3,'It','climb','Nó có leo được không?', "No, it can't.",'Không, nó không leo được.',1175,1160),
    (4,'They','play soccer','Họ biết chơi bóng đá không?','Yes, they can.','Có, họ biết chơi.',1251,1235)
]:
    _,exp=can_question(p,verb,vi)
    u.fill(f'B{i} điền',1,'Can',exp,row(132,y,97))
    u.match(f'B{i} nối',1,reply,exp+f'\n{reply}\n{tr}',[487,ly],'B')
for i,noun,vi,x,y,w in [
    (2,"ten o'clock",'Bây giờ là mười giờ.',557,412,181),(3,'summer','Bây giờ là mùa hè.',92,642,145),
    (4,'windy','Trời có gió.',556,644,148)
]:
    parts(u,f'C{i}',2,['It','is',noun],slots((x,y,74),(x+80,y,98),(x+186,y,w)),[None]*3,weather_exp(noun,vi))
for i,key,alts,x,y,oy,w,exp in [
    (2,"can't ride",['can rides','rides can',"can't ride"],179,894,926,195,can_exp('She',"can't",'ride a horse','Cô ấy không biết cưỡi ngựa.')[1]),
    (3,'Can',['Can','Does','Are'],127,999,1033,146,can_question('They','dance','Họ biết nhảy múa không?')[1]),
    (4,'It',['This','It','That'],126,1106,1135,147,weather_exp('sunny','Trời nắng.')),
    (5,'It, winter',['It, a winter','It, winter','Those, winter'],126,1212,1246,146,weather_exp('winter','Bây giờ là mùa đông.'))
]:
    u.mark(f'D{i} khoanh',2,key,exp,'circle',[(v,[dx-13,oy-21,220,42],[dx-13,oy-13,27,27]) for v,dx in zip(alts,[139,403,665])])
    if i==5:
        parts(u,'D5',2,['It','winter'],slots((x,y,w),(306,y,145)),[None,None],exp)
    else:
        u.fill(f'D{i} điền',2,key,exp,row(x,y,w))



lessons['Unit 15'].review_slots.append({'id':'E4','page':2,'rect':row(538,1126,397,36),
    'note':'Giáo viên cần xác nhận câu E4 vì Answer Key thiếu dòng đáp án tương ứng.'})
lessons['Unit 19'].review_slots.append({'id':'C2','page':1,'rect':row(159,1047,579,37),
    'note':'Giáo viên cần đối chiếu hai từ watermelons và cucumbers trong đề và đáp án.'})
lessons['Unit 22'].review_slots.append({'id':'A3 điền','page':0,'rect':row(668,1204,131),
    'note':'Giáo viên cần đối chiếu nội dung A3 và D4 trước khi chấm phần can/can’t.'})
for i,rect in enumerate(slots((604,1179,74),(686,1179,49)),1):
    lessons['Unit 24'].review_slots.append({'id':f'A2.{i}','page':0,'rect':rect,
        'note':'Giáo viên cần xác nhận cách làm vì đề in thêm is sau hai ô trống.'})
