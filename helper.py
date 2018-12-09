import dbconnector as db

element_len = {
	'id': 72,
	'req_by': 57,
	'section': 24,
	'department_head': 27,
	'location': 23,
	'description_of_service_as': 180
}

# Checks if the given MSO is approved by both TSM and TSS.
def can_edit(id):
    return (db.get_mso(id)['tsm_approval']) == 1 and (db.get_mso(id)['supervisor_approval'] == 1)

# Check if current user is authorized to delete the given MSO
def can_delete(id, session):
	user_info = db.get_user_by_email(session['email'])
	current_user = user_info['first_name'] + ' ' + user_info['last_name']
	approval = (db.get_mso(id)['tsm_approval']) == None and (db.get_mso(id)['supervisor_approval'] == None)
	return((current_user == db.get_mso(id)['posted_by']) and approval)

def a4_len_calc(element, value):
	try:
		return value +  (element_len[element] - len(value))*' '
	except:
		return str(value) +  (element_len[element] - len(str(value)))*' '

def a4_formatter(id):
	mso_formatted = {}
	mso = db.get_mso(id)

	mso_formatted['id'] = 'CNS-' + a4_len_calc('id', mso['id'])
	mso_formatted['mso_req_date'] = str(mso['posted_on']).replace(' ',',').split(',')[0]
	mso_formatted['mso_req_time'] = str(mso['posted_on']).replace(' ',',').split(',')[1]
	mso_formatted['requested_by'] = a4_len_calc('req_by', mso['requested_by'])
	mso_formatted['section'] = a4_len_calc('section', mso['section'])
	mso_formatted['department_head'] = a4_len_calc('department_head', mso['department_head'])
	mso_formatted['location'] = a4_len_calc('location', mso['location'])
	#mso_formatted['description_of_service'] = a4_len_calc('description_of_service', mso['description_of_service'])


	return mso_formatted

def dos_awd_parser(t=''):
	try:
		if len(t) <= 512:
			t += " "*(512-len(t))
		else:
			t = t[:512] + '...'
		
		l1 = t[0:61].upper()
		l2 = t[61:152].upper()
		l3 = t[152:243].upper()
		l4 = t[243:334].upper()
		l5 = t[334:425].upper()
		l6 = t[425:516].upper()
	except:
		return {'l1':'', 'l2':'', 'l3':'', 'l4':'', 'l5':'', 'l6':''}
	return {'l1':l1, 'l2':l2, 'l3':l3, 'l4':l4, 'l5':l5, 'l6':l6}

# Returns Airport id number of wcbb(work compleated by name)
def wcb_id(wcbn):
	print(wcb)
# t = dos_awd_parser("Affronting imprudence do he he everything. Sex lasted dinner wanted indeed imprudence do he he everything. Sex lasted dinner wanted indeed imprudence do he he everything. Sex lasted dinner wanted indeed imprudence do he he everything. Sex lasted dinner wanted indeed imprudence do he he everything. Sex lasted dinner wanted indeed wished out law. Far advanced settling say finished raillery. Offered chiefly farther of my no colonel shyness. Such on help ye some door if in. Laughter proposal laughing any son law consider. Needed except up piqued an. Woody equal ask saw sir weeks aware decay. Entrance prospect removing we packages strictly is no smallest he. For hopes may chief get hours day rooms. Oh no turned behind polite piqued enough at. Forbade few through inquiry blushes you. Cousin no itself eldest it in dinner latter missed no. Boisterous estimating interested collecting get conviction friendship say boy. Him mrs shy article smiling respect opinion excited. Welcomed humoured rejoiced peculiar to in an. Imagine was you removal raising gravity. Unsatiable understood or expression dissimilar so sufficient. Its party every heard and event gay. Advice he indeed things adieus in number so uneasy. To many four fact in he fail. My hung it quit next do of. It fifteen charmed by private savings it mr. Favourable cultivated alteration entreaties yet met sympathize. Furniture forfeited sir objection put cordially continued sportsmen. Ever man are put down his very. And marry may table him avoid. Hard sell it were into it upon. He forbade affixed parties of assured to me windows. Happiness him nor she disposing provision. Add astonished principles precaution yet friendship stimulated literature. State thing might stand one his plate. Offending or extremity therefore so difficult he on provision. Tended depart turned not are. Old unsatiable our now but considered travelling impression. In excuse hardly summer in basket misery. By rent an part need. At wrong of of water those linen. Needed oppose seemed how all. Very mrs shed shew gave you. Oh shutters do removing reserved wandered an. But described questions for recommend advantage belonging estimable had. Pianoforte reasonable as so am inhabiting. Chatty design remark and his abroad figure but its. Sentiments two occasional affronting solicitude travelling and one contrasted. Fortune day out married parties. Happiness remainder joy but earnestly for off. Took sold add play may none him few. If as increasing contrasted entreaties be. Now summer who day looked our behind moment coming. Pain son rose more park way that. An stairs as be lovers uneasy. Had strictly mrs handsome mistaken cheerful. We it so if resolution invitation remarkably unpleasant conviction. As into ye then form. To easy five less if rose were. Now set offended own out required entirely. Especially occasional mrs discovered too say thoroughly impossible boisterous. My head when real no he high rich at with. After so power of young as. Bore year does has get long fat cold saw neat. Put boy carried chiefly shy general. Whole wound wrote at whose to style in. Figure ye innate former do so we. Shutters but sir yourself provided you required his. So neither related he am do believe. Nothing but you hundred had use regular. Fat sportsmen arranging preferred can. Busy paid like is oh. Dinner our ask talent her age hardly. Neglected collected an attention listening do abilities. Is he staying arrival address earnest. To preference considered it the")
# print(t['l1'])
# print(t['l2'])
# print(t['l3'])
# print(t['l4'])
# print(t['l5'])
# print(t['l6'])